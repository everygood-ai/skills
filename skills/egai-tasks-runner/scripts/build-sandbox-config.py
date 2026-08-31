#!/usr/bin/env python3
"""Copy the shipped srt (sandbox-runtime) baseline settings into a project-local generated file."""

from __future__ import annotations

import json
import sys
from pathlib import Path


BASELINE_PATH = Path(__file__).resolve().parent.parent / "assets" / "srt-settings.baseline.json"
OUTPUT_FILENAME = ".srt-settings.generated.json"


class BuildSandboxConfigError(ValueError):
    pass


def load_baseline() -> dict[str, object]:
    if not BASELINE_PATH.is_file():
        raise BuildSandboxConfigError(f"baseline settings file not found: {BASELINE_PATH}")
    with BASELINE_PATH.open(encoding="utf-8") as baseline_file:
        return json.load(baseline_file)


def main() -> int:
    if len(sys.argv) > 2:
        print("usage: build-sandbox-config.py [PROJECT_ROOT]", file=sys.stderr)
        return 2
    project_root = Path(sys.argv[1]) if len(sys.argv) == 2 else Path.cwd()

    try:
        baseline = load_baseline()
    except (OSError, ValueError, BuildSandboxConfigError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    if not project_root.is_dir():
        print(f"error: project root does not exist: {project_root}", file=sys.stderr)
        return 1

    output_path = project_root / OUTPUT_FILENAME
    with output_path.open("w", encoding="utf-8") as output_file:
        json.dump(baseline, output_file, indent=2)
        output_file.write("\n")

    print(
        "wrote a straight copy of the baseline — no project inspection is done; "
        "add any domains or paths this project's tasks need before running sandboxed",
        file=sys.stderr,
    )
    print(str(output_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
