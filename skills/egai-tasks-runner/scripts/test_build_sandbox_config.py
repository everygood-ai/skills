from __future__ import annotations

import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path


BUILD_SANDBOX_CONFIG = Path(__file__).resolve().parent / "build-sandbox-config.py"
BASELINE_PATH = Path(__file__).resolve().parent.parent / "assets" / "srt-settings.baseline.json"


def load_baseline() -> dict[str, object]:
    with BASELINE_PATH.open(encoding="utf-8") as baseline_file:
        return json.load(baseline_file)


def load_module():
    spec = importlib.util.spec_from_file_location("build_sandbox_config", BUILD_SANDBOX_CONFIG)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BuildSandboxConfigTests(unittest.TestCase):
    def run_build(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(BUILD_SANDBOX_CONFIG), *args],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )

    def test_copies_baseline_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            project_root = Path(root)

            result = self.run_build(str(project_root))

            self.assertEqual(result.returncode, 0, result.stderr)
            output_path = project_root / ".srt-settings.generated.json"
            self.assertEqual(result.stdout.strip(), str(output_path))

            written = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(written, load_baseline())

    def test_manifests_are_not_inspected(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            project_root = Path(root)
            (project_root / "package.json").write_text("{}\n", encoding="utf-8")
            (project_root / "requirements.txt").write_text("", encoding="utf-8")
            (project_root / "Cargo.toml").write_text("", encoding="utf-8")
            (project_root / "go.mod").write_text("", encoding="utf-8")

            result = self.run_build(str(project_root))

            self.assertEqual(result.returncode, 0, result.stderr)
            written = json.loads((project_root / ".srt-settings.generated.json").read_text(encoding="utf-8"))
            self.assertEqual(written, load_baseline())
            self.assertNotIn("registry.npmjs.org", written["network"]["allowedDomains"])

    def test_defaults_to_cwd_when_no_argument_given(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            project_root = Path(root)

            result = subprocess.run(
                [sys.executable, str(BUILD_SANDBOX_CONFIG)],
                check=False,
                capture_output=True,
                text=True,
                timeout=5,
                cwd=str(project_root),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            output_path = project_root / ".srt-settings.generated.json"
            self.assertTrue(output_path.is_file())
            self.assertEqual(Path(result.stdout.strip()).resolve(), output_path.resolve())

    def test_missing_baseline_file_is_a_clear_error(self) -> None:
        module = load_module()
        module.BASELINE_PATH = module.BASELINE_PATH.parent / "does-not-exist.json"

        with tempfile.TemporaryDirectory() as root:
            argv = ["build-sandbox-config.py", root]
            original_argv = sys.argv
            sys.argv = argv
            stdout = io.StringIO()
            stderr = io.StringIO()
            try:
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    exit_code = module.main()
            finally:
                sys.argv = original_argv

            self.assertNotEqual(exit_code, 0)
            self.assertIn("baseline settings file not found", stderr.getvalue())
            self.assertFalse((Path(root) / ".srt-settings.generated.json").exists())


if __name__ == "__main__":
    unittest.main()
