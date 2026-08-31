# Epic Portfolio Templates

Read this file only when the current planning run uses the epic portfolio layout.

## Epic `index.md`

Write each epic's `index.md` using the [Index Format](../SKILL.md#index-format) plan-index template, including its `kind: "group"` frontmatter. Insert this header before `## Phases`:

```markdown
# EPIC TITLE

TWO OR THREE SENTENCES DESCRIBING THE EPIC'S OUTCOME; LINK THE SOURCE SPECIFICATION WHEN ONE EXISTS.

- **Outcome:** THE INDEPENDENTLY RELEASABLE RESULT THIS EPIC DELIVERS
- **Boundaries:** WHAT THIS EPIC COVERS AND WHAT IT EXPLICITLY EXCLUDES
- **Depends on:** OTHER EPIC NAME — CONCRETE OUTCOME THIS EPIC CONSUMES FROM IT; OMIT WHEN THIS EPIC HAS NO CROSS-EPIC DEPENDENCY

## Phases
```

Follow the header with the same phase checklist and `## References` section as the plan-index template. Number phases and tasks starting at 1 within this epic, independent of every other epic. Give each phase its own `index.md`, exactly as in a simple plan.

## Portfolio `index.md`

Write `index.md` at the portfolio root only when it holds more than one epic. List every epic with a checkbox for its status and its dependency on other epics. Leave phase and task detail out of the portfolio's `index.md`. That detail lives in each epic's own `index.md` and its phases' `index.md` files.

```markdown
---
kind: "group"
name: "PORTFOLIO TITLE"
---

# PORTFOLIO TITLE

ONE OR TWO SENTENCES DESCRIBING THE PORTFOLIO'S SCOPE.

## Epics

- [ ] [EPIC NAME](epic-SLUG/index.md)
  - **Depends on:** OTHER EPIC NAME; OMIT WHEN THIS EPIC HAS NO CROSS-EPIC DEPENDENCY
- [ ] [EPIC NAME](epic-SLUG/index.md)
```

Use `[~]` while an epic is in progress and `[x]` only when every phase in it is done. Update each epic's checkbox as work progresses. Do not duplicate a phase or task list here. A reviewer follows the epic link for that detail.
