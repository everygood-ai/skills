"""Unit and CLI tests for taskctl's card/ac command surface."""

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

from taskctl import cards  # noqa: E402

TASKCTL = SCRIPTS_DIR / "taskctl"
VALID_CARD = """\
---
id: "task-2"
title: "Add export endpoint"
phase: 1
description: "Add the invoice export endpoint."
deliverable: "A working invoice export endpoint."
acceptance_criteria:
  - id: "task-2-1"
    criterion: "Authorized requests return a CSV response."
  - id: "task-2-2"
    criterion: "Tests cover successful and invalid requests."
parallel: false
---
"""
VALID_TASK = VALID_CARD + """
# Task 2: Add export endpoint

## Scope

This body must not appear in taskctl output.
"""


class ParseStringTests(unittest.TestCase):
    def test_rejects_unquoted_value(self) -> None:
        with self.assertRaisesRegex(cards.TaskCardError, "double-quoted"):
            cards.parse_string("bare-value", "title")

    def test_rejects_empty_string(self) -> None:
        with self.assertRaisesRegex(cards.TaskCardError, "non-empty"):
            cards.parse_string('""', "title")

    def test_accepts_quoted_value(self) -> None:
        self.assertEqual(cards.parse_string('"Add export endpoint"', "title"), "Add export endpoint")


class ReadAndParseCardTests(unittest.TestCase):
    def test_read_card_stops_at_closing_delimiter(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            task_path = Path(temporary_directory) / "task-2-add-export-endpoint.md"
            task_path.write_text(VALID_TASK, encoding="utf-8")

            raw_card, card_lines = cards.read_card(task_path)

            self.assertEqual("\n".join(raw_card) + "\n", VALID_CARD)
            self.assertNotIn("This body must not appear", "\n".join(card_lines))

    def test_read_card_rejects_missing_leading_delimiter(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            task_path = Path(temporary_directory) / "task-2-add-export-endpoint.md"
            task_path.write_text("id: \"task-2\"\n", encoding="utf-8")

            with self.assertRaisesRegex(cards.TaskCardError, "must start with frontmatter"):
                cards.read_card(task_path)

    def test_parse_card_rejects_non_contiguous_acceptance_criterion_ids(self) -> None:
        invalid_task = VALID_TASK.replace('id: "task-2-2"', 'id: "task-2-3"')
        with tempfile.TemporaryDirectory() as temporary_directory:
            task_path = Path(temporary_directory) / "task-2-add-export-endpoint.md"
            task_path.write_text(invalid_task, encoding="utf-8")
            _, card_lines = cards.read_card(task_path)

            with self.assertRaisesRegex(cards.TaskCardError, "criterion 2 must have id 'task-2-2'"):
                cards.parse_card(card_lines)

    def test_parse_card_rejects_missing_fields(self) -> None:
        lines = ['id: "task-2"']
        with self.assertRaisesRegex(cards.TaskCardError, "missing fields"):
            cards.parse_card(lines)


class TaskctlCliTests(unittest.TestCase):
    def run_taskctl(
        self, command: str, task_contents: str = VALID_TASK
    ) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temporary_directory:
            task_path = Path(temporary_directory) / "task-2-add-export-endpoint.md"
            task_path.write_text(task_contents, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(TASKCTL), command, str(task_path)],
                check=False,
                capture_output=True,
                text=True,
                timeout=5,
            )

    def test_card_returns_only_complete_frontmatter(self) -> None:
        result = self.run_taskctl("card")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, VALID_CARD)
        self.assertNotIn("This body must not appear", result.stdout)

    def test_ac_returns_only_ids_and_criteria(self) -> None:
        result = self.run_taskctl("ac")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout,
            "- task-2-1 — Authorized requests return a CSV response.\n"
            "- task-2-2 — Tests cover successful and invalid requests.\n",
        )
        self.assertNotIn("deliverable", result.stdout)

    def test_rejects_non_contiguous_acceptance_criterion_ids(self) -> None:
        invalid_task = VALID_TASK.replace('id: "task-2-2"', 'id: "task-2-3"')

        result = self.run_taskctl("ac", invalid_task)

        self.assertEqual(result.returncode, 1)
        self.assertIn("criterion 2 must have id 'task-2-2'", result.stderr)

    def test_rejects_unknown_command(self) -> None:
        result = self.run_taskctl("list")

        self.assertEqual(result.returncode, 2)
        self.assertIn("usage: taskctl {card|ac} TASK_FILE", result.stderr)


if __name__ == "__main__":
    unittest.main()
