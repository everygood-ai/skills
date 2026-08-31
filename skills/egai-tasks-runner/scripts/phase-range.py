#!/usr/bin/env python3
"""List the ordered sequence of sibling phase directories for a stacked run."""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path


PHASE_DIR_RE = re.compile(r"^phase-([1-9]\d*)$")
PHASE_LOOSE_RE = re.compile(r"(?i)^phase[-_]?\d")


class PhaseRangeError(ValueError):
    pass


def load_classify_path():
    module_path = Path(__file__).resolve().parent / "classify-path.py"
    spec = importlib.util.spec_from_file_location("classify_path", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalize_phase_path(path: Path) -> Path:
    return path.parent if path.name == "index.md" else path


def require_phase(classify_path, phase_dir: Path) -> None:
    try:
        kind = classify_path.classify(phase_dir)
    except classify_path.ClassifyError as error:
        raise PhaseRangeError(str(error)) from error
    if kind != "phase":
        raise PhaseRangeError(f"not a phase: {phase_dir} (classified as {kind})")


def sibling_phases(parent: Path) -> list[Path]:
    """List this parent's phase-N subdirectories in numeric order.

    Ordered by position, not by arithmetic on N: a phase deleted after
    task-writing simply leaves a gap in the numbering, and the next phase
    in sequence is whichever phase-N directory actually exists next.

    Fails loudly, for the whole parent, the moment it finds a directory
    that looks like an attempted phase name but does not match phase-N
    exactly (wrong case, a leading zero, a separator other than -, or a
    trailing slug) — such a directory would otherwise sort invisibly out
    of every range instead of raising anything.
    """
    valid: list[Path] = []
    for entry in sorted(parent.iterdir()):
        if not entry.is_dir():
            continue
        if PHASE_DIR_RE.fullmatch(entry.name):
            valid.append(entry)
        elif PHASE_LOOSE_RE.match(entry.name):
            raise PhaseRangeError(
                f"incompatible phase directory name {entry.name!r} under {parent}; "
                "expected phase-N, N a positive integer with no leading zero"
            )
    return sorted(valid, key=lambda entry: int(PHASE_DIR_RE.fullmatch(entry.name).group(1)))


def phase_index(siblings: list[Path], target: Path, parent: Path) -> int:
    resolved = target.resolve()
    for index, sibling in enumerate(siblings):
        if sibling.resolve() == resolved:
            return index
    raise PhaseRangeError(f"{target} is not a phase-N directory under {parent}")


def phase_range(classify_path, start: Path, end: Path) -> list[Path]:
    require_phase(classify_path, start)
    parent = start.parent
    siblings = sibling_phases(parent)
    start_index = phase_index(siblings, start, parent)
    end_index = phase_index(siblings, end, parent)
    if end_index < start_index:
        raise PhaseRangeError(f"end phase {end} comes before start phase {start}")
    phases = siblings[start_index : end_index + 1]
    for phase in phases:
        require_phase(classify_path, phase)
    return phases


def main() -> int:
    if len(sys.argv) != 4 or sys.argv[2] not in {"--count", "--end"}:
        print(
            "usage: phase-range.py START_PHASE_DIR --count N | "
            "phase-range.py START_PHASE_DIR --end END_PHASE_DIR",
            file=sys.stderr,
        )
        return 2

    start = normalize_phase_path(Path(sys.argv[1]))
    classify_path = load_classify_path()
    capped_from: int | None = None
    try:
        require_phase(classify_path, start)
        siblings = sibling_phases(start.parent)
        start_index = phase_index(siblings, start, start.parent)
        if sys.argv[2] == "--count":
            if not re.fullmatch(r"[1-9]\d*", sys.argv[3]):
                raise PhaseRangeError("--count must be a positive integer")
            count = int(sys.argv[3])
            last_index = min(start_index + count - 1, len(siblings) - 1)
            if start_index + count - 1 > last_index:
                capped_from = count
            end = siblings[last_index]
        else:
            end = normalize_phase_path(Path(sys.argv[3]))
        phases = phase_range(classify_path, start, end)
    except (OSError, UnicodeError, PhaseRangeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    for phase in phases:
        print(phase)
    if capped_from is not None:
        print(
            f"note: requested {capped_from} phases from {start}, but only "
            f"{len(phases)} exist under {start.parent}; capped to {len(phases)}. "
            "A stacked range never crosses into a sibling group.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
