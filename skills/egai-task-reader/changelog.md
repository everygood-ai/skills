# Changelog

- `1.1.1` — Trimmed `SKILL.md` and `README.md` to drop named-consumer framing ("shared dependency," per-caller examples), keeping only the mechanics an activated agent needs. No behavior change.
- `1.1.0`
  - Added `validate`: full authoring-time plan validation, ported from `egai-tasks-writing`'s `validate-tasks.py`.
  - `egai-tasks-writing` now depends on this skill for validation instead of bundling its own copy.
  - Reused `cards.py`'s and `phase.py`'s shared regexes and quoted-string parser in the new `validate.py`.
- `1.0.0`
  - Created the skill: extracted `taskctl` from `egai-task-impl` into its own `cards`/`phase` package.
  - Kept `card`, `ac`, `phase-info`, and `pr-body` behavior unchanged.
  - Added `phase-batch`: groups a phase's tasks into ordered sequential and parallel execution units.
