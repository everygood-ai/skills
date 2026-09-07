from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


VALIDATOR = Path(__file__).resolve().parent / "validate_changelog.py"


class ValidateChangelogTests(unittest.TestCase):
    def run_validator(self, contents: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temporary_directory:
            changelog_path = Path(temporary_directory) / "changelog.md"
            changelog_path.write_text(contents, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(VALIDATOR), str(changelog_path)],
                capture_output=True,
                text=True,
                check=False,
            )

    def test_flat_bullets_pass(self) -> None:
        result = self.run_validator(
            "# Changelog\n\n"
            "- `1.1.0` — Added CSV export and validation.\n"
            "- `1.0.0` — Created the initial skill.\n"
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_nested_bullet_list_passes(self) -> None:
        result = self.run_validator(
            "# Changelog\n\n"
            "- `1.1.0`\n"
            "  - Added CSV export.\n"
            "  - Validated exported rows against the schema.\n"
            "- `1.0.0` — Created the initial skill.\n"
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_bullet_over_word_limit_fails(self) -> None:
        long_summary = " ".join(f"word{index}" for index in range(51))
        result = self.run_validator(f"# Changelog\n\n- `1.0.0` — {long_summary}\n")
        self.assertEqual(result.returncode, 1)
        self.assertIn("exceeding the 50-word limit", result.stderr)

    def test_nested_bullet_over_word_limit_fails(self) -> None:
        long_summary = " ".join(f"word{index}" for index in range(51))
        result = self.run_validator(
            f"# Changelog\n\n- `1.0.0`\n  - {long_summary}\n"
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("exceeding the 50-word limit", result.stderr)

    def test_version_with_no_content_fails(self) -> None:
        result = self.run_validator("# Changelog\n\n- `1.0.0`\n- `0.9.0` — Earlier.\n")
        self.assertEqual(result.returncode, 1)
        self.assertIn("no summary bullet and no indented bullet list", result.stderr)

    def test_duplicate_version_fails(self) -> None:
        result = self.run_validator(
            "# Changelog\n\n- `1.0.0` — First.\n- `1.0.0` — Duplicate.\n"
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicates the entry", result.stderr)

    def test_invalid_semver_fails(self) -> None:
        result = self.run_validator("# Changelog\n\n- `1.0` — Bad version.\n")
        self.assertEqual(result.returncode, 1)
        self.assertIn("not a MAJOR.MINOR.PATCH version", result.stderr)

    def test_no_entries_fails(self) -> None:
        result = self.run_validator("# Changelog\n\nNothing here.\n")
        self.assertEqual(result.returncode, 1)
        self.assertIn("no version entries found", result.stderr)

    def test_missing_file_is_usage_error(self) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), "/no/such/changelog.md"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
