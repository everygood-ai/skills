# egai-write-tone

Writes or rewrites text at one of three controlled tone levels: `prose`, `terse`, or `compact`.

## Concept

Every level answers the same question — is this unambiguous and free of restated content? — with a different word budget. The skill always reduces a source to its distinct ideas (facts, decisions, causal links, each counted once) before drafting, then writes from that reduced set following the rules of the chosen mode. That reduction step is what makes the output shorter without losing meaning — the modes are not just "the same text, trimmed."

The three modes are not interchangeable presets of one rule set. Each has its own reference file and its own grammar:

| Mode | Use for | Form |
|---|---|---|
| `prose` | Product docs, feature descriptions, guides | Full sentences, one idea per sentence (~10-20 words) |
| `terse` | Procedures, manuals, API/technical docs, warnings | One idea per line, imperative for instructions |
| `compact` | Requirements, project context, system-prompt text | Fragments and key:value pairs, breaks normal grammar |

Across all modes: negation (`not`/`no`/`never`) and logical connectives (`if`/`unless`/`and`/`or`/`except`) are never dropped, and code, commands, identifiers, numbers, and quoted text stay exact.

## Examples

Same source, three outputs:

> Source: "It's worth noting that when a user submits a form, the system will first validate all of the required fields, and if any of them are missing or invalid, it will then display an error message to the user explaining what went wrong, so that they can go back and fix it before trying to submit again."

**prose**

> When a user submits a form, the system validates all required fields. If any field is missing or invalid, the system displays an error message explaining the problem. The user can then fix the field and resubmit.

**terse**

> ## Form validation
> - Validate required fields on submit.
> - If a field is missing or invalid, show an error message explaining why.
> - User fixes the field and resubmits.

**compact**

> Submit → validate required fields. Invalid/missing field → show error msg (reason) → user fixes + resubmits.

## Workflow

1. Determine the mode — from an explicit request (`prose`, `terse`, `compact`, or a synonym like "dense" or "telegraphic"), or proposed from the content type and confirmed with the user.
2. Reduce the source to its distinct ideas before drafting.
3. Draft following the chosen mode's reference file: [prose.md](references/prose.md), [terse.md](references/terse.md), or [compact.md](references/compact.md).
4. Run `scripts/lint.sh MODE FILE` if `vale` is installed, and fix error-level findings.
5. Run the mode's self-check against the result.

See [SKILL.md](SKILL.md) for the full instructions this skill runs on.
