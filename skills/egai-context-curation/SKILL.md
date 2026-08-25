---
name: egai-context-curation
description: Build and maintain compact, evidence-based Markdown context for a project or codebase area. Use when asked to extract context from scratch, update context after source changes, improve existing context quality, or audit context for stale claims. Do not use for implementation planning, code changes, or general documentation that is not maintained as project context.
metadata:
  version: "3.1.1"
---

# EGAI Context Curation

Maintain a small, indexed context set that records knowledge which takes time to discover or infer from the codebase. Capture current evidence, not aspirations or obvious file contents.

## Resolve the Target

Determine these inputs before editing:

- **Mode** is `incremental-update`, `from-scratch`, `improve-existing`, or `audit-stale`. Infer it from the request when unambiguous.
- **Source path** is the root of the project or area being documented. Use the repository root only when the request does not identify a narrower area.
- For **Context path**, use an explicit path first, then a location declared by repository instructions, then an existing context directory associated with the source path. For a new context set with no convention, use `SOURCE_PATH/.context/`.
- **Scope** is one context filename or `full`, and it defaults to `full`.
- **Changed files** must be a complete list for `incremental-update`. Derive it from the current task or version-control diff only when the requested boundary is clear.
- Read the lock file (`context-lock.json` in the context directory) when present, before acting. A user-declared override — in repository instructions or the lock file — always wins over fresh detection.

Honor repository instructions when they define different filenames, schemas, or size limits. Otherwise use the context set in this skill.

Before writing any file, invoke the `egai-write-tone` skill and follow its full workflow, not only the target mode's reference file. Reduce the content to its distinct ideas first, then draft from that reduced set. Draft every context file in `compact` mode; the 500-line ceiling assumes that density. Draft every other text output this skill produces, such as a completion report, an audit finding, or a proposed-entry summary, in `terse` mode.

## Link from Repository Instructions

Keep the project's root instruction files pointing at the current context set, so a future session finds it without searching.

- Locate the repository root: the nearest ancestor directory containing `.git`, or the project root when no version control is present.
- At that root, check `AGENTS.md` and `CLAUDE.md` independently. For each one, add or update one line linking to this run's `main.md`, relative to the root:
  - Insert it as a Markdown bullet under a `## Project Context` heading. Create that heading at the end of the file if it is absent. Create the file itself, containing only that heading and bullet, when the file does not exist.
  - Use this bullet format: `- [AREA_LABEL context](RELATIVE_PATH_TO_MAIN_MD) — durable project knowledge; read before a non-trivial change in AREA_LABEL.` Set `AREA_LABEL` to the repository's directory name when Source path is the repository root, or to the area's path relative to the root otherwise.
  - Touch only the `## Project Context` heading and its bullets. Leave the rest of the file's structure and content unchanged. When the heading already lists a different area's bullet, keep it and add or update only the bullet for the current area.
- Run this check once per invocation, after the context path is finalized, in every mode. **Audit for Stale** follows its own report-then-authorize rule instead: report a missing or stale link as a mismatch, and only write it when the request authorizes edits.

## Operating Modes

### Incremental Update

Use after an implementation change.

