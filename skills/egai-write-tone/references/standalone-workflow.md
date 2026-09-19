# Standalone Direct-Use Workflow

Follow this workflow when a user directly asks `egai-write-tone` to write or
rewrite text. A consumer skill that already knows its required profile does
not need this file — it loads its own compiled contract instead.

1. Determine the mode.
   - Use it directly if the request names one explicitly: `prose`, `terse`,
     `compact`, or a synonym.
     - "readable docs" → `prose`
     - "dense" / "on-point" / "technical spec" → `terse`
     - "telegraphic" / "caveman" / "compact context" → `compact`
   - Otherwise, propose a mode from the content type:
     - User-facing docs and feature explanations → `prose`
     - Procedures, manuals, API/technical docs, warnings → `terse`
     - Requirements, specs, project-context files, system prompts →
       `compact`
   - Confirm the proposed mode with the user before writing. The wrong mode
     changes the whole output.
2. Before drafting, work out the distinct ideas in the source: facts,
   decisions, numbers, causal links, each counted once. Merge or drop
   anything that only restates a point already made, sets up what you are
   about to say, or summarizes what you just said. Write from this reduced
   set of ideas, not from the original wording. This step is why the output
   ends up shorter without losing meaning — do not skip it, even for a short
   source.
3. Load `references/contracts/kernel/v1.md` plus only the selected mode's
   current-revision profile file:
   - `prose` → `references/contracts/prose/v1.md`
   - `terse` → `references/contracts/terse/v1.md`
   - `compact` → `references/contracts/compact/v1.md`

   Never load the full `contracts/` directory — only the kernel and the one
   profile the confirmed mode selected. Draft from the reduced idea set,
   following the kernel and that profile's rules exactly.
4. When `vale` is installed, run `scripts/lint.sh MODE FILE` (see
   [Structural linting](../SKILL.md#structural-linting)) and fix every
   error-level finding. Warnings and suggestions are advisory — apply them
   when they hold up, and note the ones you deliberately leave.
5. Review the draft against the kernel's review step and the selected
   profile's rules (kernel step 5). Fix anything that fails before
   delivering.
6. State which mode you used. In `compact` mode, also state the symbol
   legend if one was used, so the reader can decode it.
