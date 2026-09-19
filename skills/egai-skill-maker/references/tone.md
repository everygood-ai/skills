# Tone Contracts

## Kernel `[tone-contract]`
**Canonical Kernel — v1**

Apply before drafting, in every tone mode:

1. Reduce the input to distinct facts, decisions, constraints, and links.
2. Drop setup, repetition, restatement, and summary that add no information.
3. Preserve meaning exactly: negation, logical connectives, sequence
   markers, numbers, units, identifiers, commands, code, and quotations.
4. Apply the selected profile's rules.
5. Review the result against this kernel and the selected profile. Repair
   every violation before delivery.

This kernel governs meaning and idea reduction only. It defines no output
form; mode profiles define form.
## README tone `[tone-contract]`
**Prose — v1**

Target: product documentation, guides, and descriptions for a general reader.

- Write complete sentences. Avoid fragments.
- Give each sentence exactly one idea, 10-20 words. Split a sentence
  needing a semicolon, an em-dash aside, or extra subordinate clause.
- Present enumerable content as a heading, list, or table, not a
  paragraph.
- No summary paragraph repeating the body. No hedging phrases unless the
  hedge is the point.
- Prefer plain, common words over rare synonyms. Explain technical terms
  at first use.
- Use active voice by default. Use passive only when the actor is unknown
  or unimportant.
- Name the same action or concept the same way throughout. Never
  introduce a synonym for something already named.
## Changelog tone `[tone-contract]`
**Terse — v1**

Target: procedures, manuals, API and technical docs, and warnings where the
reader needs the point fast.

- Give each line or short sentence exactly one idea; state it and stop.
- Group related lines under short headings, most important line first.
- Keep sentences short — split a line into two if it needs a semicolon to
  hold two ideas.
- Write instructions in imperative form: "Set X to Y," not "X should be
  set to Y."
- Use active voice by default; use passive only when the actor is unknown
  or unimportant.
- Use numbered steps for a sequence, and a table for anything with
  repeated structure, such as options or parameters.