1. Read the changed-file list, the existing context index, and `domainCapture`/`interfacesCapture` from the lock file — do not re-derive them.
2. Map each changed source area to the affected context files, per `main.md`'s index.
3. Read the affected source files, directly relevant tests or manifests, and only the context files that may need updates.
4. Remove claims made stale by the changes before adding new findings.
5. Edit the minimum necessary sections. Preserve valid content and user-authored structure.
6. Validate the affected context files with the bundled length validator.
7. Report the context files changed and any uncertainty that remains.
8. Apply [Link from Repository Instructions](#link-from-repository-instructions).

Do not rewrite an existing context file wholesale when a section-level edit is sufficient. If the changed-file list is incomplete or mixes unrelated work, identify the gap before writing.

### From Scratch

Use to create a context set for an undocumented project or area.

1. Inspect the source tree, key entry points, manifests, configuration, tests, and machine-readable contract specifications.
2. Inspect recent history for the source path when version control is available and history clarifies current structure or conventions.
3. Run spec detection and the `domain.md`/`interfaces.md` applicability checks in [Capture and applicability](#capture-and-applicability). Write the resulting `domainCapture`, `interfacesCapture`, and any `specPaths` to the lock file.
4. Create the context directory and populate `main.md`, `architecture.md`, `rules.md`, `testing.md`, and any file that step 3 marked applicable, per [Context Set](#context-set) and limited by the requested scope. Skip `domain.md`/`interfaces.md` entirely — no stub, no index entry — when their applicability check resolved to skip.
5. Record only decisions and behavior supported by current project evidence.
6. Mark a claim that is inferred but not directly established with `[inferred — verify]`.
7. Use `# TODO: insufficient evidence — verify` instead of inventing content for a required file or section.
8. Apply [Link from Repository Instructions](#link-from-repository-instructions), unless this is a dry run.

When the user requests a dry run, propose entries grouped by target file and make no file changes.

### Improve Existing

Use when the context exists but is unclear, oversized, incomplete, duplicated, or hard to navigate.

1. Read the index, the requested context files, and enough source evidence to verify proposed edits.
2. Identify claims that are vague, duplicated, obvious from one file, unsupported, misplaced, or beyond the 500-line ceiling.
3. Replace them with concise, source-verifiable statements in the correct file.
4. Restore missing index links and required sections only when evidence exists.
5. Validate the scoped files against the flat length ceiling.
6. Preserve useful project-specific organization unless it conflicts with repository instructions or factual accuracy.
7. Apply [Link from Repository Instructions](#link-from-repository-instructions).

Improvement is not permission to expand the documented scope or redesign the project.

### Audit for Stale

Use to compare existing context against the current source tree.

1. Check paths, symbols, commands, dependencies, flows, rules, lifecycle states, and contracts named in the scoped context.
2. Re-run the `domain.md`/`interfaces.md` applicability checks ([Capture and applicability](#capture-and-applicability)) against current project state — do not only re-verify existing claims. If a file recorded `not-applicable` now shows a signal, flag it for capture (report-only unless the request authorizes edits, per existing mode rules) and propose updating the lock file. Flag the symmetric case too: a captured file whose signal has disappeared.
3. Check whether the repository root's `AGENTS.md`/`CLAUDE.md` link to `main.md` for every documented area, per [Link from Repository Instructions](#link-from-repository-instructions). Flag a missing or stale link as a mismatch.
4. Classify each mismatch as stale, unsupported, ambiguous, or still valid.
5. Report the evidence and proposed removal or correction for every mismatch.
6. Apply corrections only when the request authorizes edits, including a flagged link. If the request asks only for an audit, leave files unchanged.
7. After edits, recheck links, paths, names, the flat length ceiling, and contradictions across the context set.
8. Run the bundled length validator on every scoped context file.

## Source-to-Context Mapping

| Changed source area | Context files to inspect |
|---|---|
| Entry points, runtime, language, framework, major dependencies | `main.md` |
| Modules, folders, runtime flows, integrations | the relevant architecture-topic file(s) per `main.md`'s index |
| Business rules, state transitions, user flows, data lifecycle | the relevant domain-topic file(s) per `main.md`'s index, when `domainCapture` is `code-derived` |
| Non-obvious implementation invariants and conventions | `rules.md` |
| Test commands, frameworks, naming, coverage, high-risk scenarios | `testing.md` |
| Exposed or consumed endpoints, events, shared types, specifications | the relevant interfaces-topic file(s) per `main.md`'s index, when `interfacesCapture` is `code-derived` |
| First extraction for a new area | `main.md` plus every applicable topic file per [Capture and applicability](#capture-and-applicability) |

Inspect more than one context file when a change crosses concerns. Do not update a file merely because it appears in the mapping. Update it only when its current claims or useful coverage changed.

A flow's concrete technical detail (endpoints, queues, auth mechanisms, library names) belongs in `architecture.md`. The same flow's domain meaning (entity state changes, business decisions, user intent) belongs in `domain.md`. When a flow spans both, record the technical detail once, in `architecture.md`, and give `domain.md` only the domain-level shape.

## Context Set

### Lock file

Path: the context directory plus `context-lock.json` (for example `.context/context-lock.json`) — a JSON state file next to, not inside, the content it governs.

Fields:

- `domainCapture`: `spec-backed`, `code-derived`, or `not-applicable`.
- `interfacesCapture`: `code-derived` or `not-applicable`. No `spec-backed` value — `interfaces.md` has no document-existence skip axis.
- `specPaths` (optional array): populated only when a detected or declared PDD (or equivalent) drove `domainCapture: spec-backed`. Omit when the spec is not locally readable. Not used for `interfacesCapture`; a machine-readable spec found for `interfaces.md` is recorded inside `interfaces.md` itself, not in the lock file.

No split-tracking field. Splitting state lives entirely in `main.md`'s index.

**From Scratch** writes the lock file after running detection (see [Operating Modes](#operating-modes)). **Incremental Update** and **Audit for Stale** read `domainCapture`/`interfacesCapture` from it instead of re-deriving them each run; **Audit for Stale** additionally re-runs the applicability checks and proposes lock file updates when the verdict changed.

### Capture and applicability

`architecture.md`, `rules.md`, and `testing.md` are always captured. No capture-mode or applicability test ever skips them.

`domain.md` and `interfaces.md` are captured or skipped per an independent per-file test, run during **From Scratch** and re-run during **Audit for Stale**.

**`domain.md`**

- Before drafting `domain.md` only, search headlessly for an authoritative product/domain design document (a PDD or equivalent, including a repo-declared authoritative doc). No user prompt.
- If found: skip `domain.md` entirely — no stub, no index entry. Record `domainCapture: spec-backed` and the document's path(s) in `specPaths`.
- If not found: capture it only when the project shows a domain signal — entities with defined identity, state, or lifecycle; rules governing their transitions; or significant end-to-end user or system flows. Record `domainCapture: code-derived`.
- No spec and no signal: skip it. Record `domainCapture: not-applicable`.

**`interfaces.md`**

- No document-existence skip axis at all, and no parallel document search to `domain.md`'s. A spec never skips this file.
- Capture it whenever the project shows a boundary-contract signal — a network or event surface, a CLI command surface, or an exported machine-readable schema. Record `interfacesCapture: code-derived`.
- No signal: skip it — no stub, no index entry. Record `interfacesCapture: not-applicable`.
- When a machine-readable spec (OpenAPI, AsyncAPI, GraphQL SDL, protobuf, JSON Schema) exists, it shapes the file's content instead of skipping it: write mostly paths to the spec plus a short summary — see that file's "paths to authoritative machine-readable specifications" bullet — instead of reconstructing contracts from code.

Read both signals broadly, wider than "business application" or "networked service." A CLI command surface counts as a boundary contract. A release or task lifecycle counts as a domain signal, the same as a commercial business domain. A skills library or CLI tool can carry a real domain and a real interface surface under these broader signals; do not narrow either test back to the two literal categories.

Detection during **From Scratch** is headless: search the project for an authoritative design document and check the signals above without prompting the user. A user-declared override — in repository instructions or the lock file — always wins over detection.

### Splitting

`main.md` is the single index for an open-ended file set, not a fixed six. The five defaults below — architecture, domain, rules, testing, interfaces — are a starting set, not a ceiling.

Split a topic into multiple named files when the project's own shape divides it, not because a file merely runs long. Worked example: a repo with a real frontend and a real backend gets `frontend-architecture.md` and `backend-architecture.md` in place of one `architecture.md`. A CLI-only repo has no such split and keeps one `architecture.md`.

Name a split-off file by its actual content or shape (`frontend-architecture.md`, `payments-domain.md`), never a numbered or generic suffix (`architecture-2.md`, `architecture-extra.md`).

Every context file — default or split-off, including `main.md` itself — must stay at or under 500 lines, counting every physical line. This is a hard backstop, not a target to fill: hitting it forces a split, since there is no per-file limit left to raise.

### `main.md` — Identity and Index

Include:

- Project or area name.
- Language, framework, and major libraries on one line.
- Principal entry points on one line.
- Last verified date.
- A relative link to every other context file present, each with a one-line justification for opening it — not just its topic. State what the reader would come to that file needing, not only what it contains.

  - Weak: `[architecture.md](architecture.md) — internal structure.`
  - Strong: `[architecture.md](architecture.md) — read before changing cross-module data flow; covers request routing and integration boundaries.`

This index is the sole routing mechanism for the context set — content files carry no frontmatter of their own. A vague entry breaks discovery, not just navigation.

Exclude full file lists, dependency trees, and code snippets. Keep the file under the 500-line ceiling; in practice it stays far shorter, since it only indexes.

### `architecture.md` — Internal Structure

Always captured. Include:

- Key folders or files grouped by purpose, named by purpose or file path rather than an internal identifier such as a component, class, hook, or variable name. Those identifiers drift on rename.
- Significant runtime flows expressed from source through major steps to destination.
- External or cross-area integration points.

Exclude business rules, test guidance, code, and contract schemas. Keep every file under the 500-line ceiling; split into topic-named files (see [Splitting](#splitting)) when the project's own shape divides its architecture, rather than letting one file grow toward the ceiling.

### `domain.md` — Rules and Flows

Captured only when [Capture and applicability](#capture-and-applicability) resolves `domainCapture` to `code-derived`. Skipped entirely — no stub, no index entry — when it resolves to `spec-backed` or `not-applicable`.

When captured, include only applicable sections:

- Business rules derived from implemented behavior.
- Entity states and allowed transitions.
- Significant end-to-end user or system flows.
- Creation, mutation, retention, and deletion of key data.

Exclude internal file structure, test patterns, code, and contract schemas. Keep every file under the 500-line ceiling; split by topic (see [Splitting](#splitting)) when the project's domain itself divides.

### `rules.md` — Implementation Rules

Always captured. Record non-obvious, source-established rules that future implementers must preserve. Write one `MUST` or `SHOULD` statement per bullet.

Exclude business rules, generic engineering advice, and rules already present in repository instructions. Keep the file under the 500-line ceiling.

### `testing.md` — Test Guidance

Always captured. Include:

- Exact test commands, or state that no test suite exists.
- Framework and version, captured only when reaching them takes more than the manifest: a version pinned outside it, a non-obvious dependency combination, or required setup such as stub order, transform inclusions, or mandatory global mocks.
- Test file and case naming conventions.
- Explicit coverage requirements when present.
- Non-obvious, high-risk scenarios that require protection.

Exclude test implementations, business rules, and contract schemas. Keep the file under the 500-line ceiling.

### `interfaces.md` — Boundary Contracts

Captured whenever [Capture and applicability](#capture-and-applicability) resolves `interfacesCapture` to `code-derived`. Skipped entirely — no stub, no index entry — only when it resolves to `not-applicable`. No document, machine-readable or prose, skips this file on its own.

Record current contracts that the project or area exposes or consumes:

- Operations and their purpose and authorization requirement.
- Emitted or consumed events and payload summaries.
- Shared types exported across boundaries.
- Paths to authoritative machine-readable specifications.

When a machine-readable spec (OpenAPI, AsyncAPI, GraphQL SDL, protobuf, JSON Schema) exists, let it shape the content: write mostly paths to the spec plus a short summary instead of reconstructing contracts from code.

Summarize contracts instead of copying request or response schemas. Exclude planned, internal-only, or nonexistent contracts. Keep every file under the 500-line ceiling; split by topic (see [Splitting](#splitting)) when the project's boundary surface itself divides.

## Validate Context Lengths

After creating or changing context files, run the bundled validator from this skill's directory:

```bash
bash scripts/validate-context-lengths.sh CONTEXT_DIRECTORY [CONTEXT_FILE ...]
```

Omit `[CONTEXT_FILE ...]` to validate every `.md` file present in the context directory — the actual file set, not a fixed list. For a scoped update, pass each affected basename, such as `main.md architecture.md`. The validator must pass before reporting a write as complete. It checks total physical lines in each scoped file against the flat 500-line ceiling; there is no frontmatter to check.

## Writing Standards

- Prefer one short bullet and a source path over a paragraph that restates implementation.
- Keep every claim verifiable against current project evidence.
- Capture a fact only when reaching it requires reading multiple files or inferring a relationship no single file states outright.
- In `architecture.md` and `domain.md`, state what exists. An absence claim such as "No Redux" drifts silently once the project adopts the pattern, because nothing about adoption removes it. Route a deliberate prohibition through `rules.md` instead, as a `MUST NOT` with its reason.
- Do not copy implementation blocks. Use exact syntax only when a one-line identifier or command is necessary.
- Keep each fact in one context file and link related material instead of duplicating it.
- Treat the context as current state. Remove contradicted, renamed, or obsolete information.
- Update and prune together so each context file remains under the 500-line ceiling.
- Preserve uncertainty explicitly. Never turn an inference into an unqualified fact.

## Completion Check

Before reporting completion, confirm:

- Every changed claim is supported by current source, tests, configuration, specifications, or repository instructions.
- No context claim contradicts the current code or another context file.
- All documented paths, links, commands, and symbols resolve when they are expected to exist.
- `scripts/validate-context-lengths.sh` passes for every created or changed context file.
- Content appears in the correct file and remains under the 500-line ceiling.
- Unaffected valid content and project-specific organization remain intact.
- Outside a dry run and an audit-only request, the repository root's `AGENTS.md` and `CLAUDE.md` each link to `main.md` for every documented area.
- The final report names the operating mode, inspected scope, files changed, and unresolved verification markers.

Read [the changelog](changelog.md) only when reviewing this skill's version history or preparing a revision.
