#!/usr/bin/env python3
"""Classify a path from an egai-tasks-writing plan as a group, a phase, or a task."""

from __future__ import annotations

import re
import sys
from pathlib import Path


TASK_FILE_RE = re.compile(r"^task-[1-9]\d*-.+\.md$")
TOP_LEVEL_RE = re.compile(r"^([a-z_]+):\s*(.*)$")
INDEX_REQUIRED_FIELDS = {"kind", "name"}


class ClassifyError(ValueError):
    pass


def read_index_frontmatter(index_path: Path) -> list[str]:
    with index_path.open(encoding="utf-8") as index_file:
        first_line = index_file.readline().rstrip("\r\n")
        if first_line.strip() != "---":
            raise ClassifyError(f"{index_path} must start with frontmatter delimited by ---")
        lines: list[str] = []
        for raw_line in index_file:
            line = raw_line.rstrip("\r\n")
            if line.strip() == "---":
                if not lines:
                    raise ClassifyError(f"{index_path} frontmatter must not be empty")
                return lines
            lines.append(line)
    raise ClassifyError(f"{index_path} frontmatter is missing its closing --- delimiter")


def parse_index_frontmatter(index_path: Path, lines: list[str]) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in lines:
        if not line.strip():
            continue
        match = TOP_LEVEL_RE.fullmatch(line)
        if not match or line.startswith(" "):
            raise ClassifyError(f"{index_path}: unsupported frontmatter syntax: {line!r}")
        key, raw_value = match.groups()
        if key not in INDEX_REQUIRED_FIELDS:
            raise ClassifyError(f"{index_path}: unexpected frontmatter field: {key}")
        if key in data:
            raise ClassifyError(f"{index_path}: frontmatter field appears more than once: {key}")
        raw_value = raw_value.strip()
        if not raw_value.startswith('"') or not raw_value.endswith('"'):
            raise ClassifyError(f"{index_path}: {key} must be a double-quoted string")
        data[key] = raw_value[1:-1]
    missing = INDEX_REQUIRED_FIELDS - data.keys()
    if missing:
        raise ClassifyError(f"{index_path}: missing fields: {', '.join(sorted(missing))}")
    if data["kind"] not in {"group", "phase"}:
        raise ClassifyError(
            f"{index_path}: kind must be \"group\" or \"phase\", found {data['kind']!r}"
        )
    return data


def classify(path: Path) -> str:
    if not path.exists():
        raise ClassifyError(f"path does not exist: {path}")

    if path.is_file():
        if path.name == "index.md":
            return classify(path.parent)
        if TASK_FILE_RE.fullmatch(path.name):
            return "task"
        raise ClassifyError(f"file is not index.md or a task-N-*.md file: {path}")

    index_path = path / "index.md"
    if not index_path.is_file():
        raise ClassifyError(f"directory has no index.md: {path}")

    lines = read_index_frontmatter(index_path)
    data = parse_index_frontmatter(index_path, lines)
    return data["kind"]


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: classify-path.py PATH", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    try:
        kind = classify(path)
    except ClassifyError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(kind)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
