# Skill package maintenance

`egai-skill-maker` owns portable skill structure, authoring guidance, bundled validation, and development-time release checks. A source package under `skills-src/` is canonical. Its matching `skills/` tree is compiler output.

## Package and resource boundaries

- `SKILL.md` contains activation and runtime instructions.
- `README.md` summarizes the package for readers who have not activated it.
- `references/` and `assets/` hold resources needed by runtime workflows.
- `scripts/` holds deterministic wrappers, validators, and tests.
- `docs/*.md` holds maintainer documentation and is not a runtime dependency.

## Validation flow

1. Run `scripts/validate.sh SKILL_DIRECTORY` for local structure, content, contamination, and orphan checks.
2. Run `scripts/validate.sh --links SKILL_DIRECTORY` when external links need checking. Network results are environment-dependent.
3. Run `scripts/validate_changelog.py CHANGELOG_PATH` for version-entry shape, uniqueness, and bullet length.
4. For source-built packages, use the repository compiler to materialize and verify generated output.

The wrapper rejects forbidden HTML in `SKILL.md`, delegates specification checks to `skill-validator`, and downgrades approved development-only orphan warnings. It does not validate runtime behavior.

## Release invariants

- Package directory, frontmatter `name`, `metadata.version`, and newest changelog version identify one skill.
- Every source edit changes the package version and adds a matching changelog entry.
- `docs/*.md`, `README.md`, `changelog.md`, `gaps.md`, and `scripts/test_*.py` do not need runtime links from `SKILL.md`.
- Other bundled resources must be linked from runtime instructions when an activated agent needs them.

## Script boundaries

`filter-orphans.py` transforms only the validator's JSON report. `validate_changelog.py` checks changelog syntax and word limits. Tone injection copies bundled contracts into a portable target. It does not use the repository compiler or tone manifest. Tests are development-time inputs and are discovered by the repository suite.
