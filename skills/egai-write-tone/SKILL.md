---
name: egai-write-tone
description: Write or rewrite text at one of three tone levels — prose (clear, scannable documentation for product docs and guides), terse (dense, on-point technical writing, one idea per line), or compact (maximum-density compression for requirements and context files, meaning must stay unambiguous). Use when asked to write, rewrite, tighten, or compress text to a stated tone or register, or to cut a wordy draft down to size without losing meaning. Do not use for casual conversational writing, marketing copy, or creative prose.
compatibility: Structural linting (scripts/lint.sh) requires the vale CLI; rules are verified with vale 3.17.1.
metadata:
  version: "3.1.3"
---

# EGAI Write Tone

Write or rewrite text at a controlled tone level. Every level answers the same question — is this unambiguous and free of restated content? — with a different budget for words.

| Mode | Use for | Governing rules |
|---|---|---|
| `prose` | Product documentation, feature descriptions, guides — text meant to read well and scan fast | [references/contracts/prose/v1.md](references/contracts/prose/v1.md) |
| `terse` | Technical/procedural documentation that needs to be dense and on-point | [references/contracts/terse/v1.md](references/contracts/terse/v1.md) |
| `compact` | Dense requirements, compact project context, system-prompt-style text | [references/contracts/compact/v1.md](references/contracts/compact/v1.md) |

Modes are not interchangeable presets of the same rules — each profile file is authoritative for its mode, on top of the shared [kernel](references/contracts/kernel/v1.md). Do not apply terse's line-by-line format to prose mode, and do not apply prose's full-sentence grammar to compact mode.

## Workflow

On activation, follow [references/standalone-workflow.md](references/standalone-workflow.md) in full. It is the complete procedure: determining the mode, reducing the source to its distinct ideas, loading the kernel plus the selected mode's profile, drafting, linting, reviewing the result before delivery, and reporting which mode was used.

A consumer skill that already knows its required profile does not need the standalone workflow — it loads its own compiled contract instead.

## Structural linting

`scripts/lint.sh` runs a bundled Vale style package that checks structural rules mechanically: sentence length, Latin abbreviations, and (in `compact` mode) filler words and undefined symbols. It cannot check whether ideas were actually deduplicated, or whether structure (headings/lists/tables) was used where the content called for it — those need a human read.

```bash
scripts/lint.sh prose FILE.md
scripts/lint.sh terse FILE.md
scripts/lint.sh compact FILE.md
```

Run it from the skill directory, or with a path to this skill's `scripts/lint.sh`. It requires `vale` on `PATH`, installed via the repository root's `install.sh`. It exits `3` with an install hint when `vale` is missing. Treat that as "skip linting," not a failure. Latin abbreviations are the only error-level rule, and apply in every mode. Everything else is a warning or suggestion that needs a human read, not an automatic block.

Read [references/linting.md](references/linting.md) for the full rule layout, before adding or changing a rule.

## Cross-cutting rules (all modes)

The [kernel](references/contracts/kernel/v1.md) owns meaning preservation (negation, conditions, sequence, numbers, identifiers, commands, code, quotations) and idea reduction for every mode. These rules cover what it does not:

- Use headings, bullet lists, numbered steps, or tables wherever the source has a natural grouping, sequence, or set of alternatives. A reader scans structure faster than a paragraph, in every mode including `prose`. Reserve plain paragraphs for content that is genuinely a single flowing argument.
- Never guess at meaning to compress further — an unresolved ambiguity is a failure in every mode, most of all in `compact`.

Read [the changelog](changelog.md) only when reviewing this skill's version history or preparing a revision. Read [gaps.md](gaps.md) only when reviewing what the linter cannot check.
