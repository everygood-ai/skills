---
name: egai-tasks-writing
description: Create execution-ready Markdown task plans from feature requests and technical specifications. Use when asked to decompose implementation work into phased, schema-valid task files with frontmatter cards, precise scope, testable acceptance criteria, a plan index, and mandatory egai-context-curation handoffs. Supports an optional epic-portfolio layout for splitting large initiatives into independently releasable epics. Do not use for implementation or external issue-tracker management.
metadata:
  version: "5.0.4"
---

# EGAI Tasks Writing

Create implementation plans that a capable engineer unfamiliar with the codebase can execute from the cited project context.

## Workflow

1. Read the request, supplied design material, applicable repository instructions, and the code or documentation needed to resolve project-specific names and constraints.
2. Select the layout for this planning run: **simple plan** or **epic portfolio** (see [Layouts](#layouts)). Use the layout the user names. Ask when the user names neither and the request describes multiple independently releasable workstreams. Otherwise, default to simple plan.
3. Identify the required changes, non-negotiable constraints, affected components, expected behavior, and required tests. Distinguish confirmed requirements from unresolved decisions.
4. Resolve minor gaps from repository evidence. Ask for clarification when a missing decision would materially change scope, architecture, or observable behavior. Do not hide the decision inside a task.
5. Decompose the work into cohesive phases and order tasks by implementation dependency. In an epic portfolio, decompose each epic independently.
6. Before writing an `index.md` or any task file, invoke the `egai-write-tone` skill in `terse` mode and follow its full workflow, not only its reference file. Reduce each task's content to its distinct ideas first, then draft every task file, every `index.md`, and any other text output this skill produces from that reduced set. Frontmatter fields still follow the schema in [Task File Schema](#task-file-schema). Terse mode governs the body prose.
7. Write `index.md` at the plan root, listing its phases. Inside each `phase-N/` subdirectory of that plan root, write one Markdown file per task and that phase's own `index.md` listing its tasks. `N` is the phase number matching the task's `phase` frontmatter field. Use task numbers that increase across all phases within that plan root. In an epic portfolio, repeat this for each epic, starting every epic at Phase 1 / Task 1. Write the portfolio's `index.md` only after every epic's own `index.md` exists.
8. Run `python3 EGAI_TASK_READER_SKILL_DIRECTORY/scripts/taskctl validate TASK_PATH` from the planning workspace, where `EGAI_TASK_READER_SKILL_DIRECTORY` contains `egai-task-reader`'s `SKILL.md` and `TASK_PATH` is the generated plan root, epic root, portfolio root, or a task file. Call this directly, not through a spawned subagent. The pass/fail result decides whether the plan is done.
9. Review the complete task set against the quality checks before delivery.

Write planning artifacts only. Do not implement the tasks or alter non-planning project artifacts unless the user explicitly requests that separate work.

The validator itself is `egai-task-reader`'s `taskctl validate` command, not a script bundled with this skill. Maintain its behavior in `egai-task-reader`'s own `scripts/taskctl/validate.py` and its tests in `scripts/taskctl/tests/test_validate.py`.

## Layouts

A **plan root** is the directory that directly holds one `index.md` and that plan's `phase-N/` directories. An **epic** is an optional, independently releasable workstream containing its own phases. An epic directory is itself a plan root. Phase and task numbers are scoped to their plan root. Every epic therefore starts at Phase 1 / Task 1 on its own and stays movable.

Every plan root, and every `phase-N/` directory inside it, holds exactly one `index.md` listing its own children with a checkbox each. A plan root's `index.md` lists phases. A phase's `index.md` lists tasks.

**Simple plan**: one plan root, no epics.

```text
plan/
  index.md
  phase-1/
    index.md
    task-1-....md
  phase-2/
    index.md
    task-....md
```

**Epic portfolio**: a portfolio root holding multiple epics, each its own plan root.

```text
plan/
  index.md
  epic-authentication/
    index.md
    phase-1/
      index.md
      task-1-....md
  epic-billing/
    index.md
    phase-1/
      index.md
      task-1-....md
```

Write the portfolio's `index.md` only when it holds more than one epic. List every epic there with a checkbox for its status and its dependencies. Keep phase and task detail in each epic's own `index.md` and its phases' `index.md` files. Never let two plan-root `index.md` files nest inside one another's subtree. Each plan root owns exactly one, and each phase inside it owns one more of its own.

Do not add an epic field to task frontmatter. The task file's path is the source of truth for which epic it belongs to. Record epic-level intent, cross-epic dependencies, and outcome in the epic's `index.md`, not in its tasks.

When using epic portfolio, read [the epic portfolio reference](references/epic-portfolio.md) for the portfolio and epic `index.md` templates before writing either file.

## Phase Decomposition

Define a phase as a cohesive, independently testable slice of the change. Group work that touches the same files or tightly related code and produces one meaningful outcome.

Define a task as the smallest independently committable and verifiable unit that a less capable implementation agent could complete from its cited context. A task may rely on completed earlier tasks, but it must produce a meaningful change at its point in the sequence.

Apply these rules:

- Keep each phase to at most six tasks, including its final context-update task. Split larger groups at a testable boundary.
- Put foundation work before consumers and behavior before integration or end-to-end verification.
- Keep tightly coupled changes together when separating them would leave neither task independently verifiable.
- Split an objective that joins distinct outcomes with "and." Keep inseparable actions together when they form one observable result.
- Execute tasks in task-number order by default. Set `parallel: true` only for tasks in a consecutive parallel batch that may run concurrently at the start of a phase or after the preceding sequential task completes. The whole batch must complete before the next `parallel: false` task starts.
- Keep every task in a parallel batch independent of the other tasks in that batch: no shared mutable files, produced artifacts, or ordering dependency.
- Name deferred behavior explicitly in the plan's phase entry when a phase intentionally leaves stubs, partial wiring, or incomplete behavior for a later phase.
- Add a dependency note only when a phase relies on a concrete outcome from an earlier phase.

## Mandatory Phase Ending

End every phase with `phase-P/task-N-update-context.md`, where `P` is the phase number and `N` is the task number. This task must invoke `egai-context-curation` in `incremental-update` mode after the phase's implementation tasks are complete.

Use this format:

```markdown
---
id: "task-N"
title: "Update Context"
phase: PHASE_NUMBER
description: "Update the project context to reflect all changes completed in this phase."
deliverable: "Project context that accurately describes the codebase after this phase."
acceptance_criteria:
  - id: "task-N-1"
    criterion: "egai-context-curation has completed an incremental-update and reported the inspected scope and context files changed."
  - id: "task-N-2"
    criterion: "No updated context claim contradicts the current code."
  - id: "task-N-3"
    criterion: "Context links, paths, and component names resolve to current project artifacts."
parallel: false
---

# Task N: Update Context

## Context to Read First

- All files added or modified during this phase
- Existing project context for the affected area

## Scope

- Invoke `egai-context-curation` in `incremental-update` mode for the affected project area.
- Pass the complete list of files changed in this phase, the relevant source path, and the applicable context path.
- Have `egai-context-curation` synchronize project context with the implemented behavior and structure.

```

## Task File Schema

Place each task file at `phase-P/task-N-short-name.md`. The `phase-P` directory sits directly inside a plan root: the top-level plan directory in a simple plan, or an epic directory in an epic portfolio. `P` matches the task's `phase` frontmatter value. `N` is the task number, unique within that plan root. Follow this structure for every implementation task:

```markdown
---
id: "task-N"
title: "SHORT NAME"
phase: PHASE_NUMBER
description: "OBJECTIVE SENTENCE STARTING WITH A STRONG VERB; NAME THE COMPONENT AND SINGLE OUTCOME."
deliverable: "ONE INDEPENDENTLY VERIFIABLE RESULT."
acceptance_criteria:
  - id: "task-N-1"
    criterion: "OBSERVABLE CONDITION GROUNDED IN THE SOURCE REQUIREMENTS."
  - id: "task-N-2"
    criterion: "BOUNDARY, FAILURE, COMPATIBILITY, OR INTEGRATION CONDITION."
  - id: "task-N-3"
    criterion: "Tests cover: SPECIFIC BEHAVIORS AND RELEVANT TEST LEVEL."
parallel: false
---

# Task N: SHORT NAME

## Context to Read First

- `PATH` — SPECIFIC SECTION, SYMBOL, OR REASON TO READ IT
- `PATH` — RELEVANT REQUIREMENT, CONSTRAINT, OR TEST GUIDANCE

## Scope

REQUIRED END STATE; DESCRIBE OUTCOMES, NOT STEP-BY-STEP IMPLEMENTATION.

- REQUIRED CHANGE TO A NAMED COMPONENT, ENTITY, BEHAVIOR, OR FILE
- REQUIRED CHANGE
```

Replace every placeholder. Use double-quoted, single-line YAML strings in frontmatter. Escape embedded double quotes. The validator intentionally rejects multiline scalars and additional frontmatter fields so task cards remain predictable and independently readable.

Apply these frontmatter rules:

- Include exactly `id`, `title`, `phase`, `description`, `deliverable`, `acceptance_criteria`, and `parallel`.
- Set `id` to `task-N`, matching the task number in the filename and heading.
- Set `title` to the heading text after `Task N:`.
- Set `phase` to the positive integer of the containing overview phase.
- Write `description` as the task's single strong-verb objective.
- Write `deliverable` as one independently verifiable result.
- Give every criterion an `id` of `task-N-M`, where `M` starts at 1 and increases without gaps, and a non-empty `criterion` string.
- Set `parallel` to a YAML boolean. Use `false` unless the phase decomposition rules establish a safe consecutive parallel batch.

Cite exact existing paths and symbols in the body when available. A path produced by an earlier task is valid context only when the task order makes that dependency clear. Never invent a reference merely to fill the section.

## Writing Rules

Write for an eager junior engineer who has read the cited context but has not worked in the codebase.

- Start each implementation `description` with a strong verb such as **Add**, **Implement**, **Wire**, **Extract**, **Migrate**, **Register**, **Remove**, or **Verify**.
- Give each task one objective. Name the affected component and concrete outcome.
- Preserve component, entity, endpoint, event, and file names exactly as they appear in the source material.
- Use direct requirements. Avoid "you should," "consider," "handle appropriately," "works correctly," and other language that cannot be verified.
- Keep product rationale and general domain explanation in the cited source material, not in task files.
- State scope as required end state. Do not prescribe implementation steps unless the source design makes the method non-negotiable.
- Do not include code, SQL, configuration blocks, or shell commands. Include exact syntax only when it is the sole unambiguous expression of a required constraint, and explain its necessity in one sentence.
- Make every implementation task independently committable and verifiable after its declared predecessors are complete. Merge a task with its neighbor when it has no independently observable deliverable.
- Include at least one test-based frontmatter acceptance criterion in every implementation task. Name the behavior, input or condition, and expected result. "Tests pass" is insufficient.
- Cover applicable success, boundary, failure, compatibility, and integration behavior without duplicating the same criterion in multiple tasks.
- Keep acceptance criteria within the task's scope. Do not make a task responsible for the whole phase.

The mandatory context-update task is documentation work and uses the accuracy criteria in its dedicated schema instead of a test-based criterion. Its `parallel` value is always `false` because it consumes the completed phase.

## Index File Schema

Every `index.md` — plan root, epic, or phase — starts with required YAML frontmatter, `---`-delimited, giving two fields: `kind` (`"group"` for a plan root or epic, `"phase"` for a phase directory) and `name` (the node's title, quoted; for a phase, the name only, without the `N:` prefix). The validator reads `kind` directly instead of inferring group versus phase from directory structure, so an empty group still classifies correctly.

Keep the Markdown heading in the body too: `# TITLE` for a group, `# Phase N: NAME` for a phase, with `N` sourced from the `phase-N` directory name, never duplicated in frontmatter. The validator requires the heading to match `name` exactly.

## Index Format

Every plan root and every phase writes an `index.md`. Use this template for a plan root, directly for a simple plan. In an epic portfolio, prepend the epic header from [the epic portfolio reference](references/epic-portfolio.md) before `## Phases` when writing an epic's `index.md`.

```markdown
---
kind: "group"
name: "PLAN OR EPIC TITLE"
---

# PLAN OR EPIC TITLE

TWO OR THREE SENTENCES DESCRIBING THE OUTCOME AND BOUNDARY; LINK THE SOURCE SPECIFICATION WHEN ONE EXISTS.

## Phases

- [ ] [Phase 1: NAME](phase-1/index.md)
  - **Outcome:** INDEPENDENTLY TESTABLE RESULT AVAILABLE AT THE END OF THE PHASE
  - **Scope:** SPECIFIC COMPONENTS, ENTITIES, ENDPOINTS, OR BEHAVIORS DELIVERED IN FULL
  - **Deferred to later phases:** SPECIFIC INCOMPLETE BEHAVIOR AND THE PHASE THAT COMPLETES IT; OMIT WHEN EMPTY
- [ ] [Phase 2: NAME](phase-2/index.md)
  - **Outcome:** INDEPENDENTLY TESTABLE RESULT
  - **Scope:** SPECIFIC WORK DELIVERED IN FULL
  - **Depends on:** Phase 1 — CONCRETE OUTCOME CONSUMED FROM PHASE 1
  - **Deferred to later phases:** OMIT WHEN EMPTY

## References

- EXISTING SOURCE SPECIFICATION, DESIGN, REPOSITORY INSTRUCTION, OR CONTEXT PATH
```

Use nested bullets under a phase entry when its **Scope** covers multiple items. Omit **Depends on**, **Deferred to later phases**, or **References** when they would be empty. Initialize each phase checkbox with `[ ]`. Use `[~]` while a phase is in progress and `[x]` only when every task in it is done. Do not add a textual state. The plan index must make intentional incompleteness visible so reviewers do not mistake it for an omission.

Write each phase's own `index.md` inside its `phase-N/` directory, listing only its tasks:

```markdown
---
kind: "phase"
name: "NAME"
---

# Phase N: NAME

## Tasks

- [ ] [Task 1: SHORT NAME](task-1-short-name.md)
- [ ] [Task 2: Update Context](task-2-update-context.md)
```

Include every phase task under **Tasks** in execution order, with links relative to the phase directory. Initialize each entry with `[ ]`. Use `[~]` while implementation is in progress and `[x]` only when the task is done.

## Quality Checks

Confirm all of the following:

- Every requirement maps to at least one task, and no task adds unsupported product or architecture decisions.
- Every task passes `EGAI_TASK_READER_SKILL_DIRECTORY/scripts/taskctl validate`. Its frontmatter has the exact schema, matches its filename and heading, and has continuous acceptance-criterion IDs.
- Every group and phase `index.md` has `kind`/`name` frontmatter, and its Markdown heading matches `name` exactly.
- Every implementation task has one strong-verb `description` and names an independently verifiable `deliverable`.
- Every cited path exists now or is explicitly created by an earlier task.
- Every task file lives inside a `phase-N/` directory where `N` matches the task's `phase` frontmatter field, and that `phase-N/` directory sits directly inside a plan root.
- No task frontmatter carries an epic field, and the folder path is the only record of which epic a task belongs to.
- Every plan root has its own `index.md`, every phase inside it has its own `index.md`, and no plan-root `index.md` nests inside another plan root's subtree.
- In an epic portfolio, `index.md` exists at the portfolio root only when it holds more than one epic.
- The portfolio's `index.md` lists each epic's dependencies and a status checkbox, not phase or task detail.
- Every phase's `index.md` lists exactly its own task files, each with a checkbox, and no task appears in more than one phase's `index.md`.
- `EGAI_TASK_READER_SKILL_DIRECTORY/scripts/taskctl validate` passes when run against the full plan, portfolio, or epic root, confirming task numbering is unique within each plan root and correctly reset per epic.
- Every implementation task includes a behavior-specific test criterion in `acceptance_criteria`.
- Task order satisfies dependencies, numbering is continuous, and filenames match headings.
- Every `parallel: true` task belongs to a consecutive, conflict-free parallel batch at the phase start or bounded by sequential work.
- Every task appears once, in its own phase's `index.md`, with a `[ ]` checkbox and no textual state.
- Every phase has an independently testable outcome and no more than six tasks.
- Every phase ends with exactly one context-update task that invokes `egai-context-curation` in `incremental-update` mode, and no task follows it within that phase.
- Every intentional stub or partial behavior appears under **Deferred to later phases** with its completion phase.
- Task files contain no code except a justified exact-syntax constraint.
- Each `index.md` accurately summarizes its own children.

Read [the changelog](changelog.md) only when reviewing this skill's version history or preparing a revision.
