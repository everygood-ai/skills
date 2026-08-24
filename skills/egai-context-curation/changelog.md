# Changelog

- `3.1.0` — Added "Link from Repository Instructions": every mode now ensures the repository root's `AGENTS.md` and `CLAUDE.md` link to the current run's `main.md` under a `## Project Context` heading, creating either file if it does not exist. `audit-stale` treats a missing or stale link as a mismatch, applied only when edits are authorized.
- `3.0.0` — Breaking schema change. Dropped context-file frontmatter (`description`, `limit`) and the per-file limit/permission workflow in favor of a single flat 500-line ceiling on every context file. Replaced the fixed six-file set with an open-ended, `main.md`-indexed split model: split a topic when the project's own shape divides it, not on line count. Added a `.context/context-lock.json` lock file recording `domainCapture`/`interfacesCapture` decisions from a new per-file applicability test, so `domain.md` and `interfaces.md` are captured or skipped based on project signal (and, for `domain.md`, an authoritative spec) instead of always being drafted. `audit-stale` now re-checks that applicability, not just existing claims. Rewrote `scripts/validate-context-lengths.sh` to check the flat ceiling against whatever `.md` files are actually present.
- `2.1.0` — Added a tone-compliance step: draft the six context files in `egai-write-tone` `compact` mode and every other text output in `terse` mode, invoking that skill's full workflow rather than only its reference file. Rewrote prose to comply with `egai-write-tone` `prose` mode's redundancy-first rules.
- `2.0.0` — Renamed the skill from `general-context-curation` to `egai-context-curation`.
- `1.1.3` — Replaced HTML-like placeholders and comments with plain-text markers.
- `1.1.2` — Required each context limit to be one unquoted positive integer rather than a range or text value.
- `1.1.1` — Raised all default context-file limits to a combined 490-line budget.
- `1.1.0` — Added required context-file frontmatter, permission-gated limit increases, and deterministic metadata and line-count validation.
- `1.0.0` — Created a portable four-mode workflow for extracting, updating, improving, and auditing compact project context.
