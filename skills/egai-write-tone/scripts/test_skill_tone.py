from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
LINT_SCRIPT = SCRIPTS_DIR / "lint.sh"
SKILLS_DIR = SCRIPTS_DIR.parent.parent
SKILL_FILES = sorted(SKILLS_DIR.glob("*/SKILL.md"))
REPO_ROOT = SKILLS_DIR.parent
TONE_MANIFEST_PATH = REPO_ROOT / "tone-contracts.json"
CONTRACTS_DIR = SCRIPTS_DIR.parent / "references" / "contracts"
KERNEL_V1 = CONTRACTS_DIR / "kernel" / "v1.md"
PROFILE_V1_FILES = {
    "prose": CONTRACTS_DIR / "prose" / "v1.md",
    "terse": CONTRACTS_DIR / "terse" / "v1.md",
    "compact": CONTRACTS_DIR / "compact" / "v1.md",
}
TERSE_REPORT_V1 = CONTRACTS_DIR / "terse-report" / "v1.md"
SKILL_MD = SCRIPTS_DIR.parent / "SKILL.md"
STANDALONE_WORKFLOW = SCRIPTS_DIR.parent / "references" / "standalone-workflow.md"
DELETED_REFERENCE_FILES = (
    SCRIPTS_DIR.parent / "references" / "prose.md",
    SCRIPTS_DIR.parent / "references" / "terse.md",
    SCRIPTS_DIR.parent / "references" / "compact.md",
)
MARKDOWN_LINK_RE = re.compile(r"\]\(([^)]+)\)")

VALE_INSTALLED = shutil.which("vale") is not None


def _load_tone_manifest() -> dict:
    if not TONE_MANIFEST_PATH.is_file():
        return {}
    return json.loads(TONE_MANIFEST_PATH.read_text(encoding="utf-8"))


def _without_compiled_tone_sections(skill_file: Path, content: str) -> str:
    """Cut each compiled tone-contract section's exact pinned text out of `content`.

    A compiled section (see compile-tone-contracts.py) is a verbatim, pinned
    profile — its own author already targets prose, terse, or compact rules
    for that section alone, not for the whole `SKILL.md`. Removing the exact
    contract text (its heading survives) keeps this test checking only the
    hand-authored prose around it.
    """
    consumer_key = str(skill_file.relative_to(REPO_ROOT))
    for entry in _load_tone_manifest().get(consumer_key, []):
        contract_path = (
            SCRIPTS_DIR.parent
            / "references"
            / "contracts"
            / entry["profile"]
            / f"v{entry['revision']}.md"
        )
        if contract_path.is_file():
            content = content.replace(contract_path.read_text(encoding="utf-8"), "")
    return content


