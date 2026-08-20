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
