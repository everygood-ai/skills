---
name: egai-write-tone
description: Write or rewrite text at one of three tone levels — prose (clear, scannable documentation for product docs and guides), terse (dense, on-point technical writing, one idea per line), or compact (maximum-density compression for requirements and context files, meaning must stay unambiguous). Use when asked to write, rewrite, tighten, or compress text to a stated tone or register, or to cut a wordy draft down to size without losing meaning. Do not use for casual conversational writing, marketing copy, or creative prose.
compatibility: Structural linting (scripts/lint.sh) requires the vale CLI; rules are verified with vale 3.17.1.
metadata:
  version: "3.0.1"
---

# EGAI Write Tone

Write or rewrite text at a controlled tone level. Every level answers the same question — is this unambiguous and free of restated content? — with a different budget for words.

| Mode | Use for | Governing rules |
|---|---|---|
| `prose` | Product documentation, feature descriptions, guides — text meant to read well and scan fast | [references/prose.md](references/prose.md) |
| `terse` | Technical/procedural documentation that needs to be dense and on-point | [references/terse.md](references/terse.md) |
| `compact` | Dense requirements, compact project context, system-prompt-style text | [references/compact.md](references/compact.md) |

Modes are not interchangeable presets of the same rules — each reference file is authoritative for its mode. Do not apply terse's line-by-line format to prose mode, and do not apply prose's full-sentence grammar to compact mode.

## Workflow

1. Determine the mode.
   - Use it directly if the request names one explicitly: `prose`, `terse`, `compact`, or a synonym.
     - "readable docs" → `prose`
     - "dense" / "on-point" / "technical spec" → `terse`
     - "telegraphic" / "caveman" / "compact context" → `compact`
   - Otherwise, propose a mode from the content type:
     - User-facing docs and feature explanations → `prose`
     - Procedures, manuals, API/technical docs, warnings → `terse`
     - Requirements, specs, project-context files, system prompts → `compact`
   - Confirm the proposed mode with the user before writing. The wrong mode changes the whole output.
2. Before drafting, work out the distinct ideas in the source: facts, decisions, numbers, causal links, each counted once. Merge or drop anything that only restates a point already made, sets up what you are about to say, or summarizes what you just said. Write from this reduced set of ideas, not from the original wording. This step is why the output ends up shorter without losing meaning — do not skip it, even for a short source.
3. Read the reference file for the chosen mode and draft from the reduced idea set, following that reference's rules exactly.
4. When `vale` is installed, run `scripts/lint.sh MODE FILE` (see [Structural linting](#structural-linting)) and fix every error-level finding. Warnings and suggestions are advisory — apply them when they hold up, and note the ones you deliberately leave.
5. Run the reference's self-check section against the result. Fix anything that fails before delivering.
6. State which mode you used. In `compact` mode, also state the symbol legend if one was used, so the reader can decode it.

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

- Use headings, bullet lists, numbered steps, or tables wherever the source has a natural grouping, sequence, or set of alternatives. A reader scans structure faster than a paragraph, in every mode including `prose`. Reserve plain paragraphs for content that is genuinely a single flowing argument.
- Keep code, commands, identifiers, numeric values, and quoted text exact and unmodified, regardless of mode.
- Never drop negation (`not`/`no`/`never`/`must not`) or logical connectives (`if`/`unless`/`and`/`or`/`except`) to save words — compress around them, not them.
- Never guess at meaning to compress further — an unresolved ambiguity is a failure in every mode, most of all in `compact`.
- When rewriting existing text, preserve its factual content. Tone level changes form, not meaning.

Read [the changelog](changelog.md) only when reviewing this skill's version history or preparing a revision. Read [gaps.md](gaps.md) only when reviewing what the linter cannot check.
