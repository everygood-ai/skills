# Plan orchestration model

`egai-tasks-runner` executes a validated `egai-tasks-writing` tree. One foreground coordinator owns logical recursion and checkbox state, delegates card reading to terminal `egai-task-reader` workers, and delegates task bodies to terminal `egai-task-impl` workers.

## Path and dispatch ownership

The input is one group directory/index, phase directory/index, or task file plus optional instructions. Resolve relative paths from the workspace and forward the instructions unchanged to every child agent.

- A group reads its `index.md`, marks an eligible child `[~]`, and processes that child in the same coordinator. It serializes children, marks `[x]` on success or `[ ]` on a blocker, and stops only children that depend on a blocked child.
- A phase asks a direct, terminal `egai-task-reader` worker for `phase-batch`. It dispatches each reported unit in order, concurrently within a `parallel: true` unit. Before dispatch, it marks each task `[~]`; after terminal reports, it marks `[x]` only when all criteria are proven and otherwise `[ ]`.
- A task is dispatched to one direct, terminal `egai-task-impl` worker. The coordinator owns the checkbox whenever it dispatches, so the implementation worker must not edit `index.md`.

The runner tree is logical, not an agent tree. A background-aware coordinator may be forced to return before its own background children report; therefore a runner never spawns another runner. Only the foreground coordinator spawns terminal workers and waits for every report before it mutates state or returns. If a host cannot wait for a direct worker, run that worker's action inline instead of introducing a nested coordinator.

Every dispatch report includes visited paths and kinds, each unit’s final status, unproven criterion IDs, and the current state of touched indexes. A blocker stops only work that depends on it, except a blocked task stops later dependent tasks in its phase.

## Explicit run modes

Stacked Phase Mode is enabled only by an explicit caller request. The requested start must classify as a phase. Resolve sibling phases in order with `scripts/phase-range.py`; gaps from deleted phases are skipped, malformed phase-like directory names fail, and a `--count` range caps at the available siblings. The same foreground coordinator gives each phase a worktree and branch chained from the previous phase, commits after completed units, then pushes or opens a PR when available before its worktree is removed. Direct terminal `egai-task-reader` workers supply branch/PR metadata and the finished PR body; direct terminal implementation workers receive the worktree path. A blocked phase halts the remainder of the range.

Sandbox Mode is also explicit and replaces dispatch entirely. `scripts/build-sandbox-config.py` copies `assets/srt-settings.baseline.json` to the project’s `.srt-settings.generated.json` without inspecting the project. The runner checks `srt` and the generated file, prints interactive and headless commands, and stops. Users must add project-specific domains or sockets before running; a blocked-domain retry edits the generated file and reruns the printed command directly.

## Script boundary

Run scripts from the package containing `SKILL.md`:

- `scripts/classify-path.py PATH` returns `group`, `phase`, or `task` from path shape and index frontmatter, failing on missing or malformed inputs.
- `scripts/phase-range.py START --count N` or `START --end END` returns an ordered sibling-phase range for stacked mode.
- `scripts/build-sandbox-config.py [PROJECT_ROOT]` materializes the baseline sandbox settings file.

Their focused tests are `scripts/test_classify_path.py`, `scripts/test_phase_range.py`, `scripts/test_build_sandbox_config.py`, and `scripts/test_sandbox_e2e.py`.
