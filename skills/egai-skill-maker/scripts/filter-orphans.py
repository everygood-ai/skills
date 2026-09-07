#!/usr/bin/env python3
"""Exempt dev-time-only files from skill-validator's orphan-resource warning.

Reads skill-validator's `-o json` output from stdin. An activated agent never
needs a runtime pointer to a skill's own test files, gaps.md, changelog.md,
or README.md, so a "potentially unreferenced file" warning naming one of
those is downgraded to informational instead of requiring SKILL.md to link
it. Prints a plain-text report and exits 0 (clean), 2 (warnings remain), or
1 (errors remain), matching skill-validator's own exit-code contract.
"""

from __future__ import annotations

import json
import sys


def is_exempt_orphan_file(file: str) -> bool:
    if file in {"changelog.md", "gaps.md", "README.md"}:
        return True
    parts = file.split("/")
    return len(parts) >= 2 and parts[0] == "scripts" and parts[-1].startswith("test_") and parts[-1].endswith(".py")


def is_orphan_warning(result: dict) -> bool:
    return (
        result.get("level") == "warning"
        and result.get("category") == "Structure"
        and str(result.get("message", "")).startswith("potentially unreferenced file:")
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
        if is_orphan_warning(result) and is_exempt_orphan_file(str(result.get("file", ""))):
            results.append(
                {
                    "level": "info",
                    "category": result.get("category", "Structure"),
                    "message": (
                        "exempted orphan warning (dev-time-only file, no runtime "
                        f"reference required): {result.get('file')}"
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
