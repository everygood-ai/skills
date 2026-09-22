#!/usr/bin/env python3
"""Copy this public skill's pinned tone rules into one portable skill.

The public egai-skill-maker package is deliberately self-contained. This
script reads its compiled references/tone.md rather than this repository's
source compiler, capability bundles, or legacy tone-contract manifest.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


PROFILE_HEADINGS = {
    "prose": "## Prose tone `[tone-contract]`",
    "terse": "## Terse tone `[tone-contract]`",
    "compact": "## Compact tone `[tone-contract]`",
    "terse-report": "## Terse report tone `[tone-contract]`",
}
KERNEL_HEADING = "## Kernel `[tone-contract]`"
HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*$")


class ToneInjectionError(ValueError):
    pass


def _heading_parts(line: str) -> tuple[int, str] | None:
    match = HEADING_RE.match(line.rstrip("\r\n"))
    if match is None:
        return None
    return len(match.group(1)), match.group(2).strip()


def section(text: str, heading: str) -> str:
    """Return the exact body of one unique Markdown section."""
    wanted = _heading_parts(heading)
    if wanted is None:
        raise ToneInjectionError(f"invalid bundled heading: {heading!r}")
    wanted_level, wanted_title = wanted
    lines = text.splitlines(keepends=True)
    matches = [
        index
        for index, line in enumerate(lines)
        if _heading_parts(line) == (wanted_level, wanted_title)
    ]
    if len(matches) != 1:
        raise ToneInjectionError(
            f"bundled tone reference must contain exactly one {heading!r}; found {len(matches)}"
        )
    start = matches[0] + 1
    end = len(lines)
    for index in range(start, len(lines)):
        parsed = _heading_parts(lines[index])
        if parsed is not None and parsed[0] <= wanted_level:
            end = index
            break
    body = "".join(lines[start:end])
    if not body.strip():
        raise ToneInjectionError(f"bundled tone reference has an empty {heading!r} section")
    return body


def render(reference: str, profile: str, heading: str) -> str:
    if not heading.startswith("## "):
        raise ToneInjectionError("--heading must begin with '## '")
    if "\n" in heading or "\r" in heading:
        raise ToneInjectionError("--heading must be one line")
    kernel = section(reference, KERNEL_HEADING)
    profile_text = section(reference, PROFILE_HEADINGS[profile])
    return (
        "# Tone Guidance\n\n## Kernel\n"
        + kernel.rstrip()
        + "\n\n"
        + heading
        + "\n"
        + profile_text.rstrip()
        + "\n"
    )


def inject(skill_dir: Path, profile: str, heading: str, replace: bool) -> Path:
    if not skill_dir.is_dir():
        raise ToneInjectionError(f"skill directory is not a directory: {skill_dir}")
    if not (skill_dir / "SKILL.md").is_file():
        raise ToneInjectionError(f"skill directory has no SKILL.md: {skill_dir}")
    package_root = Path(__file__).resolve().parent.parent
    reference_path = package_root / "references" / "tone.md"
    try:
        reference = reference_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ToneInjectionError(f"cannot read bundled tone reference: {reference_path}") from exc
    target = skill_dir / "references" / "tone.md"
    if target.exists() and not replace:
        raise ToneInjectionError(f"refusing to replace existing file: {target}; pass --replace")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render(reference, profile, heading), encoding="utf-8")
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_directory", type=Path)
    parser.add_argument("--profile", choices=sorted(PROFILE_HEADINGS), required=True)
    parser.add_argument("--heading", required=True)
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args(argv)
    try:
        target = inject(args.skill_directory, args.profile, args.heading, args.replace)
    except ToneInjectionError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
