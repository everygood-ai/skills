# Structural Linting

`scripts/lint.sh` wraps [Vale](https://vale.sh) with a bundled style package under `scripts/vale/styles/`. Vale requires this exact `StylesPath/StyleName/RuleName.yml` layout, so the nesting is fixed by the tool, not a choice made here.

## Layout

- [scripts/lint.sh](../scripts/lint.sh) — entry point; resolves the mode to a config and calls `vale`.
- [scripts/vale/prose.vale.ini](../scripts/vale/prose.vale.ini) — loads `EGAICommon` + `EGAIProse`.
- [scripts/vale/terse.vale.ini](../scripts/vale/terse.vale.ini) — loads `EGAICommon` + `EGAITerse`.
- [scripts/vale/compact.vale.ini](../scripts/vale/compact.vale.ini) — loads `EGAICommon` + `EGAITerse` + `EGAICompact`.
- `scripts/vale/styles/EGAICommon/` — rules shared by every mode: [LatinAbbreviations.yml](../scripts/vale/styles/EGAICommon/LatinAbbreviations.yml) (error).
- `scripts/vale/styles/EGAIProse/` — [SentenceLength.yml](../scripts/vale/styles/EGAIProse/SentenceLength.yml) (suggestion, 30+ words), [StackedClauseHint.yml](../scripts/vale/styles/EGAIProse/StackedClauseHint.yml) (suggestion, flags semicolons and em-dashes — prose mode wants these split into separate sentences).
- `scripts/vale/styles/EGAITerse/` — [NoSemicolons.yml](../scripts/vale/styles/EGAITerse/NoSemicolons.yml) (warning), [SentenceLength.yml](../scripts/vale/styles/EGAITerse/SentenceLength.yml) (warning, 25+ words), [PassiveVoiceHint.yml](../scripts/vale/styles/EGAITerse/PassiveVoiceHint.yml) (suggestion).
- `scripts/vale/styles/EGAICompact/` — [FillerWords.yml](../scripts/vale/styles/EGAICompact/FillerWords.yml) (suggestion), [SymbolLegendReminder.yml](../scripts/vale/styles/EGAICompact/SymbolLegendReminder.yml) (suggestion, flags `→` and `!=`).

## Adding or changing a rule

- Add a new mode-specific check as a new `.yml` file under the matching `EGAIProse`/`EGAITerse`/`EGAICompact` folder; add a shared check under `EGAICommon`.
- Existence-rule tokens for non-word characters (`;`, `→`, `!=`, `—`) need `nonword: true`, or Vale silently matches nothing.
- Existence-rule tokens ending in a literal `\.` (abbreviations like `e.g.`) need the period made optional (`\.?`), because Vale's sentence tokenizer strips a trailing abbreviation period before the regex sees it — `\be\.g\.` never matches, `\be\.g\.?` does.
- After editing a rule, run `scripts/lint.sh MODE FILE` against a small sample containing and lacking the target text to confirm the rule fires and does not false-positive.
- Whether ideas were actually deduplicated, and whether structure (headings/lists/tables) was used where the content called for it, cannot be linted — see [gaps.md](../gaps.md).

## Mechanical-rule coverage audit (kernel/profile contracts, Phase 6 Task 18)

Audited `references/contracts/kernel/v1.md`, `contracts/prose/v1.md`, `contracts/terse/v1.md`, `contracts/compact/v1.md`, and `contracts/terse-report/v1.md` against the mechanical-check categories named in the tone-improvements plan's "Move mechanical checks into scripts":

- **Sentence-length thresholds** — covered: `EGAIProse/SentenceLength.yml` (prose), `EGAITerse/SentenceLength.yml` (terse and compact, since `compact.vale.ini` loads `EGAITerse`).
- **Semicolons** — covered: `EGAIProse/StackedClauseHint.yml` (prose, also flags em-dashes) and `EGAITerse/NoSemicolons.yml` (terse and compact).
- **Latin abbreviations** — covered: `EGAICommon/LatinAbbreviations.yml` (every mode, `e.g.`/`i.e.`/`etc.`/`et al.`/`vs.`). Running `scripts/lint.sh compact contracts/compact/v1.md` found `contracts/compact/v1.md` used `e.g.` in its own body text; fixed by rewording to "such as."
- **Undefined or inconsistently used symbols** — partially covered: `EGAICompact/SymbolLegendReminder.yml` flags `→` and `!=` as a reminder to define them in a legend, but it is an existence check, not state tracking — it cannot detect whether a symbol was actually defined before first use, or reused for two meanings. No contract file introduces a symbol beyond what this rule already flags, so no coverage gap exists against current content.
- **Repeated adjacent lines or headings** — not coverable with this linter: Vale's rule types here (`existence`, `occurrence`) match a fixed regex token against the document; none can compare one line's content against another's to detect duplication, and Vale's Go regex engine has no backreference support to express that in a single token rule either. No rule added.
- **Paragraph and list-shape constraints** — not coverable with this linter: existence/occurrence rules match tokens, not block-level Markdown structure (paragraph vs. list vs. table). No rule added.

No new rule file was needed; the one real defect found (the `e.g.` usage above) was a content fix, not a linter gap. `scripts/lint.sh` runs clean (no errors) against all three mode-matched contract files (`prose/v1.md` in `prose` mode, `terse/v1.md` in `terse` mode, `compact/v1.md` in `compact` mode) as of this audit.
