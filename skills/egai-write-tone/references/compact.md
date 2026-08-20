# Compact Mode — Dense Compression

Target output: intense requirements, compact project context, and system-prompt-style text where token density matters more than grammaticality, as long as meaning survives intact.

Compact mode goes further than [terse mode](terse.md) and deliberately breaks normal sentence grammar for it. It does not relax terse mode's demand for one unambiguous reading per statement — it raises it, because there is no room left to re-read a fragment two ways.

## Before you draft

Reduce the source to its distinct ideas first: facts, decisions, causal links, each named once. Drop anything that only restates, sets up, or summarizes a point made elsewhere. Draft from that reduced set, not from a looser first pass you plan to compress afterward.

## Never compress away

These carry meaning on their own. Dropping or implying them is a correctness bug, not a style choice:

- Negation: `not`, `no`, `never`, `must not`, `do not`. Never drop a negation or imply it through tone — write it out, every time.
- Logical connectives that change meaning: `if`, `unless`, `and`, `or`, `except`. Compress the words around them, not these.
- Numbers, units, thresholds, identifiers, code, commands, and quoted text. Keep them exact.
- Sequence and causality markers (`then`, `before`, `after`) — keep as words, or replace only through a symbol legend defined per the rule below.

## Compression techniques (allowed)

- Drop articles (`a`, `an`, `the`) when the referent stays unambiguous. `Use cache` not `Use the cache`.
- Drop the copula/linking `be` verb where the elision is standard shorthand. `Status: ready` not `The status is ready`.
- Drop auxiliary verbs and complex tenses; prefer bare stems or simple present/past.
- Write sentence fragments and label:value pairs instead of full clauses.
- Prefer bullet or key:value structure over prose paragraphs.
- Allow noun stacks longer than three words when unambiguous; hyphenate compound modifiers to show grouping.
- Omit a repeated subject or verb across parallel list items when the lead-in makes the ellipsis recoverable.
- Cut filler adjectives and adverbs that carry no decision-relevant information.
- Define a fixed symbol legend once per document if it helps (`→` then/leads-to, `+` and, `=` is/equals, `!=` not-equal, `>`/`<` more/less-than). Never introduce a symbol without defining it first. Never reuse a symbol for two meanings in the same document.

## Self-check

- Reread each compressed line: if removing this word could change what a reader concludes, restore it.
- Does every fragment resolve to exactly one reading, with no guessing required?
- Is every symbol used in the document defined in its legend, and used the same way everywhere?
- Are all numbers, identifiers, code, and quoted text still exact?
- Could this line still be misread by someone who only has the surrounding context, not the whole document? If so, it is too compressed.
