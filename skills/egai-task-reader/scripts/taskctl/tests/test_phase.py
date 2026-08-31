"""Unit and CLI tests for taskctl's phase-batch/phase-info/pr-body commands."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# `run-tests.py` runs this file as its own subprocess, so it must resolve and
# register the package location itself. The package lives one directory up
# from this file's parent (scripts/taskctl/tests -> scripts/taskctl -> scripts).
SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from taskctl import phase  # noqa: E402
from taskctl.cards import TaskCardError  # noqa: E402

TASKCTL = SCRIPTS_DIR / "taskctl"


def write_task(phase_dir: Path, number: int, title: str, ac_count: int, parallel: bool = False) -> None:
    criteria = "\n".join(
        f'  - id: "task-{number}-{n}"\n    criterion: "Criterion {n} holds."'
        for n in range(1, ac_count + 1)
    )
    (phase_dir / f"task-{number}-{title.lower().replace(' ', '-')}.md").write_text(
        "---\n"
        f'id: "task-{number}"\n'
        f'title: "{title}"\n'
        "phase: 11\n"
        f'description: "Does {title}."\n'
        f'deliverable: "A working {title}."\n'
        "acceptance_criteria:\n"
        f"{criteria}\n"
        f"parallel: {'true' if parallel else 'false'}\n"
        "---\n",
        encoding="utf-8",
    )


def write_phase_index(phase_dir: Path, name: str = "Billing Export") -> None:
    phase_dir.mkdir(exist_ok=True)
    (phase_dir / "index.md").write_text(
        f'---\nkind: "phase"\nname: "{name}"\n---\n'
        f"# Phase 11: {name}\n\n## Tasks\n",
        encoding="utf-8",
    )


class PhaseInfoUnitTests(unittest.TestCase):
    def test_prints_number_name_slug_branch_and_pr_title(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            phase_dir = Path(root) / "phase-11"
            write_phase_index(phase_dir)

            info = phase.phase_info(phase_dir)

            self.assertEqual(
                info,
                {
                    "number": "11",
                    "name": "Billing Export",
                    "slug": "billing-export",
                    "branch": "feature/phase-11-billing-export",
                    "pr_title": "Phase 11: Billing Export",
                },
            )

    def test_rejects_group_kind(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            phase_dir = Path(root) / "phase-11"
            phase_dir.mkdir()
            (phase_dir / "index.md").write_text(
                '---\nkind: "group"\nname: "Billing Export"\n---\n', encoding="utf-8"
            )

            with self.assertRaisesRegex(TaskCardError, "expected 'phase'"):
                phase.phase_info(phase_dir)


class PhaseTaskFilesUnitTests(unittest.TestCase):
    def test_rejects_empty_phase_directory(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            phase_dir = Path(root) / "phase-11"
            write_phase_index(phase_dir)

            with self.assertRaisesRegex(TaskCardError, "no task-N-\\*.md files found"):
                phase.phase_task_files(phase_dir)

    def test_sorts_by_numeric_task_id(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            phase_dir = Path(root) / "phase-11"
            write_phase_index(phase_dir)
            write_task(phase_dir, 10, "Tenth task", ac_count=1)
            write_task(phase_dir, 2, "Second task", ac_count=1)

            files = phase.phase_task_files(phase_dir)

            self.assertEqual([entry.name for entry in files], [
                "task-2-second-task.md",
                "task-10-tenth-task.md",
            ])


class PhaseBatchUnitTests(unittest.TestCase):
    def test_all_sequential_tasks_are_their_own_units(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            phase_dir = Path(root) / "phase-11"
            write_phase_index(phase_dir)
            write_task(phase_dir, 1, "First task", ac_count=1, parallel=False)
            write_task(phase_dir, 2, "Second task", ac_count=1, parallel=False)

            result = phase.phase_batch(phase_dir)

            self.assertEqual(
                result,
                {
                    "units": [
                        [{"id": "task-1", "file": "task-1-first-task.md"}],
                        [{"id": "task-2", "file": "task-2-second-task.md"}],
                    ]
                },
            )

    def test_consecutive_parallel_tasks_group_into_one_unit(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            phase_dir = Path(root) / "phase-11"
            write_phase_index(phase_dir)
            write_task(phase_dir, 1, "First task", ac_count=1, parallel=False)
            write_task(phase_dir, 2, "Second task", ac_count=1, parallel=True)
            write_task(phase_dir, 3, "Third task", ac_count=1, parallel=True)
            write_task(phase_dir, 4, "Fourth task", ac_count=1, parallel=False)

            result = phase.phase_batch(phase_dir)

            self.assertEqual(
                result,
                {
                    "units": [
                        [{"id": "task-1", "file": "task-1-first-task.md"}],
                        [
                            {"id": "task-2", "file": "task-2-second-task.md"},
                            {"id": "task-3", "file": "task-3-third-task.md"},
                        ],
                        [{"id": "task-4", "file": "task-4-fourth-task.md"}],
                    ]
                },
            )

    def test_trailing_parallel_run_forms_the_final_unit(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            phase_dir = Path(root) / "phase-11"
            write_phase_index(phase_dir)
            write_task(phase_dir, 1, "First task", ac_count=1, parallel=True)
            write_task(phase_dir, 2, "Second task", ac_count=1, parallel=True)

            result = phase.phase_batch(phase_dir)

            self.assertEqual(
                result,
                {
                    "units": [
                        [
                            {"id": "task-1", "file": "task-1-first-task.md"},
                            {"id": "task-2", "file": "task-2-second-task.md"},
                        ],
                    ]
                },
            )

    def test_rejects_empty_phase_directory(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            phase_dir = Path(root) / "phase-11"
            write_phase_index(phase_dir)

            with self.assertRaisesRegex(TaskCardError, "no task-N-\\*.md files found"):
                phase.phase_batch(phase_dir)

    def test_propagates_malformed_card_error(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            phase_dir = Path(root) / "phase-11"
            write_phase_index(phase_dir)
            (phase_dir / "task-1-broken.md").write_text(
                '---\nid: "task-1"\n---\n', encoding="utf-8"
            )

            with self.assertRaisesRegex(TaskCardError, "missing fields"):
                phase.phase_batch(phase_dir)


class PrBodyUnitTests(unittest.TestCase):
    def test_builds_title_stacking_note_bullets_and_criterion_count(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            phase_dir = Path(root) / "phase-11"
            write_phase_index(phase_dir)
            write_task(phase_dir, 1, "Add export endpoint", ac_count=2)
            write_task(phase_dir, 2, "Update docs", ac_count=1)

            body = phase.pr_body(phase_dir, "feature/phase-10-invoicing")

            self.assertEqual(
                body,
                "Phase 11: Billing Export\n"
                "\n"
                "Stacked on `feature/phase-10-invoicing`.\n"
                "\n"
                "- **Add export endpoint** — Does Add export endpoint. "
                "A working Add export endpoint.\n"
                "- **Update docs** — Does Update docs. A working Update docs.\n"
                "\n"
                "3 acceptance criteria verified across 2 tasks.",
            )


class PhaseInfoCliTests(unittest.TestCase):
    def run_phase_info(self, phase_dir: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(TASKCTL), "phase-info", str(phase_dir)],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )

    def test_prints_number_name_slug_branch_and_pr_title(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            phase_dir = Path(root) / "phase-11"
            write_phase_index(phase_dir)

            result = self.run_phase_info(phase_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                result.stdout,
                "number: 11\n"
                "name: Billing Export\n"
                "slug: billing-export\n"
                "branch: feature/phase-11-billing-export\n"
                "pr_title: Phase 11: Billing Export\n",
            )

    def test_rejects_missing_frontmatter(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            phase_dir = Path(root) / "phase-11"
            phase_dir.mkdir()
            (phase_dir / "index.md").write_text("# Phase 11\n", encoding="utf-8")

            result = self.run_phase_info(phase_dir)

            self.assertEqual(result.returncode, 1)
            self.assertIn("must start with frontmatter", result.stderr)


class PrBodyCliTests(unittest.TestCase):
    def run_pr_body(self, phase_dir: Path, base_branch: str = "feature/phase-10-invoicing") -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(TASKCTL), "pr-body", str(phase_dir), base_branch],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )

    def test_builds_title_stacking_note_bullets_and_criterion_count(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            phase_dir = Path(root) / "phase-11"
            write_phase_index(phase_dir)
            write_task(phase_dir, 1, "Add export endpoint", ac_count=2)
            write_task(phase_dir, 2, "Update docs", ac_count=1)

            result = self.run_pr_body(phase_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                result.stdout,
                "Phase 11: Billing Export\n"
                "\n"
                "Stacked on `feature/phase-10-invoicing`.\n"
                "\n"
                "- **Add export endpoint** — Does Add export endpoint. "
                "A working Add export endpoint.\n"
                "- **Update docs** — Does Update docs. A working Update docs.\n"
                "\n"
                "3 acceptance criteria verified across 2 tasks.\n",
            )

    def test_rejects_phase_with_no_task_files(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            phase_dir = Path(root) / "phase-11"
            write_phase_index(phase_dir)

            result = self.run_pr_body(phase_dir)

            self.assertEqual(result.returncode, 1)
            self.assertIn("no task-N-*.md files found", result.stderr)


class PhaseBatchCliTests(unittest.TestCase):
    def run_phase_batch(self, phase_dir: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(TASKCTL), "phase-batch", str(phase_dir)],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )

    def test_prints_ordered_units_as_json(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            phase_dir = Path(root) / "phase-11"
            write_phase_index(phase_dir)
            write_task(phase_dir, 1, "First task", ac_count=1, parallel=False)
            write_task(phase_dir, 2, "Second task", ac_count=1, parallel=True)
            write_task(phase_dir, 3, "Third task", ac_count=1, parallel=True)

            result = self.run_phase_batch(phase_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                json.loads(result.stdout),
                {
                    "units": [
                        [{"id": "task-1", "file": "task-1-first-task.md"}],
                        [
                            {"id": "task-2", "file": "task-2-second-task.md"},
                            {"id": "task-3", "file": "task-3-third-task.md"},
                        ],
                    ]
                },
            )

    def test_rejects_phase_with_no_task_files(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            phase_dir = Path(root) / "phase-11"
            write_phase_index(phase_dir)

            result = self.run_phase_batch(phase_dir)

            self.assertEqual(result.returncode, 1)
            self.assertIn("no task-N-*.md files found", result.stderr)

    def test_rejects_malformed_card(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            phase_dir = Path(root) / "phase-11"
            write_phase_index(phase_dir)
            (phase_dir / "task-1-broken.md").write_text(
                '---\nid: "task-1"\n---\n', encoding="utf-8"
            )

            result = self.run_phase_batch(phase_dir)

            self.assertEqual(result.returncode, 1)
            self.assertIn("error:", result.stderr)
            self.assertIn("missing fields", result.stderr)


if __name__ == "__main__":
    unittest.main()
