# egai-tasks-writing

Creates execution-ready Markdown task plans from feature requests and technical specifications. It decomposes a request into phased, schema-valid task files, each with a frontmatter card, precise scope, and testable acceptance criteria.

## Input

The input is a feature request or technical specification, given as free text, plus any supplied design material and applicable repository instructions. This differs from the other two task-pipeline skills, which take a filesystem path to an existing plan or task file.

The caller also selects a layout: a **simple plan**, one plan root with no epics, or an **epic portfolio**, a set of independently releasable epics that each start their own Phase 1. Use the layout the user names. Ask when the user names neither and the request describes multiple independently releasable workstreams; otherwise default to simple plan.

## Output

The skill writes one `index.md` per plan root, epic, and phase, plus one `task-N-*.md` file per task. Every phase ends with a mandatory context-update task that invokes `egai-context-curation` in `incremental-update` mode.

### Example: simple plan

```text
plan/
  index.md
  phase-1/
    index.md
    task-1-add-auth-schema.md
    task-2-implement-login-endpoint.md
    task-3-update-context.md
  phase-2/
    index.md
    task-4-add-session-refresh.md
    task-5-update-context.md
```

### Example: epic portfolio

```text
plan/
  index.md
  epic-authentication/
    index.md
    phase-1/
      index.md
      task-1-add-auth-schema.md
      task-2-update-context.md
  epic-billing/
    index.md
    phase-1/
      index.md
      task-1-add-invoice-model.md
      task-2-update-context.md
```

Each plan root — the top-level `plan/` directory in a simple plan, or each epic directory in a portfolio — owns exactly one `index.md`, and so does every `phase-N/` directory inside it. See [Layouts](SKILL.md#layouts) for the full rules.

## Task Frontmatter

Every task file opens with a required, schema-validated YAML frontmatter card.

Keep this schema exact because [egai-task-reader](../egai-task-reader/README.md) depends on it mechanically. Every pipeline skill depends on egai-task-reader in turn. Its bundled `taskctl` package reads the frontmatter card without loading the task body:

- `ac` returns `acceptance_criteria` for [egai-task-impl](../egai-task-impl/README.md)'s verification.
- `validate` checks the whole schema, including this skill's own authoring-time check, for `egai-tasks-writing`.
- `phase-batch`, `phase-info`, and `pr-body` serve [egai-tasks-runner](../egai-tasks-runner/README.md)'s scheduling and PR metadata needs.

A missing field, an extra field, or a gap in `acceptance_criteria` IDs breaks that read before any dependent skill reaches the prose. The frontmatter must stand on its own. See [egai-task-reader](../egai-task-reader/README.md) for the full command reference.

```yaml
---
id: "task-2"
title: "Implement Login Endpoint"
phase: 1
description: "Implement the POST /login endpoint that authenticates a user and returns a session token."
deliverable: "A working /login endpoint verified by an integration test."
acceptance_criteria:
  - id: "task-2-1"
    criterion: "POST /login with valid credentials returns a session token and 200 status."
  - id: "task-2-2"
    criterion: "POST /login with invalid credentials returns 401 and no token."
  - id: "task-2-3"
    criterion: "Tests cover: valid login, invalid credentials, and missing request fields."
parallel: false
---
```

| Field | Type | Meaning |
| --- | --- | --- |
| `id` | string | `task-N`, matching the task number in the filename and heading. |
| `title` | string | The heading text after `Task N:`. |
| `phase` | integer | The number of the containing `phase-N/` directory. |
| `description` | string | The task's single strong-verb objective, naming the component and outcome. |
| `deliverable` | string | One independently verifiable result. |
| `acceptance_criteria` | list | Entries with `id` (`task-N-M`, gapless from 1) and `criterion`, an observable, testable condition. At least one criterion in an implementation task must be test-based. |
| `parallel` | boolean | `true` only for a task in a safe, conflict-free consecutive parallel batch; `false` otherwise. |

No other frontmatter fields are permitted, and values must be double-quoted single-line YAML strings. `taskctl validate` rejects multiline scalars and unrecognized keys. See [Task File Schema](SKILL.md#task-file-schema) for the full field rules and the mandatory context-update task's variant schema.

## Task Pipeline

`egai-tasks-writing` is the first stage of a three-skill chain: it authors the plan tree that [egai-tasks-runner](../egai-tasks-runner/README.md) walks, dispatching sub-agents that call [egai-task-impl](../egai-task-impl/README.md) to implement each task's body. This skill only drafts plans; it never implements a task or edits an existing plan's runtime state.

See [SKILL.md](SKILL.md) for the full workflow, the task file and index schemas, and the quality checks the validator enforces.
