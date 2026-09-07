#!/usr/bin/env python3
"""Validate changelog.md bullet structure and length without third-party dependencies."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


MAX_WORDS = 50
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
TOP_BULLET_RE = re.compile(r"^- `(?P<version>[^`]+)`(?P<rest>.*)$")
SUB_BULLET_RE = re.compile(r"^(?P<indent>\s+)- (?P<text>.+)$")
FLAT_SEPARATOR_RE = re.compile(r"^\s*—\s*(?P<text>.+)$")


class ChangelogError(ValueError):
    pass


@dataclass(frozen=True)
class VersionEntry:
    version: str
    bullets: tuple[str, ...]
    line_number: int


def word_count(text: str) -> int:
    return len(text.split())


def parse_changelog(text: str) -> list[VersionEntry]:
    lines = text.splitlines()
    entries: list[VersionEntry] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        top_match = TOP_BULLET_RE.match(line)
        if not top_match:
            index += 1
            continue

        version = top_match.group("version")
        if not VERSION_RE.fullmatch(version):
            raise ChangelogError(
                f"line {index + 1}: {version!r} is not a MAJOR.MINOR.PATCH version"
            )

        rest = top_match.group("rest")
        flat_match = FLAT_SEPARATOR_RE.match(rest)
        line_number = index + 1
        index += 1

        if flat_match:
            entries.append(
                VersionEntry(version, (flat_match.group("text").strip(),), line_number)
            )
            continue

        if rest.strip():
            raise ChangelogError(
                f"line {line_number}: version `{version}` must be followed by "
                "an em dash (—) and a summary, or by nothing and an "
                "indented bullet list"
            )

        sub_bullets: list[str] = []
        while index < len(lines):
            sub_match = SUB_BULLET_RE.match(lines[index])
            if not sub_match:
                break
            sub_bullets.append(sub_match.group("text").strip())
            index += 1

        if not sub_bullets:
            raise ChangelogError(
                f"line {line_number}: version `{version}` has no summary bullet "
                "and no indented bullet list"
            )
        entries.append(VersionEntry(version, tuple(sub_bullets), line_number))

    if not entries:
        raise ChangelogError("no version entries found (expected lines like '- `1.0.0` ...')")
    return entries


def check_entries(entries: list[VersionEntry]) -> list[str]:
    errors: list[str] = []
    seen_versions: dict[str, int] = {}
    for entry in entries:
        if entry.version in seen_versions:
            errors.append(
                f"line {entry.line_number}: version `{entry.version}` duplicates the "
                f"entry at line {seen_versions[entry.version]}"
            )
        else:
            seen_versions[entry.version] = entry.line_number

        for bullet in entry.bullets:
            if not bullet:
                errors.append(
                    f"version `{entry.version}` (line {entry.line_number}): "
                    "bullet text is empty"
                )
                continue
            count = word_count(bullet)
            if count > MAX_WORDS:
                errors.append(
                    f"version `{entry.version}` (line {entry.line_number}): bullet has "
                    f"{count} words, exceeding the {MAX_WORDS}-word limit: {bullet!r}"
                )
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_changelog.py CHANGELOG_PATH", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"error: not a file: {path}", file=sys.stderr)
        return 2

    try:
        entries = parse_changelog(path.read_text(encoding="utf-8"))
    except ChangelogError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    errors = check_entries(entries)
    for error in errors:
        print(f"ERROR {path}: {error}", file=sys.stderr)

    if errors:
        print(f"FAILED {len(errors)} issue(s) across {len(entries)} version(s)", file=sys.stderr)
        return 1

    print(f"Validated {len(entries)} version(s) in {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
