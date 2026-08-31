"""CLI tests for taskctl's `validate` command.

Ported from egai-tasks-writing's former scripts/test_validate_tasks.py,
adapted to invoke `taskctl validate TASK_PATH` instead of the standalone
validate-tasks.py script.
"""

from __future__ import annotations

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

TASKCTL = SCRIPTS_DIR / "taskctl"
VALID_TASK = """\
---
id: "task-1"
title: "Add export endpoint"
phase: 1
description: "Add the invoice export endpoint."
deliverable: "A working invoice export endpoint."
acceptance_criteria:
  - id: "task-1-1"
    criterion: "Authorized requests return a CSV response."
  - id: "task-1-2"
    criterion: "Tests cover successful and invalid requests."
parallel: false
---

# Task 1: Add export endpoint

## Scope

Add the endpoint without changing unrelated routes.
"""

VALID_TASK_PHASE2 = """\
---
id: "task-2"
title: "Update Context"
phase: 2
description: "Update project context to reflect phase changes."
deliverable: "Updated context files describing the new endpoint."
acceptance_criteria:
  - id: "task-2-1"
    criterion: "egai-context-curation reports inspected scope and changed context files."
parallel: false
---

# Task 2: Update Context

## Scope

Invoke egai-context-curation in incremental-update mode.
"""

PLAN_INDEX = (
    '---\nkind: "group"\nname: "Plan"\n---\n'
    "# Plan\n\nOne plan root with no links to check.\n"
)
PHASE_INDEX = (
    '---\nkind: "phase"\nname: "Name"\n---\n'
    "# Phase 1: Name\n\nNo links to check.\n"
)
PHASE_INDEX_2 = (
    '---\nkind: "phase"\nname: "Name"\n---\n'
    "# Phase 2: Name\n\nNo links to check.\n"
)


