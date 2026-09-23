---
name: egai-tasks-runner
description: Orchestrate execution of an egai-tasks-writing plan by walking its node tree of index.md files in one coordinator. A portfolio, an epic, and a phase are each a directory with its own index.md. Use when given a path to any such node, or to a single task file, plus optional additional instructions, and asked to run, continue, or drive that work to completion. Traverses child nodes in the current runner, invokes terminal egai-task-reader and egai-task-impl workers directly, and keeps every index.md checkbox current. Also use when asked to run a range of phases in Stacked Phase Mode, with one git worktree, branch, and pull request per phase, chained sequentially instead of one shared working tree. Also use when asked to run the work sandboxed, printing a fresh `srt`-wrapped CLI command instead of dispatching directly. Do not use to draft task plans or to implement a task's body directly.
metadata:
  version: "3.4.0"
---

# EGAI Tasks Runner

This skill runs one `egai-tasks-writing` plan by walking its node tree in the caller's runner. A portfolio, an epic, and a phase are all directories with their own `index.md` file. A task is a leaf file, not a directory. This skill keeps every `index.md` file current and dispatches only terminal reader and implementation workers. It delegates plan drafting to `egai-tasks-writing`. It delegates task-body implementation to `egai-task-impl`.

Read [references/tone.md](references/tone.md) before drafting. Apply its Kernel plus [Report tone](references/tone.md#report-tone-tone-contract) to every status update and report this skill produces.

## Terms

A **node** is a directory that holds one `index.md` file. That file lists the node's children, each with a checkbox. A node's children are either more nodes or task files. A node whose children are nodes is a **group**. A node whose children are task files is a **phase**. A **task** is one `task-N-*.md` file. `egai-tasks-writing` uses richer names for the same shapes. A portfolio is a group of epics. An epic is a group of phases.

## Input Contract

Accept the following input:

- One filesystem path: a node's directory, its `index.md` file, or a task file.
- Optional additional instructions, given as free text.

Resolve relative paths from the current workspace. Forward the additional instructions unchanged to every terminal worker this skill spawns.

## Classify the Path

Before dispatching, run `python3 SKILL_DIRECTORY/scripts/classify-path.py PATH`. Replace `SKILL_DIRECTORY` with the directory that contains this `SKILL.md`. The script prints one of `group`, `phase`, or `task`.

Stop and ask the user when it exits with an error instead of a kind. Do not guess the kind.

## Dispatch by Kind

Switch on the printed kind:

### Group

Read the node's `index.md` for its child list and any `Depends on` relationships between children.

- Before processing an eligible child, set that child's checkbox in this node's `index.md` to `[~]`.
- Classify and process that child in this same runner: descend into a child group, apply the Phase procedure to a child phase, or apply the Task procedure to a child task. Do not spawn an `egai-tasks-runner` sub-agent for any child.
- Process eligible children one at a time. After a child completes, set its checkbox to `[x]`; when it is blocked, restore `[ ]`. If a child is blocked, halt only children that depend on it, then continue with demonstrably independent children.

The serialized group traversal is intentional. A runner is a coordinator, not a background worker: a background runner that spawns its own background workers can be returned to its parent before those workers report. Task parallelism remains available inside a phase, where the single foreground coordinator waits for terminal task reports.

### Phase

Spawn one terminal `egai-task-reader` worker. Give it the phase's path and ask it, in plain language, for the phase's tasks grouped into ordered execution units. Wait for its report before proceeding. The report is an ordered list of units. Each unit is a list of task IDs and files to dispatch concurrently. Run the units in the order reported.

For each unit, in order:

- Before spawning, set that task's checkbox in this phase's `index.md` to `[~]`. See [Index.md Ownership](#indexmd-ownership).
- Spawn one terminal implementation worker per task in the unit. Spawn the workers concurrently for a parallel batch, or alone for a sequential task. Instruct each worker to invoke `egai-task-impl` on the task's path, forward the additional instructions, report its outcome without editing `index.md`, and never spawn another `egai-tasks-runner`.
- On each report, set that task's checkbox to `[x]` when every acceptance criterion is verified. Set it back to `[ ]` when any criterion is unproven.
- When a task is left unproven, apply `egai-task-impl`'s Incomplete Tasks rule. Record the blocker. Stop before any task that depends on it. Continue only with later tasks that are demonstrably independent.

### Task

If the task belongs to a phase that has an `index.md` file, set its checkbox to `[~]` before spawning.

Spawn one terminal implementation worker that invokes `egai-task-impl` on the task's path. Forward the additional instructions. Instruct the worker not to edit `index.md` and never to spawn another `egai-tasks-runner`. See [Index.md Ownership](#indexmd-ownership).

When an `index.md` file tracks the task, update its checkbox from the sub-agent's report, the same way as inside a phase. Otherwise, report the outcome without an index update.

## Stacked Phase Mode

Use this mode only when a caller requests it explicitly in the forwarded additional instructions, for example "run phases 3 through 10 in stacked phase mode." Never infer this mode from tree shape, repository state, or phase count.

This mode replaces normal Phase dispatch with an ordered range of phases. Each phase gets its own git worktree, branch, and pull request. The phases run in sequence, chained one after another, instead of sharing one working tree.

Once a caller requests this mode, read [references/stacked-phase-mode.md](references/stacked-phase-mode.md). It covers the range input, the per-phase procedure, and the reporting rules.

## Sandbox Mode

Use this mode only when a caller requests it explicitly in the forwarded additional instructions, for example "run this sandboxed." Never infer this mode from repository state, tree shape, or anything else.

Sandbox Mode and Stacked Phase Mode are independent. A caller can request either mode alone, or both together.

Check this once, at the top-level node the caller directly requested. A sub-agent that this skill spawns, for a child node, a stacked phase, or a task, never re-checks or re-triggers this itself.

Once triggered, read [references/sandbox-mode.md](references/sandbox-mode.md). It covers building the run's configuration, the preflight checks, and composing the command. Triggering this mode replaces normal dispatch entirely. It builds the configuration, prints the run command for a fresh sandboxed session, and stops. No Group, Phase, or Task dispatch happens in this invocation.

## Index.md Ownership

`egai-task-impl` normally edits a task's own checkbox as part of its workflow. This skill takes over that responsibility whenever it dispatches individual tasks or child nodes itself, so exactly one runner instance writes to any given `index.md` file.

- Tell every terminal worker to report its outcome and leave `index.md` untouched.
- Use the checkbox states from `egai-task-impl`'s Index Checkboxes section: `[ ]` for pending, `[~]` for in progress, `[x]` for done.
- The runner instance that dispatched a child is the only one that edits that child's checkbox. It edits that checkbox in the parent's own `index.md`, based on the child's report.

## Worker Topology

Keep one foreground `egai-tasks-runner` coordinator for an entire normal or stacked run. It may recurse through the plan logically, but it must never delegate that recursion to another runner agent.

- A coordinator may spawn `egai-task-reader` workers and `egai-task-impl` workers directly, then wait for every worker in a unit before changing state or returning a report.
- A reader or implementation worker is terminal for orchestration purposes. Do not ask it to run this skill, manage a phase, or spawn work on behalf of the coordinator.
- Never report a phase or group as complete, in progress, or blocked based only on a child runner handoff. Completion is determined from the terminal reader and implementation reports that the foreground coordinator received.

This topology avoids host products that force a background-aware coordinator to hand control back while its own background children remain active. When a host cannot wait for direct workers, run the affected reader or task implementation inline in the coordinator; preserve the same ordering and checkbox ownership.

## Reporting

After dispatch completes, or halts on a blocker, report the following:

- The paths and kinds visited.
- Each unit's final status.
- Unproven acceptance criteria with their task IDs.
- The current state of every touched `index.md`.
