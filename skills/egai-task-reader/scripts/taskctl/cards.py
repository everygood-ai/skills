"""Parse and validate a single task file's YAML frontmatter (its "card")."""

from __future__ import annotations

import json
import re
from pathlib import Path


REQUIRED_FIELDS = {
    "id",
    "title",
    "phase",
    "description",
    "deliverable",
    "acceptance_criteria",
    "parallel",
}
STRING_FIELDS = {"id", "title", "description", "deliverable"}
TASK_ID_RE = re.compile(r"^task-[1-9]\d*$")
TOP_LEVEL_RE = re.compile(r"^([a-z_]+):\s*(.*)$")
AC_ID_RE = re.compile(r'^  - id:\s*(.+)$')
AC_CRITERION_RE = re.compile(r'^    criterion:\s*(.+)$')


class TaskCardError(ValueError):
    pass


def parse_string(raw: str, label: str) -> str:
    if not raw.startswith('"') or not raw.endswith('"'):
        raise TaskCardError(f"{label} must be a double-quoted, single-line string")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as error:
        raise TaskCardError(f"{label} is not a valid quoted string: {error.msg}") from error
    if not isinstance(value, str) or not value.strip():
        raise TaskCardError(f"{label} must be a non-empty string")
    return value


def read_card(path: Path) -> tuple[list[str], list[str]]:
    with path.open(encoding="utf-8") as task_file:
        first_line = task_file.readline().rstrip("\r\n")
        if first_line.strip() != "---":
            raise TaskCardError("task file must start with frontmatter delimited by ---")
        raw_card = [first_line]
        card_lines: list[str] = []
        for raw_line in task_file:
            line = raw_line.rstrip("\r\n")
            raw_card.append(line)
            if line.strip() == "---":
                if not card_lines:
                    raise TaskCardError("task frontmatter must not be empty")
                return raw_card, card_lines
            card_lines.append(line)
    raise TaskCardError("task frontmatter is missing its closing --- delimiter")


def parse_card(lines: list[str]) -> dict[str, object]:
    data: dict[str, object] = {}
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        if line == "acceptance_criteria:":
            if "acceptance_criteria" in data:
                raise TaskCardError("acceptance_criteria appears more than once")
            criteria: list[dict[str, str]] = []
            index += 1
            while index < len(lines) and lines[index].startswith("  "):
                if not lines[index].strip():
                    index += 1
                    continue
                id_match = AC_ID_RE.fullmatch(lines[index])
                if not id_match:
                    raise TaskCardError("invalid acceptance criterion id entry")
                criterion_id = parse_string(
                    id_match.group(1).strip(), "acceptance criterion id"
                )
                index += 1
                if index >= len(lines):
                    raise TaskCardError(
                        f"acceptance criterion {criterion_id} is missing criterion"
                    )
                criterion_match = AC_CRITERION_RE.fullmatch(lines[index])
                if not criterion_match:
                    raise TaskCardError(
                        f"acceptance criterion {criterion_id} has invalid criterion syntax"
                    )
                criterion = parse_string(
                    criterion_match.group(1).strip(),
                    f"acceptance criterion {criterion_id}",
                )
                criteria.append({"id": criterion_id, "criterion": criterion})
                index += 1
            if not criteria:
                raise TaskCardError("acceptance_criteria must not be empty")
            data["acceptance_criteria"] = criteria
            continue

        match = TOP_LEVEL_RE.fullmatch(line)
        if not match or line.startswith(" "):
            raise TaskCardError(f"unsupported frontmatter syntax: {line!r}")
        key, raw_value = match.groups()
        if key not in REQUIRED_FIELDS:
            raise TaskCardError(f"unexpected frontmatter field: {key}")
        if key in data:
            raise TaskCardError(f"frontmatter field appears more than once: {key}")
        if key == "acceptance_criteria":
            raise TaskCardError("acceptance_criteria must not have an inline value")
        if key in STRING_FIELDS:
            data[key] = parse_string(raw_value.strip(), key)
        elif key == "phase":
            if not re.fullmatch(r"[1-9]\d*", raw_value.strip()):
                raise TaskCardError("phase must be a positive integer")
            data[key] = int(raw_value.strip())
        elif key == "parallel":
            if raw_value.strip() not in {"true", "false"}:
                raise TaskCardError("parallel must be true or false")
            data[key] = raw_value.strip() == "true"
        index += 1

    missing = REQUIRED_FIELDS - data.keys()
    if missing:
        raise TaskCardError(f"missing fields: {', '.join(sorted(missing))}")

    task_id = data["id"]
    criteria = data["acceptance_criteria"]
    assert isinstance(task_id, str)
    assert isinstance(criteria, list)
    if not TASK_ID_RE.fullmatch(task_id):
        raise TaskCardError("id must match task-N with a positive integer N")
    for criterion_number, criterion in enumerate(criteria, start=1):
        expected_id = f"{task_id}-{criterion_number}"
        if criterion["id"] != expected_id:
            raise TaskCardError(
                f"criterion {criterion_number} must have id {expected_id!r}"
            )
    return data
