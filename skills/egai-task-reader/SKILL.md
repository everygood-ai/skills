---
name: egai-task-reader
description: Read and validate task-card YAML frontmatter and phase structure from an egai-tasks-writing plan, without loading a task's full prose body. Use when a caller needs a task's acceptance criteria, a phase's branch/PR metadata, a phase's tasks grouped into ordered execution units, a phase's PR body, or full authoring-time validation of a plan's task cards and index.md files, sourced from task-N-*.md files and a phase's index.md. Do not use to draft task plans, implement a task's body, or orchestrate dispatch.
metadata:
  version: "1.1.1"
---

# EGAI Task Reader

This skill's own output is terse per `egai-write-tone`.

`egai-task-reader` parses and validates `egai-tasks-writing`'s task-card and phase-structure format, without loading a task's full body.

All commands run through one bundled tool:

```text
python3 SKILL_DIRECTORY/scripts/taskctl COMMAND ARGS
```

Replace `SKILL_DIRECTORY` with the directory containing this `SKILL.md`. `taskctl` is a Python package that uses only the standard library. Invoking its directory runs its `__main__.py`.

## Command Surface

| Command | Args | Output |
|---|---|---|
| `ac` | `TASK_FILE` | Acceptance-criterion IDs and statements, one per line |
| `phase-batch` | `PHASE_DIR` | JSON: the phase's tasks grouped into ordered execution units |
| `phase-info` | `PHASE_DIR` | `key: value` lines: `number`, `name`, `slug`, `branch`, `pr_title` |
| `pr-body` | `PHASE_DIR BASE_BRANCH` | Finished PR title and body text |
| `card` | `TASK_FILE` | A task's complete, validated frontmatter block |
| `validate` | `TASK_FILE_OR_DIRECTORY [...]` | `PASS`/`ERROR` lines per file plus a summary line |

A malformed card or a missing file fails loudly. The command prints `error: PATH: MESSAGE` to stderr and exits non-zero. An unrecognized command prints a usage line to stderr and exits `2`. `validate` reports differently: see [Validate](#validate).

`card` is an internal building block. `phase-batch` reuses it to read each task. It stays a working subcommand, covered by tests, but no caller invokes it directly. Use `ac`, `phase-batch`, `phase-info`, `pr-body`, or `validate` instead.

## Validate

`validate` checks a plan's task cards and phase structure at authoring time:

- Frontmatter schema conformance.
- Filename, heading, and id consistency.
- Phase-directory nesting and epic-directory rules.
- `index.md` `kind` and heading validation.
- `index.md` link-target existence.
- Duplicate-ID detection across a plan root.

```text
python3 SKILL_DIRECTORY/scripts/taskctl validate TASK_FILE_OR_DIRECTORY [...]
```

Each `TASK_FILE_OR_DIRECTORY` is a task file, a plan root, an epic root, or a portfolio root containing `epic-*` directories. `validate` prints one `PASS PATH` or `ERROR PATH: MESSAGE` line per file, to stdout or stderr respectively. It then prints a summary line: `Validated N task files` on success, or `FAILED N of M task files` to stderr on failure.

Exit codes:

- `0`: every file passed.
- `1`: a file or a structural check failed.
- `2`: no argument resolved to a task file.

## Two Invocation Shapes

Choose the shape by whether the answer must land directly in the caller's own context, or the caller is orchestrating other subagents.

### Inline call — `ac` and `validate`

Call `ac` or `validate` directly from a caller's own script step, with no subagent round trip. Use this shape when the caller needs the result in its own context to make an immediate decision.

```text
python3 SKILL_DIRECTORY/scripts/taskctl ac TASK_FILE
python3 SKILL_DIRECTORY/scripts/taskctl validate TASK_FILE_OR_DIRECTORY [...]
```

### Subagent dispatch — `phase-batch`, `phase-info`, `pr-body`

Reach these three through a spawned subagent, not an inline call. The caller tells the subagent, in plain language, to load `egai-task-reader` and produce what it needs. For example: "load egai-task-reader and get the execution units for this phase." This `SKILL.md` then tells that subagent which script and flags to run, and how to read the result.

- **Ordered and parallel execution units.** Run `phase-batch PHASE_DIR`. Parse the JSON:

  ```json
  {"units": [[{"id": "task-1", "file": "task-1-short-name.md"}], [{"id": "task-2", "file": "..."}, {"id": "task-3", "file": "..."}]]}
  ```

  Each inner array is one ordered execution unit. Dispatch every task in one unit concurrently, wait for the whole unit, then start the next unit. A unit of size 1 simply runs alone. Grouping rule: a `parallel: false` task is its own one-task unit. A maximal consecutive run of `parallel: true` tasks is one unit.
- **Phase branch and PR metadata.** Run `phase-info PHASE_DIR` for a phase's branch name and PR title. Parse the `key: value` lines.
- **Finished PR body.** Run `pr-body PHASE_DIR BASE_BRANCH` once every task in the phase is done. Print its stdout directly as the PR body.

## Failure Handling

Treat a non-zero exit as a hard stop for that command's caller. Do not guess a task's schedule, criteria, or PR content from a partial or malformed result. Surface the stderr `error: ...` line verbatim in the caller's own report. `validate` has no single `error: ...` line. Surface its `ERROR` and `FAILED` lines instead.

Read [the taskctl tests](scripts/taskctl/tests/test_cards.py), [scripts/taskctl/tests/test_phase.py](scripts/taskctl/tests/test_phase.py), and [scripts/taskctl/tests/test_validate.py](scripts/taskctl/tests/test_validate.py) only when maintaining `taskctl` itself. Run them with `python3 scripts/taskctl/tests/test_cards.py`, `python3 scripts/taskctl/tests/test_phase.py`, and `python3 scripts/taskctl/tests/test_validate.py` from this skill's directory.

Read [the changelog](changelog.md) only when reviewing this skill's version history or preparing a revision.
