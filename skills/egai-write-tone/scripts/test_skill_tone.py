from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
LINT_SCRIPT = SCRIPTS_DIR / "lint.sh"
SKILLS_DIR = SCRIPTS_DIR.parent.parent
SKILL_FILES = sorted(SKILLS_DIR.glob("*/SKILL.md"))

VALE_INSTALLED = shutil.which("vale") is not None


class SkillToneTests(unittest.TestCase):
    @unittest.skipUnless(VALE_INSTALLED, "vale is not installed; run install.sh, then rerun tests")
    def test_every_skill_file_passes_prose_tone_lint(self) -> None:
        self.assertTrue(SKILL_FILES, "No SKILL.md files found under skills/.")
        for skill_file in SKILL_FILES:
            with self.subTest(skill=str(skill_file.relative_to(SKILLS_DIR))):
                result = subprocess.run(
                    [str(LINT_SCRIPT), "prose", str(skill_file)],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(
                    result.returncode,
                    0,
                    f"egai-write-tone prose-mode lint failed for {skill_file}:\n"
                    f"{result.stdout}{result.stderr}",
                )


if __name__ == "__main__":
    unittest.main()
