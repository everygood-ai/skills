"""Validate a plan's task cards and phase structure at authoring time.

Ported from egai-tasks-writing's former validate-tasks.py. Reuses cards.py's
identical low-level regexes and quoted-string parser, and phase.py's
identical directory-naming regexes, instead of redefining them. Keeps its own
field-parsing loops and error text, since those diverged in wording from
cards.py's lighter, single-card parsing and this module's authoring-time
diagnostics are load-bearing for callers.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

from .cards import (
    AC_CRITERION_RE,
    AC_ID_RE,
    REQUIRED_FIELDS,
    STRING_FIELDS,
    TOP_LEVEL_RE,
    parse_string,
)
from .phase import INDEX_REQUIRED_FIELDS, PHASE_DIR_RE, TASK_FILENAME_RE as TASK_FILE_RE


EPIC_DIR_RE = re.compile(r"^epic-[a-z0-9]+(?:-[a-z0-9]+)*$")
MARKDOWN_LINK_RE = re.compile(r"\]\(([^)]+)\)")


class TaskValidationError(ValueError):
    pass


@dataclass(frozen=True)
class ValidatedTask:
    task_id: str
    plan_root: Path
    phase_dir: Path


def extract_frontmatter(text: str) -> tuple[list[str], list[str]]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise TaskValidationError("file must start with YAML frontmatter delimited by ---")
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            if index == 1:
                raise TaskValidationError("frontmatter must not be empty")
            return lines[1:index], lines[index + 1 :]
    raise TaskValidationError("frontmatter is missing its closing --- delimiter")


def parse_frontmatter(lines: list[str]) -> dict[str, object]:
    data: dict[str, object] = {}
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        if line == "acceptance_criteria:":
            if "acceptance_criteria" in data:
                raise TaskValidationError("acceptance_criteria appears more than once")
            criteria: list[dict[str, str]] = []
            index += 1
            while index < len(lines) and lines[index].startswith("  "):
                if not lines[index].strip():
                    index += 1
                    continue
                id_match = AC_ID_RE.fullmatch(lines[index])
                if not id_match:
                    raise TaskValidationError(
                        "acceptance_criteria entries must start with two-space '- id:'"
                    )
                criterion_id = parse_string(
                    id_match.group(1).strip(), "acceptance criterion id"
                )
                index += 1
                if index >= len(lines):
                    raise TaskValidationError(
                        f"acceptance criterion {criterion_id} is missing criterion"
                    )
                criterion_match = AC_CRITERION_RE.fullmatch(lines[index])
                if not criterion_match:
                    raise TaskValidationError(
                        f"acceptance criterion {criterion_id} must have four-space 'criterion:'"
                    )
                criterion = parse_string(
                    criterion_match.group(1).strip(),
                    f"acceptance criterion {criterion_id}",
                )
                criteria.append({"id": criterion_id, "criterion": criterion})
                index += 1
            if not criteria:
                raise TaskValidationError("acceptance_criteria must contain at least one entry")
            data["acceptance_criteria"] = criteria
            continue

        match = TOP_LEVEL_RE.fullmatch(line)
        if not match or line.startswith(" "):
            raise TaskValidationError(f"unsupported frontmatter syntax: {line!r}")
        key, raw_value = match.groups()
        if key not in REQUIRED_FIELDS:
            raise TaskValidationError(f"unexpected frontmatter field: {key}")
        if key in data:
            raise TaskValidationError(f"frontmatter field appears more than once: {key}")
        if key == "acceptance_criteria":
            raise TaskValidationError("acceptance_criteria must not have an inline value")
        if key in STRING_FIELDS:
            data[key] = parse_string(raw_value.strip(), key)
        elif key == "phase":
            if not re.fullmatch(r"[1-9]\d*", raw_value.strip()):
                raise TaskValidationError("phase must be a positive integer")
            data[key] = int(raw_value.strip())
        elif key == "parallel":
            if raw_value.strip() not in {"true", "false"}:
                raise TaskValidationError("parallel must be the YAML boolean true or false")
            data[key] = raw_value.strip() == "true"
        index += 1

    missing = REQUIRED_FIELDS - data.keys()
    if missing:
        raise TaskValidationError(f"missing frontmatter fields: {', '.join(sorted(missing))}")
    return data


def validate_task(path: Path) -> ValidatedTask:
    match = TASK_FILE_RE.fullmatch(path.name)
    if not match:
        raise TaskValidationError("filename must match task-N-short-name.md")
    task_number = int(match.group(1))
    frontmatter, body = extract_frontmatter(path.read_text(encoding="utf-8"))
    data = parse_frontmatter(frontmatter)
    expected_task_id = f"task-{task_number}"
    if data["id"] != expected_task_id:
        raise TaskValidationError(
            f"id must be {expected_task_id!r} to match the filename"
        )

    phase_dir = path.parent
    phase_dir_match = PHASE_DIR_RE.fullmatch(phase_dir.name)
    if not phase_dir_match:
        raise TaskValidationError(
            "task file must be the direct child of a phase-N directory, "
            f"not {phase_dir.name!r}"
        )
    dir_phase = int(phase_dir_match.group(1))
    if data["phase"] != dir_phase:
        raise TaskValidationError(
            f"phase {data['phase']} in frontmatter does not match "
            f"the containing directory phase-{dir_phase}"
        )

    plan_root = phase_dir.parent
    epic_ancestor = plan_root.parent
    if EPIC_DIR_RE.fullmatch(epic_ancestor.name):
        raise TaskValidationError(
            f"phase-{dir_phase} is nested too deeply under epic "
            f"{epic_ancestor.name!r}; place phase directories directly under "
            "the plan root or an epic root, not inside an extra subdirectory "
            "or a nested epic"
        )
    if any(
        child.is_dir() and EPIC_DIR_RE.fullmatch(child.name)
        for child in plan_root.iterdir()
    ):
        raise TaskValidationError(
            f"plan root {plan_root} mixes epic subdirectories with a phase "
            "directory nested directly inside it; move phase directories "
            "under an epic root or remove the epic subdirectories"
        )

    criteria = data["acceptance_criteria"]
    assert isinstance(criteria, list)
    for criterion_number, criterion in enumerate(criteria, start=1):
        expected_criterion_id = f"{expected_task_id}-{criterion_number}"
        if criterion["id"] != expected_criterion_id:
            raise TaskValidationError(
                f"acceptance criterion {criterion_number} must have id "
                f"{expected_criterion_id!r}"
            )

    first_body_line = next((line for line in body if line.strip()), "")
    expected_heading = f"# Task {task_number}: {data['title']}"
    if first_body_line != expected_heading:
        raise TaskValidationError(f"first body heading must be {expected_heading!r}")

    return ValidatedTask(
        task_id=expected_task_id,
        plan_root=plan_root.resolve(),
        phase_dir=phase_dir.resolve(),
    )


def parse_index_frontmatter(lines: list[str]) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in lines:
        if not line.strip():
            continue
        match = TOP_LEVEL_RE.fullmatch(line)
        if not match or line.startswith(" "):
            raise TaskValidationError(f"unsupported frontmatter syntax: {line!r}")
        key, raw_value = match.groups()
        if key not in INDEX_REQUIRED_FIELDS:
            raise TaskValidationError(f"unexpected frontmatter field: {key}")
        if key in data:
            raise TaskValidationError(f"frontmatter field appears more than once: {key}")
        data[key] = parse_string(raw_value.strip(), key)
    missing = INDEX_REQUIRED_FIELDS - data.keys()
    if missing:
        raise TaskValidationError(f"missing frontmatter fields: {', '.join(sorted(missing))}")
    if data["kind"] not in {"group", "phase"}:
        raise TaskValidationError(f"kind must be \"group\" or \"phase\", found {data['kind']!r}")
    return data


def validate_index(index_path: Path, expected_kind: str) -> None:
    frontmatter, body = extract_frontmatter(index_path.read_text(encoding="utf-8"))
    data = parse_index_frontmatter(frontmatter)
    if data["kind"] != expected_kind:
        raise TaskValidationError(
            f"{index_path} has kind {data['kind']!r}, expected {expected_kind!r}"
        )

    if expected_kind == "group":
        expected_heading = f"# {data['name']}"
    else:
        phase_match = PHASE_DIR_RE.fullmatch(index_path.parent.name)
        if not phase_match:
            raise TaskValidationError(
                f"{index_path.parent} must be named phase-N to validate its index.md"
            )
        expected_heading = f"# Phase {int(phase_match.group(1))}: {data['name']}"

    first_body_line = next((line for line in body if line.strip()), "")
    if first_body_line != expected_heading:
        raise TaskValidationError(
            f"{index_path} first body heading must be {expected_heading!r}"
        )


def check_index_links(container: Path, index_path: Path) -> list[tuple[Path, str]]:
    errors: list[tuple[Path, str]] = []
    text = index_path.read_text(encoding="utf-8")
    for match in MARKDOWN_LINK_RE.finditer(text):
        target = match.group(1).strip()
        if not target.endswith(".md") or target.startswith(("http://", "https://", "#")):
            continue
        if not (container / target).resolve().is_file():
            errors.append(
                (container, f"index.md links to missing file {target!r}")
            )
    return errors


def check_plan_roots(plan_roots: set[Path]) -> list[tuple[Path, str]]:
    errors: list[tuple[Path, str]] = []
    for plan_root in sorted(plan_roots):
        index_path = plan_root / "index.md"
        if not index_path.is_file():
            errors.append((plan_root, "plan root is missing index.md"))
            continue
        try:
            validate_index(index_path, "group")
        except TaskValidationError as error:
            errors.append((plan_root, str(error)))
        errors.extend(check_index_links(plan_root, index_path))
    return errors


def check_phase_dirs(phase_dirs: set[Path]) -> list[tuple[Path, str]]:
    errors: list[tuple[Path, str]] = []
    for phase_dir in sorted(phase_dirs):
        index_path = phase_dir / "index.md"
        if not index_path.is_file():
            errors.append((phase_dir, "phase directory is missing index.md"))
            continue
        try:
            validate_index(index_path, "phase")
        except TaskValidationError as error:
            errors.append((phase_dir, str(error)))
        errors.extend(check_index_links(phase_dir, index_path))
    return errors


def collect_task_files(arguments: list[str]) -> list[Path]:
    files: list[Path] = []
    for argument in arguments:
        path = Path(argument)
        if path.is_dir():
            files.extend(sorted(path.rglob("task-*.md")))
        elif path.is_file():
            files.append(path)
        else:
            raise TaskValidationError(f"path does not exist: {path}")
    unique_files = list(dict.fromkeys(file.resolve() for file in files))
    if not unique_files:
        raise TaskValidationError("no task-N-short-name.md files found")
    return unique_files


def run(arguments: list[str]) -> int:
    """Validate every task file reachable from `arguments`.

    Each argument is a task file, a plan root, an epic root, or a portfolio
    root containing epic-* directories. Prints PASS/ERROR lines and a final
    summary, matching validate-tasks.py's original output exactly.
    """
    try:
        files = collect_task_files(arguments)
    except TaskValidationError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    failures = 0
    seen_ids: dict[tuple[Path, str], Path] = {}
    validated_plan_roots: set[Path] = set()
    validated_phase_dirs: set[Path] = set()
    for argument in arguments:
        argument_path = Path(argument)
        if argument_path.is_dir() and (argument_path / "index.md").is_file():
            validated_plan_roots.add(argument_path.resolve())
    for path in files:
        try:
            result = validate_task(path)
            key = (result.plan_root, result.task_id)
            if key in seen_ids:
                raise TaskValidationError(
                    f"duplicate id {result.task_id!r} within plan root "
                    f"{result.plan_root}; first found in {seen_ids[key]}"
                )
            seen_ids[key] = path
            validated_plan_roots.add(result.plan_root)
            validated_phase_dirs.add(result.phase_dir)
            print(f"PASS {path}")
        except (OSError, UnicodeError, TaskValidationError) as error:
            failures += 1
            print(f"ERROR {path}: {error}", file=sys.stderr)

    for plan_root, message in check_plan_roots(validated_plan_roots):
        failures += 1
        print(f"ERROR {plan_root}: {message}", file=sys.stderr)

    for phase_dir, message in check_phase_dirs(validated_phase_dirs):
        failures += 1
        print(f"ERROR {phase_dir}: {message}", file=sys.stderr)

    if failures:
        print(f"FAILED {failures} of {len(files)} task files", file=sys.stderr)
        return 1
    print(f"Validated {len(files)} task files")
    return 0
