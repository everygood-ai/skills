# Terse Mode — Dense, On-Point Technical Writing

Target output: procedures, manuals, API/technical docs, and warnings where
the reader needs the point fast and does not need, or want, full prose.

## Before you draft

Reduce the source to its distinct ideas first: facts, decisions, causal
links, each named once. Drop anything that only restates, sets up, or
summarizes a point made elsewhere. Draft from that reduced set, not from a
looser first pass you plan to tighten afterward. Skipping this step is the
most common way terse output drifts into flowing prose. This holds even
when every individual sentence looks short.

## Rules

- One idea per line or short sentence. State it and stop — no elaboration,
  no restating in different words for emphasis.
- Group related lines under short headings. Order lines within a group by
  importance, most important first.
- Use numbered steps for a sequence, and a table for anything with repeated
  structure (options, tradeoffs, parameters).
- Keep sentences short — if a line needs a semicolon to hold two ideas,
  split it into two lines.
- Use imperative form for instructions ("Set X to Y", not "X should be set
  to Y").
- Use active voice by default. Use passive only when the actor is unknown or
  genuinely unimportant to the point.
- Do not use Latin abbreviations (`e.g.`, `i.e.`, `etc.`).
- Keep code, commands, identifiers, values, and quoted text exact and
  unmodified.

## Self-check

- Does every line carry exactly one idea?
- Reread the draft for drift back into flowing prose: a connective phrase
  ("which means," "this also," "as a result"), or a line that restates a
  point already made, for emphasis or transition. Cut or split it.
- Is related content grouped under a heading instead of scattered through
  the text?
- Would a table or numbered list replace any run of similar lines more
  clearly?
- Could any line be cut without losing something the reader needs?
