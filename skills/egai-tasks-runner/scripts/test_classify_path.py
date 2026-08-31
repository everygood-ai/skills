from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


CLASSIFY_PATH = Path(__file__).resolve().parent / "classify-path.py"

GROUP_INDEX = '---\nkind: "group"\nname: "Plan"\n---\n# Plan\n'
PHASE_INDEX = '---\nkind: "phase"\nname: "Name"\n---\n# Phase 1: Name\n'


class ClassifyPathTests(unittest.TestCase):
    def run_classify(self, target: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CLASSIFY_PATH), str(target)],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )

    def test_directory_with_index_and_subnode_is_group(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            plan_root = Path(root)
            (plan_root / "index.md").write_text(GROUP_INDEX, encoding="utf-8")
            phase_dir = plan_root / "phase-1"
            phase_dir.mkdir()
            (phase_dir / "index.md").write_text(PHASE_INDEX, encoding="utf-8")

            result = self.run_classify(plan_root)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "group\n")

    def test_index_file_resolves_to_its_directorys_kind(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            plan_root = Path(root)
            index_path = plan_root / "index.md"
            index_path.write_text(GROUP_INDEX, encoding="utf-8")
            phase_dir = plan_root / "phase-1"
            phase_dir.mkdir()
            (phase_dir / "index.md").write_text(PHASE_INDEX, encoding="utf-8")

            result = self.run_classify(index_path)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "group\n")

    def test_nested_groups_are_still_classified_as_group(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            portfolio_root = Path(root)
            (portfolio_root / "index.md").write_text(GROUP_INDEX, encoding="utf-8")
            epic_dir = portfolio_root / "epic-foo"
            epic_dir.mkdir()
            (epic_dir / "index.md").write_text(GROUP_INDEX, encoding="utf-8")
            phase_dir = epic_dir / "phase-1"
            phase_dir.mkdir()
            (phase_dir / "index.md").write_text(PHASE_INDEX, encoding="utf-8")

            self.assertEqual(self.run_classify(portfolio_root).stdout, "group\n")
            self.assertEqual(self.run_classify(epic_dir).stdout, "group\n")

    def test_empty_group_directory_classifies_as_group(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            empty_group = Path(root)
            (empty_group / "index.md").write_text(GROUP_INDEX, encoding="utf-8")

            result = self.run_classify(empty_group)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "group\n")

    def test_directory_with_index_and_task_files_is_phase(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            phase_dir = Path(root)
            (phase_dir / "index.md").write_text(PHASE_INDEX, encoding="utf-8")
            (phase_dir / "task-1-do-thing.md").write_text("---\n---\n", encoding="utf-8")

            result = self.run_classify(phase_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "phase\n")

    def test_task_file_is_task(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            task_path = Path(root) / "task-3-add-export-endpoint.md"
            task_path.write_text("---\n---\n", encoding="utf-8")

            result = self.run_classify(task_path)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "task\n")

    def test_nonexistent_path_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            missing = Path(root) / "missing.md"

            result = self.run_classify(missing)

            self.assertEqual(result.returncode, 1)
            self.assertIn("does not exist", result.stderr)

    def test_directory_without_index_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            unrelated = Path(root) / "notes"
            unrelated.mkdir()
            (unrelated / "readme.md").write_text("hello\n", encoding="utf-8")

            result = self.run_classify(unrelated)

            self.assertEqual(result.returncode, 1)
            self.assertIn("has no index.md", result.stderr)

    def test_index_without_frontmatter_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            node = Path(root)
            (node / "index.md").write_text("# Empty\n", encoding="utf-8")

            result = self.run_classify(node)

            self.assertEqual(result.returncode, 1)
            self.assertIn("must start with frontmatter", result.stderr)

    def test_index_with_invalid_kind_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            node = Path(root)
            (node / "index.md").write_text(
                '---\nkind: "portfolio"\nname: "Plan"\n---\n# Plan\n', encoding="utf-8"
            )

            result = self.run_classify(node)

            self.assertEqual(result.returncode, 1)
            self.assertIn('kind must be "group" or "phase"', result.stderr)

    def test_unrecognized_file_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            stray_file = Path(root) / "notes.md"
            stray_file.write_text("hello\n", encoding="utf-8")

            result = self.run_classify(stray_file)

            self.assertEqual(result.returncode, 1)
            self.assertIn("not index.md or a task-N-*.md file", result.stderr)

    def test_wrong_argument_count_is_a_usage_error(self) -> None:
        result = subprocess.run(
            [sys.executable, str(CLASSIFY_PATH)],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("usage: classify-path.py PATH", result.stderr)


if __name__ == "__main__":
    unittest.main()
