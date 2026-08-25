# egai-context-curation

Builds and maintains compact, evidence-based project context for AI agents.

## Concept

Records source-backed knowledge that takes time to discover or infer. Excludes aspirations, obvious file contents, copied implementation, and generic advice. Treats context as current state: update and prune together.

`main.md` routes agents to the context needed for a change. Topic files hold each fact once. Source, tests, configuration, specifications, and repository instructions provide evidence.

## Context set

| File | Captures | Presence |
|---|---|---|
| `main.md` | Project identity, entry points, stack, context index | Always |
| `architecture.md` | Structure, runtime flows, integrations | Always |
| `domain.md` | Implemented rules, states, data and user flows | Only with domain signal and no authoritative domain spec |
| `rules.md` | Non-obvious implementation invariants | Always |
| `testing.md` | Commands, conventions, setup, high-risk scenarios | Always |
| `interfaces.md` | Operations, events, shared types, specification paths | Only with boundary-contract signal |

File set open-ended. Split by project shape with topic names such as `frontend-architecture.md` or `payments-domain.md`. Maximum: 500 physical lines per file.

`context-lock.json` stores `domainCapture`, `interfacesCapture`, and optional `specPaths`. Incremental runs reuse these decisions. Audits recheck them.

## Modes

| Mode | Use |
|---|---|
| `from-scratch` | Create context for undocumented project or area |
| `incremental-update` | Synchronize context after complete known change set |
| `improve-existing` | Remove duplication, weak claims, and poor routing |
| `audit-stale` | Compare existing claims with current evidence |

## Capture rules

- Capture only facts requiring multi-file reading or relationship inference.
- Keep one fact in one context file.
- Mark inference not directly established as `[inferred — verify]`.
- Use `# TODO: insufficient evidence — verify` instead of invented content.
- Skip `domain.md` or `interfaces.md` when its applicability check resolves to skip.
- Keep repository `AGENTS.md` and `CLAUDE.md` linked to each context set's `main.md`.
- Draft context in `egai-write-tone` `compact` mode. Draft reports in `terse` mode.

## Example

```text
For each project area (frontend, mobile, and backend), spawn a fresh sub-agent. Have each follow `egai-context-curation` in `from-scratch` mode for its area.
```

## Workflow

1. Resolve mode, source path, context path, scope, and changed files.
2. Read repository instructions and existing `context-lock.json`.
3. Inspect only source evidence needed for scoped context.
4. Remove stale claims before adding current findings.
5. Validate changed files with `scripts/validate-context-lengths.sh`.
6. Verify repository-instruction links and report scope, changes, and uncertainty.

See [SKILL.md](SKILL.md) for full instructions. See [Context Curation for AI Agents](../../docs/post--egai-context-curation.md) for rationale and execution guidance.
