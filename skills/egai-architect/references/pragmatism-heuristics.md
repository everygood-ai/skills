# Pragmatism Heuristics

A staff engineer earns trust by matching a design's complexity to the problem's real requirements, not to what is fashionable or to the largest future the team can imagine.

## Before adding anything

Before recommending a new service, a new datastore, a new messaging system, or a new layer of abstraction, ask in order:

1. Does an existing service, datastore, or library already solve this well enough?
2. Does the stated scale need this now, or only in a hypothetical future nobody has committed to?
3. Would the simpler alternative fail a requirement that is actually in scope, or only a requirement someone might add later?
4. Who will operate this addition in production, and have they agreed to?

Recommend the addition only when a real, current requirement fails every simpler alternative.

## Signs of overengineering

- A microservice with one caller and no independent scaling, deployment, or ownership need.
- A generic plugin or abstraction layer built for a second use case that does not exist yet.
- A new technology chosen for its reputation rather than for a requirement the current stack cannot meet.
- A design built for a hundred times the current load, with no stated timeline or commitment to reach it, at the cost of meeting today's requirements later or more expensively.
- A configuration or extensibility point with no second configuration that will ever use it.

## Signs of underengineering

Pragmatism also means recognizing where complexity is load-bearing, not optional:

- A single point of failure in a path the business has already called critical.
- A data model that cannot express a rule the domain experts described as a hard constraint.
- A synchronous call chain across a boundary that the stated latency or availability target cannot tolerate.
- A migration or rollout with no reversible step, on a system the requirements call sensitive to irreversible change, such as money movement, user data deletion, or security.

## Weigh scrutiny to the cost of being wrong

Apply the heaviest scrutiny to decisions that are hard or expensive to reverse after launch, such as:

- Data models.
- API contracts.
- Service and team boundaries.
- Consistency guarantees.
- Anything that changes what other systems must promise.

Apply lighter scrutiny to decisions that are cheap to revisit later, such as internal function boundaries, naming, and configuration values.

## State tradeoffs in concrete terms

Reject a tradeoff written in marketing language, such as "more scalable" or "cleaner", when it carries no concrete cost and benefit. A usable tradeoff names what is gained, what is given up, and the condition under which the choice would flip. For example: added latency in the failure path in exchange for no dual write, or added operational surface in exchange for independent deploys.