class SkillToneTests(unittest.TestCase):
    @unittest.skipUnless(VALE_INSTALLED, "vale is not installed; run install.sh, then rerun tests")
    def test_every_skill_file_passes_prose_tone_lint(self) -> None:
        self.assertTrue(SKILL_FILES, "No SKILL.md files found under skills/.")
        for skill_file in SKILL_FILES:
            with self.subTest(skill=str(skill_file.relative_to(SKILLS_DIR))):
                content = _without_compiled_tone_sections(
                    skill_file, skill_file.read_text(encoding="utf-8")
                )
                with tempfile.NamedTemporaryFile(
                    "w", suffix=".md", delete=False, encoding="utf-8"
                ) as handle:
                    handle.write(content)
                    scratch_path = Path(handle.name)
                try:
                    result = subprocess.run(
                        [str(LINT_SCRIPT), "prose", str(scratch_path)],
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                finally:
                    scratch_path.unlink(missing_ok=True)
                self.assertEqual(
                    result.returncode,
                    0,
                    f"egai-write-tone prose-mode lint failed for {skill_file}:\n"
                    f"{result.stdout}{result.stderr}",
                )

    def test_kernel_v1_exists_and_stays_under_word_budget(self) -> None:
        self.assertTrue(KERNEL_V1.is_file(), f"{KERNEL_V1} does not exist.")
        content = KERNEL_V1.read_text(encoding="utf-8")
        self.assertTrue(content.strip(), f"{KERNEL_V1} is empty.")
        word_count = len(content.split())
        self.assertLessEqual(
            word_count,
            100,
            f"{KERNEL_V1} has {word_count} words; kernel must stay at or under 100.",
        )

    def test_profile_v1_files_exist_and_stay_within_word_budget(self) -> None:
        for profile, path in PROFILE_V1_FILES.items():
            with self.subTest(profile=profile):
                self.assertTrue(path.is_file(), f"{path} does not exist.")
                content = path.read_text(encoding="utf-8")
                self.assertTrue(content.strip(), f"{path} is empty.")
                word_count = len(content.split())
                self.assertTrue(
                    75 <= word_count <= 120,
                    f"{path} has {word_count} words; profiles must stay within 75-120.",
                )

    def test_terse_report_v1_exists_and_is_shorter_than_terse(self) -> None:
        self.assertTrue(TERSE_REPORT_V1.is_file(), f"{TERSE_REPORT_V1} does not exist.")
        terse_report_content = TERSE_REPORT_V1.read_text(encoding="utf-8")
        self.assertTrue(terse_report_content.strip(), f"{TERSE_REPORT_V1} is empty.")
        terse_path = PROFILE_V1_FILES["terse"]
        terse_content = terse_path.read_text(encoding="utf-8")
        terse_report_word_count = len(terse_report_content.split())
        terse_word_count = len(terse_content.split())
        self.assertLess(
            terse_report_word_count,
            terse_word_count,
            f"{TERSE_REPORT_V1} has {terse_report_word_count} words; "
            f"must be lower than {terse_path}'s {terse_word_count} words.",
        )

    def test_standalone_workflow_references_kernel_and_all_profiles(self) -> None:
        self.assertTrue(
            STANDALONE_WORKFLOW.is_file(), f"{STANDALONE_WORKFLOW} does not exist."
        )
        content = STANDALONE_WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "references/contracts/kernel/v1.md",
            content,
            f"{STANDALONE_WORKFLOW} does not reference references/contracts/kernel/v1.md.",
        )
        for profile in ("prose", "terse", "compact"):
            relative_path = f"references/contracts/{profile}/v1.md"
            with self.subTest(profile=profile):
                self.assertIn(
                    relative_path,
                    content,
                    f"{STANDALONE_WORKFLOW} does not reference {relative_path}.",
                )

    @unittest.skipUnless(VALE_INSTALLED, "vale is not installed; run install.sh, then rerun tests")
    def test_representative_mode_samples_pass_lint_end_to_end(self) -> None:
        """Exercise each mode's full lint config on a mode-shaped sample.

        A mode-correct sample (drafted per that mode's own profile shape)
        must lint clean, and the same sample with a Latin abbreviation added
        must trip `EGAICommon.LatinAbbreviations`. The second half of each
        case pins the shared error-level rule to every mode's config, so a
        future edit that detaches a mode's `.vale.ini` from `EGAICommon`
        fails this test instead of silently passing everything through.
        """
        cases = {
            "prose": (
                "The retry policy retries a failed request up to three "
                "times. It waits one second between each attempt. It gives "
                "up once every attempt fails.",
                "The retry policy retries a failed request up to three "
                "times, e.g. after a timeout.",
            ),
            "terse": (
                "1. Retry a failed request up to three times.\n"
                "2. Wait one second between attempts.\n"
                "3. Give up once all three attempts fail.",
                "Retry a failed request up to three times, e.g. after a "
                "timeout.",
            ),
            "compact": (
                "Retries: 3 max.\nWait: 1s between attempts.\nThen: give up.",
                "Retries: 3 max, e.g. after a timeout.",
            ),
        }
        for mode, (good_text, bad_text) in cases.items():
            with self.subTest(mode=mode, sample="mode-correct"):
                self.assertEqual(
                    self._lint_text(mode, good_text),
                    0,
                    f"A mode-correct {mode} sample should lint clean under {mode} mode.",
                )
            with self.subTest(mode=mode, sample="latin-abbreviation"):
                self.assertNotEqual(
                    self._lint_text(mode, bad_text),
                    0,
                    f"A Latin abbreviation should be an error-level finding in {mode} mode.",
                )

    @staticmethod
    def _lint_text(mode: str, text: str) -> int:
        with tempfile.NamedTemporaryFile(
            "w", suffix=".md", delete=False, encoding="utf-8"
        ) as handle:
            handle.write(text)
            scratch_path = Path(handle.name)
        try:
            result = subprocess.run(
                [str(LINT_SCRIPT), mode, str(scratch_path)],
                capture_output=True,
                text=True,
                check=False,
            )
        finally:
            scratch_path.unlink(missing_ok=True)
        return result.returncode

    def test_no_internal_link_resolves_to_deleted_reference_files(self) -> None:
        deleted_resolved = {path.resolve() for path in DELETED_REFERENCE_FILES}
        for deleted_file in DELETED_REFERENCE_FILES:
            with self.subTest(deleted_file=str(deleted_file)):
                self.assertFalse(deleted_file.is_file(), f"{deleted_file} should have been deleted.")

        for source in (SKILL_MD, STANDALONE_WORKFLOW):
            with self.subTest(source=str(source)):
                content = source.read_text(encoding="utf-8")
                for link in MARKDOWN_LINK_RE.findall(content):
                    if link.startswith(("http://", "https://", "#")):
                        continue
                    target, _, _fragment = link.partition("#")
                    resolved = (source.parent / target).resolve()
                    self.assertNotIn(
                        resolved,
                        deleted_resolved,
                        f"{source} links to deleted reference file {target!r}.",
                    )


if __name__ == "__main__":
    unittest.main()