class ValidateCommandTests(unittest.TestCase):
    def run_validator(
        self,
        files: dict[str, str],
        target_name: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temporary_directory:
            task_directory = Path(temporary_directory)
            for filename, contents in files.items():
                file_path = task_directory / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(contents, encoding="utf-8")
            target = task_directory if target_name is None else task_directory / target_name
            return subprocess.run(
                [sys.executable, str(TASKCTL), "validate", str(target)],
                check=False,
                capture_output=True,
                text=True,
                timeout=5,
            )

    def test_accepts_valid_task_file(self) -> None:
        result = self.run_validator(
            {
                "index.md": PLAN_INDEX,
                "phase-1/index.md": PHASE_INDEX,
                "phase-1/task-1-add-export-endpoint.md": VALID_TASK,
            },
            "phase-1/task-1-add-export-endpoint.md",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS", result.stdout)
        self.assertIn("Validated 1 task files", result.stdout)

    def test_rejects_missing_required_field(self) -> None:
        invalid_task = VALID_TASK.replace('deliverable: "A working invoice export endpoint."\n', "")

        result = self.run_validator({"task-1-add-export-endpoint.md": invalid_task})

        self.assertEqual(result.returncode, 1)
        self.assertIn("missing frontmatter fields: deliverable", result.stderr)

    def test_rejects_filename_and_task_id_mismatch(self) -> None:
        result = self.run_validator({"task-2-add-export-endpoint.md": VALID_TASK})

        self.assertEqual(result.returncode, 1)
        self.assertIn("id must be 'task-2' to match the filename", result.stderr)

    def test_rejects_heading_and_title_mismatch(self) -> None:
        invalid_task = VALID_TASK.replace(
            "# Task 1: Add export endpoint", "# Task 1: Add CSV endpoint"
        )

        result = self.run_validator({"phase-1/task-1-add-export-endpoint.md": invalid_task})

        self.assertEqual(result.returncode, 1)
        self.assertIn("first body heading must be", result.stderr)

    def test_rejects_non_contiguous_acceptance_criterion_ids(self) -> None:
        invalid_task = VALID_TASK.replace('id: "task-1-2"', 'id: "task-1-3"')

        result = self.run_validator({"phase-1/task-1-add-export-endpoint.md": invalid_task})

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "acceptance criterion 2 must have id 'task-1-2'", result.stderr
        )

    def test_accepts_task_in_matching_phase_directory(self) -> None:
        result = self.run_validator(
            {
                "index.md": PLAN_INDEX,
                "phase-1/index.md": PHASE_INDEX,
                "phase-1/task-1-add-export-endpoint.md": VALID_TASK,
            },
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS", result.stdout)
        self.assertIn("Validated 1 task files", result.stdout)

    def test_rejects_task_with_mismatched_phase_directory(self) -> None:
        result = self.run_validator(
            {"phase-2/task-1-add-export-endpoint.md": VALID_TASK},
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("does not match", result.stderr)

    def test_accepts_tasks_spanning_multiple_phase_directories(self) -> None:
        result = self.run_validator(
            {
                "index.md": PLAN_INDEX,
                "phase-1/index.md": PHASE_INDEX,
                "phase-1/task-1-add-export-endpoint.md": VALID_TASK,
                "phase-2/index.md": PHASE_INDEX_2,
                "phase-2/task-2-update-context.md": VALID_TASK_PHASE2,
            },
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Validated 2 task files", result.stdout)

    def test_rejects_orphan_task_at_plan_root(self) -> None:
        result = self.run_validator(
            {"task-1-add-export-endpoint.md": VALID_TASK},
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("must be the direct child of a phase-N directory", result.stderr)

    def test_rejects_missing_index_in_plan_root(self) -> None:
        result = self.run_validator(
            {
                "phase-1/index.md": PHASE_INDEX,
                "phase-1/task-1-add-export-endpoint.md": VALID_TASK,
            },
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("plan root is missing index.md", result.stderr)

    def test_rejects_missing_index_in_phase_dir(self) -> None:
        result = self.run_validator(
            {
                "index.md": PLAN_INDEX,
                "phase-1/task-1-add-export-endpoint.md": VALID_TASK,
            },
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("phase directory is missing index.md", result.stderr)

    def test_accepts_nested_epic_task(self) -> None:
        result = self.run_validator(
            {
                "epic-foo/index.md": PLAN_INDEX,
                "epic-foo/phase-1/index.md": PHASE_INDEX,
                "epic-foo/phase-1/task-1-add-export-endpoint.md": VALID_TASK,
            },
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Validated 1 task files", result.stdout)

    def test_accepts_multiple_epics_with_duplicate_local_ids(self) -> None:
        result = self.run_validator(
            {
                "index.md": '---\nkind: "group"\nname: "Portfolio"\n---\n# Portfolio\n',
                "epic-foo/index.md": PLAN_INDEX,
                "epic-foo/phase-1/index.md": PHASE_INDEX,
                "epic-foo/phase-1/task-1-add-export-endpoint.md": VALID_TASK,
                "epic-bar/index.md": PLAN_INDEX,
                "epic-bar/phase-1/index.md": PHASE_INDEX,
                "epic-bar/phase-1/task-1-add-export-endpoint.md": VALID_TASK,
            },
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Validated 2 task files", result.stdout)

    def test_validates_epic_root_directly(self) -> None:
        result = self.run_validator(
            {
                "epic-foo/index.md": PLAN_INDEX,
                "epic-foo/phase-1/index.md": PHASE_INDEX,
                "epic-foo/phase-1/task-1-add-export-endpoint.md": VALID_TASK,
            },
            "epic-foo",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Validated 1 task files", result.stdout)

    def test_rejects_phase_nested_too_deep_under_epic(self) -> None:
        result = self.run_validator(
            {
                "epic-foo/index.md": PLAN_INDEX,
                "epic-foo/extra/phase-1/task-1-add-export-endpoint.md": VALID_TASK,
            },
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("nested too deeply under epic", result.stderr)

    def test_rejects_mixed_layout_in_single_plan_root(self) -> None:
        result = self.run_validator(
            {
                "index.md": PLAN_INDEX,
                "phase-1/index.md": PHASE_INDEX,
                "phase-1/task-1-add-export-endpoint.md": VALID_TASK,
                "epic-foo/index.md": PLAN_INDEX,
                "epic-foo/phase-1/index.md": PHASE_INDEX,
                "epic-foo/phase-1/task-1-add-export-endpoint.md": VALID_TASK,
            },
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("mixes epic subdirectories", result.stderr)

    def test_rejects_phase_index_heading_mismatched_with_frontmatter_name(self) -> None:
        mismatched_phase_index = (
            '---\nkind: "phase"\nname: "Name"\n---\n'
            "# Phase 1: A Different Name\n\nNo links to check.\n"
        )
        result = self.run_validator(
            {
                "index.md": PLAN_INDEX,
                "phase-1/index.md": mismatched_phase_index,
                "phase-1/task-1-add-export-endpoint.md": VALID_TASK,
            },
            "phase-1/task-1-add-export-endpoint.md",
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("first body heading must be", result.stderr)

    def test_rejects_phase_index_with_group_kind(self) -> None:
        group_kind_phase_index = '---\nkind: "group"\nname: "Name"\n---\n# Phase 1: Name\n'
        result = self.run_validator(
            {
                "index.md": PLAN_INDEX,
                "phase-1/index.md": group_kind_phase_index,
                "phase-1/task-1-add-export-endpoint.md": VALID_TASK,
            },
            "phase-1/task-1-add-export-endpoint.md",
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("has kind 'group', expected 'phase'", result.stderr)

    def test_rejects_portfolio_root_passed_directly_with_bad_frontmatter(self) -> None:
        result = self.run_validator(
            {
                "index.md": "# Portfolio\n",
                "epic-foo/index.md": PLAN_INDEX,
                "epic-foo/phase-1/index.md": PHASE_INDEX,
                "epic-foo/phase-1/task-1-add-export-endpoint.md": VALID_TASK,
            },
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("must start with YAML frontmatter", result.stderr)


if __name__ == "__main__":
    unittest.main()
