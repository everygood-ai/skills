# Review Checklist

Apply each section below that is relevant to the document under review. State explicitly when a section does not apply, and give the reason.

## Problem framing

- Does the document state the problem and its requirements before proposing a solution?
- Are functional and non-functional requirements, including scale, latency, availability, consistency, and compliance, both stated, not only the functional ones?
- Is the current and near-term scale stated in concrete numbers, not in vague terms such as "web scale" or "a lot"?

## Alternatives and tradeoffs

- Does the document name at least one rejected alternative for every hard-to-reverse decision?
- Are the tradeoffs stated in concrete terms, as described in [pragmatism-heuristics.md](pragmatism-heuristics.md#state-tradeoffs-in-concrete-terms), rather than in marketing language?
- Does the chosen option follow from the stated requirements, or does it look chosen first with requirements fitted to it afterward?

## Domain model

- Are the bounded contexts and their ownership clear? See [domain-and-scale-modeling.md](domain-and-scale-modeling.md#domain-driven-design).
- Does every piece of shared data have exactly one system of record?
- Do the service or team boundaries match the domain boundaries, or does the design split one business rule across two owners without naming the resulting coordination cost?

## Scale and reliability

- Does the design name its single points of failure and its partial-failure behavior, not only its success path?
- Is the consistency model stated in terms of the business rule it protects?
- Are retries, timeouts, and idempotency addressed together everywhere the design retries anything?
- Is capacity planned against the resource that will actually bind first?

## Operational readiness

- Does the design describe how it will be observed in production and how an operator will know it is unhealthy?
- Does the rollout include a reversible step, or does the document explain why one is not needed?
- Are migration and backfill steps, if any, described, including their failure and retry behavior?

## Complexity and scope

- Read [pragmatism-heuristics.md](pragmatism-heuristics.md) and flag any addition, such as a service, a datastore, or an abstraction, that the stated requirements do not yet justify.
- Flag any requirement the design under-serves: a stated hard constraint the chosen design cannot actually meet.

## Verdict

State one of three verdicts: approve, approve with changes, or revise before reproposal. List every blocking finding separately from suggestions. A blocking finding must trace to a stated requirement, a correctness risk, or an unacceptable operational risk, not to a stylistic preference.
