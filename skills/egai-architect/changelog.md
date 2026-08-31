# Changelog

- `1.1.2` — Rewrote prose to comply with `egai-write-tone` `prose` mode's new redundancy-first rules. Fixed a stale reference to `terse` mode's dropped procedural/descriptive classification step. Changed the tone-compliance step to invoke `egai-write-tone`'s full workflow, not only its reference file, after live use showed a draft could still drift into flowing prose when only the reference file's rules were loaded. Strengthened the delivery gate to run the self-check as the primary meaning-level pass before linting, and to require rewriting any failing section instead of only noting it.
- `1.1.1` — Updated the `egai-write-tone` mode name from `medium` to `terse`, following that skill's `low`/`medium`/`high` to `prose`/`terse`/`compact` rename.
- `1.1.0` — Added an ad hoc judgment workflow path and closed the gap where a tradeoff answer or recommendation, not framed as a document or review, skipped `egai-write-tone` medium-mode control entirely.
- `1.0.1` — Reordered the tone-compliance step to load `egai-write-tone`'s medium-mode rules before drafting instead of rewriting a finished draft, avoiding a duplicate full-text pass.
- `1.0.0` — Created the initial skill.
