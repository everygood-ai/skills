# Context entry structure

Give each independently reviewable or changeable fact its own Markdown list item. Do not combine branches, comparison mechanics, consumers, and skip conditions in one sentence.

When related facts share a subject, use a compact parent claim with nested child items for the distinct details. Keep each item to one compact statement. Use one nested level normally; add another only when a child has independently changing branches.

Name the parent by its cross-file behavior, ownership, or consequence. Do not name it after a private method, class, variable, or field. When an implementation location materially helps verification, add a relative link to its code file after the semantic claim; do not substitute a symbol name or line anchor.

```markdown
- Coverage classification ([implementation](../src/coverage_scope.py)) distinguishes full runs from incremental runs.
  - Full run: fresh state with no earlier snapshot covers every declared record.
  - Incremental run: only records added or changed from the resolved base need coverage.
  - Comparison: current and base snapshots use one declaration model.
  - Consumer: reverse reachability only.
  - Skip: unreadable revision metadata or unresolved base.
```
