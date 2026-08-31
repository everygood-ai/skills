# Domain and Scale Modeling

## Domain-driven design

- Identify the bounded contexts in the problem: the areas where a term means one specific thing, with one team or component responsible for its rules. A term can mean different things in different parts of the system. For example, "customer" means one thing for billing and another for support. That difference marks a context boundary, not a shared model to unify.
- Use the domain experts' own vocabulary, the ubiquitous language, in the document. A model that needs translation between the document and the people who understand the domain has already drifted from it.
- Model the aggregates and entities that the business rules actually constrain, not every noun in the problem statement. An aggregate should enforce one consistency rule as a unit. If two candidate aggregates never need to change together, they are two aggregates.
- Align service and team boundaries to bounded contexts, not to org-chart convenience alone. A boundary that splits one business rule across two teams and two deployments creates an ongoing coordination cost. Name that cost explicitly if the design accepts it.

## Distributed systems judgment

- State each consistency requirement in the language of the business rule it protects. For example: "the balance must never go negative" or "search results may lag writes by up to five minutes". Do not state it as an abstract preference for "strong" or "eventual" consistency.
- Name where the design accepts eventual consistency, and how a reader, whether a user, a downstream system, or an operator, will observe the resulting lag or temporary inconsistency.
- Identify every single point of failure and every partial-failure path: what happens when one dependency is slow, unavailable, or returns a partial result. A design that describes only the success path is incomplete.
- Design retries, timeouts, and idempotency together. A retry without idempotency risks duplicate side effects. Idempotency without a bound, such as a queue depth, a retry budget, or a circuit breaker, risks cascading failure into a struggling dependency.
- Plan capacity in the units the system actually depends on: requests per second, data volume growth, connection counts, and whichever resource will run out first. Do not size a design only in requests per second when storage growth or a shared downstream limit will bind first.
- Include an operational story. State the signals that reveal the system is unhealthy, how it degrades under partial failure or overload, and how a rollout can be reversed if it fails after release.

## Data ownership

- Give each piece of data exactly one system of record. A design where two systems can both write the authoritative value needs an explicit reconciliation rule, or it carries a latent bug.
- State who owns a shared reference, such as a customer ID or a product catalog entry, across contexts. State how other contexts are allowed to use it: by copy, by reference, or by call.
