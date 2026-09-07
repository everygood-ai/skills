# egai-skill-maker

Creates, revises, and validates portable Agent Skills that follow the agentskills.io specification. It also creates and updates each skill's `README.md`.

## Trigger Conditions

Use this skill for any of the following:

- Designing a new skill.
- Adding a feature or mode to an existing skill.
- Carrying out a task plan, spec, or research document that changes a skill's `SKILL.md`, scripts, references, or assets.
- Organizing a skill's bundled resources.
- Fixing a skill's metadata or structure.
- Checking a skill for specification compliance.
- Writing or refreshing a skill's `README.md`.

The trigger applies even when a request names a plan or document instead of the skill itself. It still applies as long as the change lands inside a skill directory.

## Skill Structure

A skill is a directory with `SKILL.md` at its root. Alongside it:

| File | Status | Role |
|---|---|---|
| `README.md` | Required | Compact documentation of the skill's logic, for a reader who has not activated the skill. |
| `changelog.md` | Required | Version history, one entry per delivered change. |
| `gaps.md` | Optional | Requested behavior the specification or tooling cannot yet represent. |
| `scripts/` | Optional | Executable code, including tests. |
| `references/` | Optional | Documentation loaded only when a task needs it. |
| `assets/` | Optional | Templates, images, and data files used in generated output. |

## Workflow

1. Scope the capability from the request. Split unrelated capabilities into separate skills.
2. Write `SKILL.md`: frontmatter (`name`, `description`, `metadata.version`), then imperative body instructions.
3. Draft the `SKILL.md` prose with `egai-write-tone` in `prose` mode.
4. Pick one version increment for the whole delivered change. Draft the `changelog.md` entry with `egai-write-tone` in `terse` mode.
5. Create or update `README.md` with `egai-write-tone` in `prose` mode, whenever the skill is new or its behavior changed.
6. Validate with `scripts/validate.sh`, and validate `changelog.md` with `scripts/validate_changelog.py`.
7. Test the skill on representative requests, then run the repository's full test suite.

See [SKILL.md](SKILL.md) for the full procedure: naming rules, frontmatter constraints, the version and changelog policy, and the validation wrapper's exit codes.

## Validation

`scripts/validate.sh` wraps the `skill-validator` CLI's structure, content, and contamination checks. It downgrades an orphan-resource warning naming a `scripts/test_*.py` file, `changelog.md`, `gaps.md`, or `README.md` to an `info` diagnostic. An activated agent never needs a runtime pointer to those dev-time-only files.
