# Context maintenance model

`egai-context-curation` owns compact, evidence-based `.context/` files and their routing links. It documents current cross-file knowledge that takes inference to establish. It does not own implementation plans, general documentation, or skill-local runtime instructions.

## Capture boundary

- Capture a fact only when multiple files or relationship inference are required.
- Keep current behavior and durable constraints. Remove stale claims during every authorized update.
- Keep lifecycle mechanics, script behavior, and skill-local invariants in the owning skill's maintainer documentation.
- Keep `main.md` as the index. Topic files own architecture, domain, rules, testing, interfaces, or project-shaped splits.

## Operating flow

1. Resolve mode, source path, context path, scope, and the lock file.
2. Read only evidence needed for the scoped context files.
3. Remove stale or unsupported claims before adding current facts.
4. Update repository-instruction links when the mode permits writes.
5. Validate every changed context file against the flat 500-line ceiling.

## Lock and applicability rules

`context-lock.json` records `domainCapture`, `interfacesCapture`, and applicable specification paths. Incremental updates reuse those decisions. From-scratch runs detect them. Stale audits recheck them and report changes. `domain.md` and `interfaces.md` may be absent when their independent applicability tests resolve to skip.

## Script boundary and verification

`scripts/validate-context-lengths.sh` checks only Markdown line counts and file existence. It does not assess evidence quality, routing, or factual accuracy. Run it from the skill directory with the context directory and, for scoped work, each changed basename.
