from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


FILTER = Path(__file__).resolve().parent / "filter-orphans.py"


def orphan_warning(file: str) -> dict:
    return {
        "level": "warning",
        "category": "Structure",
        "message": f"potentially unreferenced file: {file} — agents may not discover this file",
        "file": file,
    }


class FilterOrphansTests(unittest.TestCase):
    def run_filter(self, report: dict) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(FILTER)],
            input=json.dumps(report),
            capture_output=True,
            text=True,
            check=False,
        )

    def test_exempts_test_file_gaps_changelog_and_readme(self) -> None:
        report = {
            "results": [
                orphan_warning("scripts/test_helper.py"),
                orphan_warning("gaps.md"),
                orphan_warning("changelog.md"),
                orphan_warning("README.md"),
            ]
        }
        result = self.run_filter(report)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("INFO", result.stdout)
        self.assertNotIn("WARNING", result.stdout)

    def test_keeps_real_orphan_warning(self) -> None:
        report = {"results": [orphan_warning("scripts/helper.py")]}
        result = self.run_filter(report)
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn("WARNING", result.stdout)

    def test_keeps_errors_and_fails(self) -> None:
        report = {
            "results": [
                {"level": "error", "category": "Frontmatter", "message": "name is missing"},
                orphan_warning("gaps.md"),
            ]
        }
        result = self.run_filter(report)
        self.assertEqual(result.returncode, 1, result.stdout)

    def test_non_orphan_warning_is_untouched(self) -> None:
        report = {
            "results": [
                {"level": "warning", "category": "Content", "message": "some other warning"},
            ]
        }
        result = self.run_filter(report)
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn("some other warning", result.stdout)

    def test_invalid_json_passes_through_and_exits_3(self) -> None:
        result = subprocess.run(
            [sys.executable, str(FILTER)],
            input="not json",
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 3)
        self.assertEqual(result.stdout, "not json")


if __name__ == "__main__":
    unittest.main()
