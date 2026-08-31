# egai-task-reader

`egai-task-reader` reads and validates task-card YAML frontmatter and phase structure from an [egai-tasks-writing](../egai-tasks-writing/README.md) plan. It never loads a task's full prose body.

## Command Surface

One bundled tool, `taskctl`, backs every command.

| Command | Returns |
|---|---|
| `ac` | A task's acceptance-criterion IDs and statements. |
| `phase-batch` | A phase's tasks, grouped into ordered, parallel-safe execution units. |
| `phase-info` | A phase's branch name and PR title. |
| `pr-body` | A finished phase's PR title and body text. |
| `validate` | Pass/fail results for a plan's task cards and `index.md` files, checked against the schema. |
| `card` | A task's complete, validated frontmatter block. |

`card` is an internal building block. `phase-batch` reuses it to read each task in a phase. It stays a working subcommand, but no external caller invokes it directly.

See [SKILL.md](SKILL.md) for exact arguments, output formats, and exit codes.

## Invocation Shapes

This skill defines two ways to call it, chosen by whether the caller needs the answer directly in its own context.

**Inline call — `ac` and `validate`.** Call these directly from a caller's own script step, with no subagent round trip. Use this shape when the caller needs the result in its own context to make an immediate decision.

**Subagent dispatch — `phase-batch`, `phase-info`, `pr-body`.** Spawn a subagent instead, and ask it in plain language for what is needed. This skill's own `SKILL.md` then carries the script invocation and result-parsing detail that subagent needs.

## Task Pipeline

`egai-task-reader` is a shared dependency, not a stage in the task pipeline. [egai-tasks-writing](../egai-tasks-writing/README.md), [egai-task-impl](../egai-task-impl/README.md), and [egai-tasks-runner](../egai-tasks-runner/README.md) each call it for a different need: plan validation, criteria verification, and phase scheduling.

See [SKILL.md](SKILL.md) for the full command reference and both invocation shapes.
