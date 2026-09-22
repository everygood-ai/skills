# Tone contract lifecycle

`egai-write-tone` owns the portable router, mode profiles, standalone workflow, and structural lint wrapper. Canonical contract text is maintained in versioned `capabilities/write-tone-*/vN/` bundles.

## Source and generated ownership

- Source `references/contracts/*/vN.md` files contain capability placeholders and preserve the package's contract layout.
- The compiler resolves each placeholder to one selected capability revision.
- Generated `skills/egai-write-tone/references/contracts/` files are materialized consumers. Never edit them directly.
- `SKILL.md` routes users to profiles and workflow. It does not own duplicate canonical contract prose.

## Operational flow

1. Add or revise canonical text in a new immutable capability revision when contract meaning changes.
2. Update source placeholders only when this package should consume that revision.
3. Compile the source package and verify the generated tree.
4. Release the source package with a paired version and changelog update.

## Script boundaries and invariants

- `scripts/lint.sh` selects one Vale configuration per mode. It checks structural patterns, not idea deduplication or Markdown block shape.
- `scripts/test_skill_tone.py` checks contract files, workflow links, and representative lint behavior.
- Keep one canonical contract per capability revision and keep source placeholders whole-line and fence-aware.
- Mode names, contract paths, and revision references must remain aligned across source, capabilities, and generated output.

## Verification

Run `go run ./cmd/skills-compiler verify egai-write-tone`, then run the generated package's focused tests and mode lint checks. Treat missing `vale` as an environment-dependent lint skip, not a contract failure.
