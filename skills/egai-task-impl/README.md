# egai-task-impl

Implements one task written by [egai-tasks-writing](../egai-tasks-writing/README.md). It reads a task's scope, implements the required change, and verifies each acceptance criterion before marking the task done.

## Input

The preferred input is a filesystem path: exactly one task-file path per invocation. The skill also accepts task contents copied directly into the request, but only as a fallback. When both a path and copied contents are present, the path is authoritative. When only copied contents are supplied, the skill locates the task's real path in the repository before implementing.

`egai-task-impl` calls [egai-task-reader](../egai-task-reader/README.md)'s `taskctl ac` inline instead of bundling its own script. This verifies acceptance criteria without re-reading the task body. See egai-task-reader's own README for its full command surface.

## Task Pipeline

`egai-task-impl` is the last stage of the task pipeline: it implements one task's body after [egai-tasks-writing](../egai-tasks-writing/README.md) has authored the plan and [egai-tasks-runner](../egai-tasks-runner/README.md) has dispatched it. When `egai-tasks-runner` dispatches a task directly, it owns that task's `index.md` checkbox, so `egai-task-impl` reports its outcome without editing `index.md`. When invoked standalone, without a dispatching runner, `egai-task-impl` updates the checkbox itself.

See [SKILL.md](SKILL.md) for the full workflow and the incomplete-task handling.
