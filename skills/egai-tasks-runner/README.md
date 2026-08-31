# egai-tasks-runner

Orchestrates execution of an [egai-tasks-writing](../egai-tasks-writing/README.md) plan by walking its node tree. A portfolio, an epic, and a phase are each a directory with its own `index.md`; a task is a leaf file. The skill dispatches one sub-agent per node, invokes [egai-task-impl](../egai-task-impl/README.md) once per task, and keeps every `index.md` checkbox current.

## Input

The input is a single filesystem path: a node's directory, its `index.md` file, or a task file, plus optional free-text instructions. The skill resolves relative paths from the current workspace and forwards the instructions, unchanged, to every sub-agent it spawns at every recursion level.

## Task Pipeline

`egai-tasks-runner` is the middle stage of the task pipeline. It walks the tree [egai-tasks-writing](../egai-tasks-writing/README.md) authored and dispatches sub-agents down that tree, calling [egai-task-impl](../egai-task-impl/README.md) once per task. Exactly one runner instance writes to any given `index.md`: the instance that dispatched a child owns that child's checkbox in the parent's `index.md`.

Phase dispatch also depends on [egai-task-reader](../egai-task-reader/README.md), which groups a phase's tasks into ordered execution units before dispatch. The skill reaches it through a sub-agent dispatch, the same way it reaches `egai-task-impl`.

## Run Modes

Two run modes change how the skill dispatches, both triggered only by an explicit caller request, never inferred from repo state or tree shape.

**Stacked Phase Mode** runs an ordered range of phases, each in its own git worktree, branch, and pull request, chained sequentially instead of sharing one working tree. Each phase's loop also dispatches an `egai-task-reader` sub-agent for the phase's branch name and PR title before work starts. It dispatches another `egai-task-reader` sub-agent for the finished PR body once the phase's tasks are done. See [references/stacked-phase-mode.md](references/stacked-phase-mode.md) for the full procedure.

**Sandbox Mode** runs the requested work inside an `srt` (sandbox-runtime) session instead of dispatching sub-agents directly. Once triggered, it replaces normal dispatch entirely: it builds a per-run `srt` config, then prints an `srt --settings <path> <agent-cli> "<prompt>"` command for a fresh sandboxed session and stops. The skill never executes that sandboxed session itself; running the printed command is left to the caller.

The `srt` config comes from two files:

| File | Role |
|---|---|
| `assets/srt-settings.baseline.json` | The fixed baseline filesystem and network config, shipped with this skill. Never used directly as the `srt` target. |
| `.srt-settings.generated.json` | The per-run config, a straight copy of the baseline written to the project root. No project inspection happens. |

The generated config is a best-effort default: a plain copy of the baseline, not a per-project one. It has no package-registry domains, no third-party API domains, and nothing else specific to the project's actual needs; adding those to `.srt-settings.generated.json` before running is the user's responsibility. If a sandboxed run fails partway through on a blocked domain, add that domain to the generated file and re-run the printed `srt` command directly — re-triggering Sandbox Mode instead would regenerate the file from the baseline and discard the edit. See [references/sandbox-mode.md](references/sandbox-mode.md) for the full procedure, including the preflight checks and the reminder text printed alongside the command.

See [SKILL.md](SKILL.md) for the full workflow, the group/phase/task dispatch rules, and the `index.md` ownership rules.
