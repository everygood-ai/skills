# Task execution contract

`egai-task-impl` implements exactly one schema-valid `task-N-*.md` file authored by `egai-tasks-writing`. It is the evidence-producing leaf of the task pipeline; it does not draft plans, schedule tasks, or accept an unstructured request.

## Input and scope

Accept one task-file path, resolving a relative path from the current workspace. The file at that path is authoritative when copied task text is also supplied. Read the complete card and its `Context to Read First`, then implement only the card’s `Scope` and `deliverable`, preserving unrelated changes.

The task’s acceptance criteria are immutable definition data. Query them with `egai-task-reader`’s `taskctl ac TASK_FILE`, then verify every criterion using the most direct relevant test or inspection. Report criterion IDs with concrete evidence; a passing unrelated test or implementation intent is not proof.

## Checkbox and context boundaries

When invoked standalone, update the task entry in its phase `index.md`: `[ ]` to `[~]` before work and `[x]` only after every criterion is proven. If any criterion is unproven, return the entry to `[ ]`, record the blocker, and stop before dependent work. Never rewrite criteria or add completion state to the card.

When `egai-tasks-runner` dispatches the task, the runner owns the phase index checkbox. In that mode, report the outcome and leave every `index.md` untouched so only one runner instance writes a given index.

The mandatory phase-ending context task is still a normal single task: it invokes `egai-context-curation` in incremental-update mode and proves the resulting context is current. This skill does not update context outside the task’s declared scope.

## Reporting and maintenance

Completion reports include the task ID, each criterion ID and verification evidence, changed files, and unproven criteria or blockers. Apply the compiled report-tone reference. Keep implementation comments rare and intent-focused; if a non-obvious comment is required, obtain compact wording through the live `egai-write-tone` invocation. The package has no implementation scripts of its own; task-card parsing and criterion access remain owned by `egai-task-reader`.
