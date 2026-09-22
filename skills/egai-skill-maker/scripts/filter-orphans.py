#!/usr/bin/env python3
"""Exempt dev-time-only files from skill-validator structure warnings.

Reads skill-validator's `-o json` output from stdin. An activated agent never
needs a runtime pointer to a skill's own test files, gaps.md, changelog.md,
README.md, or maintainer Markdown under docs/, so a "potentially unreferenced
file" warning naming one of those is downgraded to informational instead of
requiring SKILL.md to link it. Prints a plain-text report and exits 0 (clean),
2 (warnings remain), or 1 (errors remain), matching skill-validator's own
exit-code contract. The same rule downgrades the validator's unknown-directory
warning for the maintainer-only docs/ directory.
"""

from __future__ import annotations

import json
import sys


def is_exempt_orphan_file(file: str) -> bool:
    if file in {"changelog.md", "gaps.md", "README.md"}:
        return True
    parts = file.split("/")
    if len(parts) >= 2 and parts[0] == "docs" and parts[-1].endswith(".md"):
        return True
    return len(parts) >= 2 and parts[0] == "scripts" and parts[-1].startswith("test_") and parts[-1].endswith(".py")


def is_orphan_warning(result: dict) -> bool:
    return (
        result.get("level") == "warning"
        and result.get("category") == "Structure"
        and str(result.get("message", "")).startswith("potentially unreferenced file:")
    )


def is_docs_directory_warning(result: dict) -> bool:
    return (
        result.get("level") == "warning"
        and result.get("category") == "Structure"
        and str(result.get("message", "")).startswith("unknown directory: docs/")
    )


def main() -> int:
    raw = sys.stdin.read()
    try:
        report = json.loads(raw)
    except json.JSONDecodeError:
        sys.stdout.write(raw)
        return 3

    results = []
    for result in report.get("results", []):
        exempt_orphan = is_orphan_warning(result) and is_exempt_orphan_file(
            str(result.get("file", ""))
        )
        exempt_docs_directory = is_docs_directory_warning(result)
        if exempt_orphan or exempt_docs_directory:
            results.append(
                {
                    "level": "info",
                    "category": result.get("category", "Structure"),
                    "message": (
                        "exempted validator warning (maintainer docs are dev-time-only; "
                        f"no runtime reference required): {result.get('file') or result.get('message')}"
                    ),
                }
            )
        else:
            results.append(result)

    for result in results:
        level = str(result.get("level", "info")).upper()
        print(f"{level:7} {result.get('message', '')}")

    errors = sum(1 for result in results if result.get("level") == "error")
    warnings = sum(1 for result in results if result.get("level") == "warning")
    status = "passed" if errors == 0 else "failed"
    print(f"\nResult: {status}, {errors} error(s), {warnings} warning(s)")

    if errors:
        return 1
    if warnings:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
