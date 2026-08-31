---
name: egai-tasks-runner
description: Orchestrate execution of an egai-tasks-writing plan by recursing through its node tree of index.md files. A portfolio, an epic, and a phase are each a directory with its own index.md. Use when given a path to any such node, or to a single task file, plus optional additional instructions, and asked to run, continue, or drive that work to completion. Recurses into itself for each child node, invokes egai-task-impl once per task in a phase, and keeps every index.md checkbox current. Also use when asked to run a range of phases in Stacked Phase Mode, with one git worktree, branch, and pull request per phase, chained sequentially instead of one shared working tree. Also use when asked to run the work sandboxed, printing a fresh `srt`-wrapped CLI command instead of dispatching directly. Do not use to draft task plans or to implement a task's body directly.
metadata:
  version: "3.2.1"
---

# EGAI Tasks Runner

This skill runs one `egai-tasks-writing` plan by walking its node tree. A portfolio, an epic, and a phase are all directories with their own `index.md` file. A task is a leaf file, not a directory. This skill dispatches sub-agents down the tree and keeps every `index.md` file current. It delegates plan drafting to `egai-tasks-writing`. It delegates task-body implementation to `egai-task-impl`.

Write every status update and report this skill produces in `egai-write-tone` terse mode.

## Terms

A **node** is a directory that holds one `index.md` file. That file lists the node's children, each with a checkbox. A node's children are either more nodes or task files. A node whose children are nodes is a **group**. A node whose children are task files is a **phase**. A **task** is one `task-N-*.md` file. `egai-tasks-writing` uses richer names for the same shapes. A portfolio is a group of epics. An epic is a group of phases.

## Input Contract

Accept the following input:

- One filesystem path: a node's directory, its `index.md` file, or a task file.
- Optional additional instructions, given as free text.

Resolve relative paths from the current workspace. Forward the additional instructions to every sub-agent this skill spawns. Keep the instructions unchanged at every recursion level.

## Classify the Path

Before dispatching, run `python3 SKILL_DIRECTORY/scripts/classify-path.py PATH`. Replace `SKILL_DIRECTORY` with the directory that contains this `SKILL.md`. The script prints one of `group`, `phase`, or `task`.

Stop and ask the user when it exits with an error instead of a kind. Do not guess the kind.

## Dispatch by Kind

Switch on the printed kind:

### Group

Read the node's `index.md` for its child list and any `Depends on` relationships between children.

- Before spawning a child, set that child's checkbox in this node's `index.md` to `[~]`.
- Spawn one `egai-tasks-runner` sub-agent for each child. Pass that child's path and the forwarded instructions. A child with no unmet `Depends on` relationship may run concurrently with other such children, because each child owns its own `index.md` file. Wait for a depended-on child's sub-agent to finish before you start a dependent one.
- On each report, set that child's checkbox to `[x]` when the child completed. Set it back to `[ ]` when the child is blocked.
- If a child's sub-agent reports a blocker, halt only the children that depend on it. Let unrelated children continue.

### Phase

Spawn one `egai-task-reader` sub-agent. Give it the phase's path and ask it, in plain language, for the phase's tasks grouped into ordered execution units. The sub-agent reports back an ordered list of units. Each unit is a list of task IDs and files to dispatch concurrently. Run the units in the order reported.

For each unit, in order:

- Before spawning, set that task's checkbox in this phase's `index.md` to `[~]`. See [Index.md Ownership](#indexmd-ownership).
- Spawn one sub-agent per task in the unit. Spawn the sub-agents concurrently for a parallel batch, or alone for a sequential task. Instruct each sub-agent to invoke `egai-task-impl` on the task's path, forward the additional instructions, and report its outcome without editing `index.md`.
- On each report, set that task's checkbox to `[x]` when every acceptance criterion is verified. Set it back to `[ ]` when any criterion is unproven.
- When a task is left unproven, apply `egai-task-impl`'s Incomplete Tasks rule. Record the blocker. Stop before any task that depends on it. Continue only with later tasks that are demonstrably independent.

### Task

If the task belongs to a phase that has an `index.md` file, set its checkbox to `[~]` before spawning.

Spawn one sub-agent that invokes `egai-task-impl` on the task's path. Forward the additional instructions. Instruct the sub-agent not to edit `index.md`. See [Index.md Ownership](#indexmd-ownership).

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

- Tell every sub-agent, at every level, to report its outcome and leave `index.md` untouched.
- Use the checkbox states from `egai-task-impl`'s Index Checkboxes section: `[ ]` for pending, `[~]` for in progress, `[x]` for done.
- The runner instance that dispatched a child is the only one that edits that child's checkbox. It edits that checkbox in the parent's own `index.md`, based on the child's report.

## Reporting

After dispatch completes, or halts on a blocker, report the following:

- The paths and kinds visited.
- Each unit's final status.
- Unproven acceptance criteria with their task IDs.
- The current state of every touched `index.md`.
