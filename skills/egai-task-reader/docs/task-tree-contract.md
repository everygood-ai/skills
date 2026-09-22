# Task-tree contract

`egai-task-reader` is the mechanical reader and authoring-time validator for plans produced by `egai-tasks-writing`. It reads cards and indexes without loading task prose, then returns deterministic data for the other task-pipeline skills.

## Owned inputs and structure

- A plan root is a directory with a group `index.md`; an epic is another plan root nested below a portfolio; a phase is a `phase-N/` directory with a phase `index.md`.
- Group and phase indexes have exactly the `kind` and `name` frontmatter fields. `kind` is `group` or `phase`; the first body heading must match the name and phase number.
- A phase directly contains `task-N-short-name.md` files. Each card has exactly `id`, `title`, `phase`, `description`, `deliverable`, `acceptance_criteria`, and `parallel`. Criterion IDs are gapless `task-N-M` values.
- Index links must resolve. Plans may use a simple layout or an epic portfolio, but a plan root cannot mix direct phases with epic directories.

## `taskctl` interfaces

Run the bundled standard-library package with `python3 SKILL_DIRECTORY/scripts/taskctl COMMAND ARGS`.

- `ac TASK_FILE` returns criterion IDs and statements for implementation evidence.
- `card TASK_FILE` returns a complete validated card for internal phase processing.
- `phase-batch PHASE_DIR` returns JSON execution units: each `parallel: false` task is a unit, and each maximal consecutive run of `parallel: true` tasks is one unit.
- `phase-info PHASE_DIR` returns the phase number, name, slug, branch, and PR title.
- `pr-body PHASE_DIR BASE_BRANCH` returns the finished stacked-phase PR text.
- `validate TASK_FILE_OR_DIRECTORY...` checks cards, index structure, links, nesting, and duplicate IDs.

Malformed cards and lookup commands fail non-zero with an `error:` diagnostic. `validate` prints one `PASS` or `ERROR` line per file followed by a summary: `0` means success, `1` means a validation failure, and `2` means no task file resolved.

`ac` and `validate` are inline calls for the caller’s immediate context. `phase-batch`, `phase-info`, and `pr-body` are requested through a reader sub-agent when a caller is orchestrating other agents.

## Consumers and maintenance boundary

`egai-tasks-writing` hands completed plans to `validate`; `egai-task-impl` uses `ac` to verify one task; and `egai-tasks-runner` uses `phase-batch`, `phase-info`, and `pr-body` while scheduling phases. Keep parsing and validation rules in `scripts/taskctl`; do not copy them into consumers. The package tests in `scripts/taskctl/tests/` are the focused regression suite for these interfaces.
