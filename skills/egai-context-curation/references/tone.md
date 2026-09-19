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
## Context file tone `[tone-contract]`
**Compact — v1**

Target: dense requirements, compact project context, and system-prompt-style
text where token density outweighs grammaticality.

- Write sentence fragments and label:value pairs instead of full clauses,
  such as "Status: ready." Each fragment must resolve to exactly one
  reading.
- Drop articles ("a," "an," "the"), the linking verb "be," and auxiliary
  verbs when unambiguous. Prefer bare stems or simple tense.
- Omit a repeated subject or verb across parallel items when the lead-in
  makes it recoverable.
- Allow noun stacks over three words when unambiguous. Hyphenate compound
  modifiers to show grouping.
- Define any symbol in a legend before its first use (`→` then, `+` and),
  and never reuse a symbol for two meanings in the same document.
## Report tone `[tone-contract]`
**Terse Report — v1**

- Lead with the outcome.
- State each result once.
- Include only changed artifacts, verification, and unresolved issues.
