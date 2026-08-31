---
name: egai-task-impl
description: Implement one schema-valid task file produced by egai-tasks-writing. Use when given a single local task-file path and asked to read the task, implement its scope and deliverable, verify its acceptance criteria, and synchronize its checkbox in the phase's index.md. Do not use to write plans, schedule multiple tasks, or implement an unstructured request.
metadata:
  version: "7.0.1"
---

# EGAI Task Impl

Implement one task written by `egai-tasks-writing`, given by its task-file path.

## Implementation Rules

Before writing new code, climb the simplicity ladder in order: Does this code need to exist at all? Is it already in the codebase? Does the standard library cover it? Can it be a one-liner? Write the minimum working code only after exhausting these alternatives.

- Avoid unrequested abstractions, such as an interface with a single implementation or a factory for one product.
- Prefer deleting code over adding it when both achieve the goal.
- Shortest working diff wins.
- Fix bugs at their root cause, not at the symptom.

Never apply these rules to: input validation at trust boundaries, error handling that prevents data loss, security measures, or anything explicitly requested in the task. Never be lazy about reading and understanding the task and its context before acting.

## Input Contract

Accept exactly one task-file path per invocation. Prefer task context as a path to a local task file, not as task contents copied into the request.

- When both a path and copied contents are present, treat the file at the path as authoritative.
- When only copied task contents are supplied, locate the corresponding task path in the repository before implementation. Ask for the path if it cannot be resolved.
- Resolve a relative path from the current workspace. Do not require the caller to preload task contents into model context.

## Task Card Access

Verify acceptance criteria through `egai-task-reader`'s bundled `taskctl`, not a copy of it in this skill. Replace `EGAI_TASK_READER_SKILL_DIRECTORY` with the directory containing `egai-task-reader`'s `SKILL.md`:

```text
python3 EGAI_TASK_READER_SKILL_DIRECTORY/scripts/taskctl ac TASK_FILE
```

`ac` returns the acceptance-criterion IDs and statements without loading the task body. Read the complete task file first. Call `ac` when verifying or reporting criteria.

## Workflow

1. Resolve the requested task path.
2. Read the task file completely, then read its **Context to Read First** and applicable repository instructions.
3. In the phase's `index.md`, change the task's checkbox from `[ ]` to `[~]`.
4. Implement only the task's body **Scope** and frontmatter `deliverable`, preserving unrelated user changes.
5. Run `taskctl ac` and verify every returned criterion with the most direct relevant test or inspection. Never report a criterion as proven based on intent, partial work, or an unrelated passing test.
6. When every criterion is proven, change the task's `index.md` checkbox to `[x]`. Acceptance criteria are immutable task-definition data. Do not add completion state to their frontmatter.
7. Report the implemented task ID, criterion IDs with verification evidence, files changed, and any unproven criteria.

## Incomplete Tasks

If a task cannot be completed safely:

- Leave every unproven acceptance criterion unchanged in the task definition.
- Report every unproven criterion by its `task-N-M` ID.
- Return its `index.md` checkbox to `[ ]`.
- Record the concrete blocker in the final report.
- Stop before dependent tasks. Continue with later tasks only when they are demonstrably independent.

Do not weaken or rewrite acceptance criteria to make an implementation appear complete. Ask for direction when completion requires a product decision, new authority, or scope beyond the task.

## Index Checkboxes

Use the task entry created by `egai-tasks-writing`, in the phase's own `index.md`:

```markdown
- [ ] [Task N: Short Name](task-N-short-name.md)
```

Use only this convention:

- `[ ]` — pending or not done
- `[~]` — in progress
- `[x]` — done

If the task entry is missing, add it to the phase's `index.md` before implementation. Do not reorder or rename other tasks.

Read [the changelog](changelog.md) only when reviewing this skill's version history or preparing a revision.
