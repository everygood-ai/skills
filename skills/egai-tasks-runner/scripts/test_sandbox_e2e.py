"""End-to-end checks for Sandbox Mode against the real `srt` binary.

Unlike test_build_sandbox_config.py (pure logic, no external dependencies),
this suite actually shells out to `srt` and, for two tests, the network. It
exists to catch cases where our JSON is well-formed but `srt` doesn't enforce
it the way we assume — for example, on macOS `/tmp` is a symlink to
`/private/tmp`, and `srt` needs the resolved path in `allowWrite`, not the
symlink, or writes there are silently denied despite `/tmp` being listed.

Skips entirely if `srt` isn't resolvable (see resolve_srt_command). Set
SRT_TEST_CMD to point at an alternate invocation, e.g. for a local checkout:
    SRT_TEST_CMD="npx --yes @anthropic-ai/sandbox-runtime@latest" pytest ...

Does NOT cover `gh` auth (Keychain vs GH_TOKEN) or SSH remotes — those need
real credentials and a real remote, and stay manual per references/sandbox-mode.md.
"""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path


BUILD_SANDBOX_CONFIG = Path(__file__).resolve().parent / "build-sandbox-config.py"
SRT_RUN_TIMEOUT = 20
NETWORK_PRECHECK_TIMEOUT = 5


def resolve_srt_command() -> list[str] | None:
    if shutil.which("srt"):
        return ["srt"]
    override = os.environ.get("SRT_TEST_CMD")
    if override:
        return shlex.split(override)
    return None


def host_is_reachable(url: str) -> bool:
    try:
        result = subprocess.run(
            ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}", "--max-time", str(NETWORK_PRECHECK_TIMEOUT), url],
            capture_output=True,
            text=True,
            timeout=NETWORK_PRECHECK_TIMEOUT + 2,
        )
        return result.stdout.strip().startswith(("2", "3"))
    except (OSError, subprocess.TimeoutExpired):
        return False


class SandboxE2ETests(unittest.TestCase):
    srt_cmd: list[str]
    project_root: Path
    outside_root: Path
    generated_config: Path

    @classmethod
    def setUpClass(cls) -> None:
        srt_cmd = resolve_srt_command()
        if srt_cmd is None:
            raise unittest.SkipTest(
                "srt not found on PATH and SRT_TEST_CMD not set — "
                "install it (see install.sh) or set SRT_TEST_CMD to run this suite"
            )
        cls.srt_cmd = srt_cmd

        cls.project_root = Path(tempfile.mkdtemp(prefix="srt-e2e-project-"))
        (cls.project_root / ".claude").mkdir()
        (cls.project_root / ".agents").mkdir()
        cls.outside_root = Path(tempfile.mkdtemp(prefix="srt-e2e-outside-"))

        build = subprocess.run(
            [sys.executable, str(BUILD_SANDBOX_CONFIG), str(cls.project_root)],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
        cls.generated_config = Path(build.stdout.strip())

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.project_root, ignore_errors=True)
        shutil.rmtree(cls.outside_root, ignore_errors=True)

    def run_in_sandbox(self, command: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [*self.srt_cmd, "--settings", str(self.generated_config), "-c", command],
            cwd=str(self.project_root),
            capture_output=True,
            text=True,
            timeout=SRT_RUN_TIMEOUT,
        )

    def test_generated_config_is_accepted(self) -> None:
        result = self.run_in_sandbox("echo sandbox-basics-ok")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("sandbox-basics-ok", result.stdout)

    def test_write_inside_project_root_succeeds(self) -> None:
        marker = f"root-{uuid.uuid4().hex}.txt"
        result = self.run_in_sandbox(f"echo ok > ./{marker} && cat ./{marker}")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.project_root / marker).is_file())

    def test_write_under_tmp_succeeds(self) -> None:
        marker = f"/tmp/srt-e2e-{uuid.uuid4().hex}.txt"
        try:
            result = self.run_in_sandbox(f"echo ok > {marker} && cat {marker}")
            self.assertEqual(result.returncode, 0, result.stderr)
        finally:
            Path(marker).unlink(missing_ok=True)

    def test_write_under_private_tmp_succeeds(self) -> None:
        marker = f"/private/tmp/srt-e2e-{uuid.uuid4().hex}.txt"
        try:
            result = self.run_in_sandbox(f"echo ok > {marker} && cat {marker}")
            self.assertEqual(result.returncode, 0, result.stderr)
        finally:
            Path(marker).unlink(missing_ok=True)

    def test_stacked_phase_mode_worktree_path_succeeds(self) -> None:
        branch_dir = f"/tmp/egai-worktrees/e2e-{uuid.uuid4().hex}"
        try:
            result = self.run_in_sandbox(f"mkdir -p {branch_dir} && echo ok > {branch_dir}/f.txt && cat {branch_dir}/f.txt")
            self.assertEqual(result.returncode, 0, result.stderr)
        finally:
            shutil.rmtree(branch_dir, ignore_errors=True)

    def test_write_to_claude_dir_is_denied(self) -> None:
        result = self.run_in_sandbox("echo blocked > ./.claude/e2e-test.txt")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.project_root / ".claude" / "e2e-test.txt").exists())

    def test_write_to_agents_dir_is_denied(self) -> None:
        result = self.run_in_sandbox("echo blocked > ./.agents/e2e-test.txt")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.project_root / ".agents" / "e2e-test.txt").exists())

    def test_write_outside_allowlist_is_denied(self) -> None:
        target = self.outside_root / "e2e-test.txt"
        result = self.run_in_sandbox(f"echo blocked > {target}")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(target.exists())

    def test_allowed_domain_is_reachable(self) -> None:
        if not host_is_reachable("https://github.com"):
            self.skipTest("github.com not reachable outside the sandbox in this environment")
        result = self.run_in_sandbox('curl -sS -o /dev/null -w "%{http_code}" --max-time 10 https://github.com')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.strip().startswith(("2", "3")), result.stdout)

    def test_non_allowed_domain_is_blocked(self) -> None:
        if not host_is_reachable("https://example.com"):
            self.skipTest("example.com not reachable outside the sandbox in this environment")
        result = self.run_in_sandbox('curl -sS -o /dev/null -w "%{http_code}" --max-time 10 https://example.com')
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
