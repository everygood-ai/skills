"""Read phase structure: index.md metadata, task-file discovery, PR body, and
grouping a phase's tasks into ordered sequential/parallel execution units.
"""

from __future__ import annotations

import re
from pathlib import Path

from .cards import TOP_LEVEL_RE, TaskCardError, parse_card, parse_string, read_card


TASK_FILENAME_RE = re.compile(r"^task-([1-9]\d*)-.+\.md$")
SLUG_RUN_RE = re.compile(r"[^a-z0-9]+")
INDEX_REQUIRED_FIELDS = {"kind", "name"}
PHASE_DIR_RE = re.compile(r"^phase-([1-9]\d*)$")


def slugify(name: str) -> str:
    slug = SLUG_RUN_RE.sub("-", name.lower()).strip("-")
    if not slug:
        raise TaskCardError(f"phase name has no alphanumeric characters to slugify: {name!r}")
    return slug


def read_index_frontmatter(index_path: Path) -> list[str]:
    with index_path.open(encoding="utf-8") as index_file:
        first_line = index_file.readline().rstrip("\r\n")
        if first_line.strip() != "---":
            raise TaskCardError("index file must start with frontmatter delimited by ---")
        card_lines: list[str] = []
        for raw_line in index_file:
            line = raw_line.rstrip("\r\n")
            if line.strip() == "---":
                if not card_lines:
                    raise TaskCardError("index frontmatter must not be empty")
                return card_lines
            card_lines.append(line)
    raise TaskCardError("index frontmatter is missing its closing --- delimiter")


def parse_index_frontmatter(lines: list[str]) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in lines:
        if not line.strip():
            continue
        match = TOP_LEVEL_RE.fullmatch(line)
        if not match or line.startswith(" "):
            raise TaskCardError(f"unsupported frontmatter syntax: {line!r}")
        key, raw_value = match.groups()
        if key not in INDEX_REQUIRED_FIELDS:
            raise TaskCardError(f"unexpected frontmatter field: {key}")
        if key in data:
            raise TaskCardError(f"frontmatter field appears more than once: {key}")
        value = parse_string(raw_value.strip(), key)
        if key == "kind" and value not in {"group", "phase"}:
            raise TaskCardError(f'kind must be "group" or "phase", found {value!r}')
        data[key] = value
    missing = INDEX_REQUIRED_FIELDS - data.keys()
    if missing:
        raise TaskCardError(f"missing fields: {', '.join(sorted(missing))}")
    return data


def phase_info(phase_dir: Path) -> dict[str, str]:
    index_path = phase_dir / "index.md"
    lines = read_index_frontmatter(index_path)
    data = parse_index_frontmatter(lines)
    if data["kind"] != "phase":
        raise TaskCardError(f"{index_path} has kind {data['kind']!r}, expected 'phase'")
    match = PHASE_DIR_RE.fullmatch(phase_dir.name)
    if not match:
        raise TaskCardError(f"phase directory name must match phase-N: {phase_dir.name!r}")
    number = int(match.group(1))
    name = data["name"]
    slug = slugify(name)
    return {
        "number": str(number),
        "name": name,
        "slug": slug,
        "branch": f"feature/phase-{number}-{slug}",
        "pr_title": f"Phase {number}: {name}",
    }


def phase_task_files(phase_dir: Path) -> list[Path]:
    candidates = [
        entry for entry in phase_dir.iterdir()
        if entry.is_file() and TASK_FILENAME_RE.fullmatch(entry.name)
    ]
    if not candidates:
        raise TaskCardError(f"no task-N-*.md files found in phase directory: {phase_dir}")
    return sorted(candidates, key=lambda entry: int(TASK_FILENAME_RE.fullmatch(entry.name).group(1)))


def pr_body(phase_dir: Path, base_branch: str) -> str:
    info = phase_info(phase_dir)
    bullets: list[str] = []
    total_criteria = 0
    for task_path in phase_task_files(phase_dir):
        _, card_lines = read_card(task_path)
        data = parse_card(card_lines)
        criteria = data["acceptance_criteria"]
        assert isinstance(criteria, list)
        total_criteria += len(criteria)
        bullets.append(f"- **{data['title']}** — {data['description']} {data['deliverable']}")

    lines = [info["pr_title"], "", f"Stacked on `{base_branch}`.", "", *bullets, ""]
    lines.append(
        f"{total_criteria} acceptance criteria verified across {len(bullets)} tasks."
    )
    return "\n".join(lines)


def phase_batch(phase_dir: Path) -> dict[str, list[list[dict[str, str]]]]:
    """Group a phase's task cards into ordered execution units.

    A `parallel: false` task is its own one-task unit. A maximal consecutive
    run of `parallel: true` tasks is one unit that may run concurrently.
    """
    units: list[list[dict[str, str]]] = []
    pending_parallel_unit: list[dict[str, str]] = []
    for task_path in phase_task_files(phase_dir):
        _, card_lines = read_card(task_path)
        data = parse_card(card_lines)
        task_id = data["id"]
        assert isinstance(task_id, str)
        entry = {"id": task_id, "file": task_path.name}
        if data["parallel"]:
            pending_parallel_unit.append(entry)
            continue
        if pending_parallel_unit:
            units.append(pending_parallel_unit)
            pending_parallel_unit = []
        units.append([entry])
    if pending_parallel_unit:
        units.append(pending_parallel_unit)
    return {"units": units}
