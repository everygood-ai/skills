# Plan authoring model

`egai-tasks-writing` turns a feature request or technical specification into an execution-ready Markdown task tree. It owns planning artifacts only; implementation and runtime checkbox updates belong to downstream skills.

## Layout ownership

Choose the layout before writing files. A simple plan has one plan root and phases. An epic portfolio has a portfolio root whose epics are independent plan roots, each with its own phases and numbering. Every plan root and every phase owns exactly one `index.md`.

```text
plan/
  index.md
  phase-1/
    index.md
    task-1-*.md
```

Group indexes list child groups or phases. Phase indexes list task files with relative checkbox links. Task numbers increase across phases in a simple plan; each epic starts again at Phase 1 / Task 1. Do not add an epic field to task frontmatter: the path establishes epic ownership.

## Task and phase contract

Decompose confirmed requirements into cohesive, independently verifiable phases and tasks, ordered by dependency. A task card has the exact schema `id`, `title`, `phase`, `description`, `deliverable`, `acceptance_criteria`, and `parallel`; criteria are observable and gapless. Use `parallel: true` only for a consecutive conflict-free batch. Keep each phase to six tasks or fewer.

Every phase ends with `task-N-update-context.md`. Its scope invokes `egai-context-curation` in `incremental-update` mode after the implementation tasks, passing the complete changed-file list and applicable context. This terminal task verifies that context claims, links, and names match the completed phase.

Before writing any index or task, read the bundled task-plan tone reference and apply it to all generated prose. Resolve project-specific names and constraints from the supplied material, repository instructions, and evidence; ask when an unresolved decision would change scope or observable behavior.

## Validation handoff

After the complete tree exists, call `egai-task-reader`’s `taskctl validate` directly from the planning workspace. The validator is the source of truth for card schema, filename/heading/id consistency, index frontmatter and links, plan/epic nesting, and duplicate IDs. A passing validation result is the authoring completion gate. Hand the validated tree to `egai-tasks-runner`; do not implement tasks or edit execution state in this package.
