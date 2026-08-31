#!/usr/bin/env python3
"""CLI dispatcher for taskctl.

Invoked as `python3 SKILL_DIRECTORY/scripts/taskctl COMMAND ARGS`. Python runs
a directory's __main__.py directly, so this module makes the package
importable by name (`taskctl`) before importing its sibling modules, since a
direct directory invocation does not otherwise know this directory's parent
belongs on sys.path.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    __package__ = "taskctl"

from taskctl.cards import TaskCardError, parse_card, read_card
from taskctl.phase import phase_batch, phase_info, pr_body
from taskctl.validate import run as run_validate


USAGE = (
    "usage: taskctl {card|ac} TASK_FILE "
    "| taskctl phase-batch PHASE_DIR "
    "| taskctl phase-info PHASE_DIR "
    "| taskctl pr-body PHASE_DIR BASE_BRANCH "
    "| taskctl validate TASK_FILE_OR_DIRECTORY [...]"
)


def main() -> int:
    if len(sys.argv) == 3 and sys.argv[1] == "phase-batch":
        phase_dir = Path(sys.argv[2])
        try:
            result = phase_batch(phase_dir)
        except (OSError, UnicodeError, TaskCardError) as error:
            print(f"error: {phase_dir}: {error}", file=sys.stderr)
            return 1
        print(json.dumps(result))
        return 0

    if len(sys.argv) == 3 and sys.argv[1] == "phase-info":
        phase_dir = Path(sys.argv[2])
        try:
            info = phase_info(phase_dir)
        except (OSError, UnicodeError, TaskCardError) as error:
            print(f"error: {phase_dir}: {error}", file=sys.stderr)
            return 1
        for key in ("number", "name", "slug", "branch", "pr_title"):
            print(f"{key}: {info[key]}")
        return 0

    if len(sys.argv) == 4 and sys.argv[1] == "pr-body":
        phase_dir = Path(sys.argv[2])
        base_branch = sys.argv[3]
        try:
            print(pr_body(phase_dir, base_branch))
        except (OSError, UnicodeError, TaskCardError) as error:
            print(f"error: {phase_dir}: {error}", file=sys.stderr)
            return 1
        return 0

    if len(sys.argv) >= 3 and sys.argv[1] == "validate":
        return run_validate(sys.argv[2:])

    if len(sys.argv) != 3 or sys.argv[1] not in {"card", "ac"}:
        print(USAGE, file=sys.stderr)
        return 2
    command = sys.argv[1]
    path = Path(sys.argv[2])
    try:
        raw_card, card_lines = read_card(path)
        data = parse_card(card_lines)
    except (OSError, UnicodeError, TaskCardError) as error:
        print(f"error: {path}: {error}", file=sys.stderr)
        return 1

    if command == "card":
        print("\n".join(raw_card))
        return 0

    criteria = data["acceptance_criteria"]
    assert isinstance(criteria, list)
    for criterion in criteria:
        print(f"- {criterion['id']} — {criterion['criterion']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
