---
name: egai-skill-maker
description: Create, revise, and validate portable Agent Skills that follow the agentskills.io specification, including each skill's README.md. Use when asked to design a new skill, add a feature or mode to an existing skill, carry out a task plan, spec, or research document that changes a skill's SKILL.md, scripts, references, or assets, organize skill resources, fix skill metadata or structure, check a skill for specification compliance, or write or refresh a skill's README.md. Triggers even when the request names a plan or document rather than the skill directly, as long as the concrete change lands inside a skill directory.
compatibility: Requires the skill-validator CLI; commands documented here are verified with v1.6.0.
metadata:
  version: "2.4.0"
---

# EGAI Skill Maker

Create self-contained, portable Agent Skills. Follow the open Agent Skills specification rather than conventions from any single agent product.

## Workflow

1. Understand the intended capability from the request and a few representative tasks.
2. Inspect any existing skill and applicable project instructions before editing.
3. Choose a focused scope. Split unrelated capabilities into separate skills.
4. Decide which knowledge belongs in `SKILL.md` and which reusable content belongs in `scripts/`, `references/`, or `assets/`.
5. Record requested behavior that the specification or available tooling cannot represent in `gaps.md`. Never invent unsupported behavior.
6. Create or update the skill in the location requested by the user or required by the project. Do not assume a client-specific installation directory.
7. When the skill or its bundled scripts require an external CLI, add that CLI's Homebrew formula to `install.sh` at the repository root in the same change.
8. Invoke the `egai-write-tone` skill in `prose` mode and follow its full workflow on the prose in `SKILL.md` and its reference files, not only the mode's reference file. Then apply the [Language quality](#language-quality) rules on top of that pass. Skip this step only when `egai-write-tone` is unavailable in the current environment.
9. Choose one release increment for the complete delivered change. Invoke `egai-write-tone` in `terse` mode on the `changelog.md` entry and follow its full workflow. Then update `changelog.md` with the same version per [Version and changelog](#version-and-changelog).
10. Create or update `README.md` per [Write README.md](#write-readmemd).
11. Validate the skill through the bundled wrapper using the commands in this file. Also validate `changelog.md` with `scripts/validate_changelog.py`.
12. Test the skill on representative requests when practical, then refine unclear or brittle instructions.
13. Review the delivered skill's own workflow and rules for logic a deterministic script could handle instead of restated agent judgment, such as naming-rule checks, version-changelog consistency, frontmatter-field validation, or length thresholds. Never implement or auto-apply a candidate. Report each one in the final output: the specific logic, why it is deterministic, and the suggested script behavior. Omit this report only when the delivered skill has no such candidate.

Ask for clarification only when a missing decision would materially change the skill. Otherwise, make a reasonable assumption and proceed.

## Design the skill

Derive the skill from concrete usage:

- Identify phrases and tasks that should activate it.
- Identify nearby tasks that should not activate it.
- Determine the repeatable workflow the agent needs to follow.
- Add only knowledge that is non-obvious, domain-specific, or necessary for reliable execution.
- Prefer concise instructions over broad background material.
- Set the level of prescription to the risk. Use flexible guidance when many approaches work, and use exact steps or scripts when consistency is important.

Keep one coherent capability per skill. Keep the package limited to the skill and its resources unless the user explicitly requests a client-specific extension.

Default the new skill's own generated text output to `egai-write-tone` terse mode. Use a different register only when the skill's purpose calls for it:

- `prose` for long-form, user-facing writing.
- `compact` for dense context or requirement files.
- Plain unstyled text for a conversational domain.

State the chosen register explicitly in the new skill's `SKILL.md`.

## Create the directory

A skill is a directory containing `SKILL.md` and, when useful, bundled resources:

```text
skill-name/
├── SKILL.md
├── README.md     # Required compact documentation of the skill's logic
├── changelog.md  # Required version history
├── gaps.md       # Optional future specification gaps
├── scripts/       # Optional executable code
├── references/    # Optional documentation loaded on demand
└── assets/        # Optional templates, images, and data files
```

Additional files and directories are allowed, but create only files that directly support the skill.

`gaps.md` holds material for reviewing possible future specification changes, not current authoring guidance. Do not link it from `SKILL.md`'s runtime instructions merely to satisfy the orphan-resource check. See [Validate through the wrapper](#validate-through-the-wrapper) for the exemption.

Name the directory and skill with the same kebab-case identifier. The name must:

- Be 1-64 characters.
- Contain only lowercase ASCII letters, digits, and hyphens.
- Not start or end with a hyphen.
- Not contain consecutive hyphens.
- Match the parent directory name exactly.

## Write `SKILL.md`

Start the file with YAML frontmatter, followed by Markdown instructions.

### Frontmatter

Always include:

```yaml
---
name: skill-name
description: Describe what the skill does and when an agent should use it.
metadata:
  version: "1.0.0"
---
```

Apply these constraints:

- `name` is required. Follow the naming rules above.
- `description` is required and must be 1-1024 characters long. State both the capability and concrete activation contexts, and include discriminating keywords without making the scope overly broad.
- `license` is optional. Use a short license name or a reference to a bundled license file.
- `compatibility` is optional and, when present, must be 1-500 characters long. Include it only for real environment requirements, such as a specific product, system package, runtime, or network access. When it names an external CLI, also add that CLI's Homebrew formula to `install.sh` at the repository root.
- `metadata` is required by this authoring workflow. Include `version` as a quoted semantic-version string, and make sure any additional metadata keys and values are also strings. Prefer distinctive keys to reduce collisions.
- `allowed-tools` is optional and experimental. It declares pre-approved tools where supported, but never treat it as a restrictive allowlist or a portable security boundary.

Do not add unspecified frontmatter fields to a portable skill. If a user requests implementation-specific fields, clearly treat them as extensions that may not work in other clients.

Quote YAML values or use block scalars when punctuation could make them ambiguous. Keep metadata values strings.

### Version and changelog

Maintain the version and changelog as one atomic change:

- Put the current version in `metadata.version` using quoted `MAJOR.MINOR.PATCH` syntax.
- Start a new skill at `"1.0.0"`.
- Increment the version exactly once for the complete set of changes delivered together. Do not create intermediate versions for individual edits, files, or iterations within the same delivery.
- Use `PATCH` by default for fixes, wording improvements, clarifications, validation refinements, test additions, and other backward-compatible maintenance.
- Use `MINOR` for a backward-compatible capability addition that gives the skill a meaningful new workflow, output, tool, script, or supported use case. Existing valid uses must continue to work without changes.
- Use `MAJOR` only for a backward-incompatible release that requires existing users, callers, generated artifacts, or dependent skills to change. Examples include renaming the skill, removing or replacing supported behavior, changing required inputs or outputs, or deliberately rejecting inputs promised by the previous release.
- Do not choose `MAJOR` merely because an update is large, touches many files, rewrites instructions, adds stricter guidance, or feels important. Choose the smallest increment that accurately represents compatibility.
- When several changes of different levels ship together, use the highest required level once for the whole delivery.
- Create `changelog.md` beside `SKILL.md`.
- Keep changelog entries newest first as a Markdown list, one list per version.
- Invoke `egai-write-tone` in `terse` mode and follow its full workflow to draft every bullet. Skip this step only when `egai-write-tone` is unavailable in the current environment.
- Cap each bullet at 50 words or fewer. Split a version with more than one distinct change into several short bullets instead of one long sentence.
- Make the first changelog version match `metadata.version` exactly.
- When adopting this workflow for an unversioned skill, set it to `"1.0.0"` and summarize its current baseline.
- Do not change the version for inspection or validation that produces no file changes.
- Run `scripts/validate_changelog.py CHANGELOG_PATH` from the `egai-skill-maker` directory. Fix every reported issue before delivery.

Use this changelog format. A version with one change is a single bullet. A version with several changes is a version-only line followed by an indented bullet list:

```markdown
# Changelog

- `1.1.0`
  - Added CSV export.
  - Validated exported rows against the schema.
- `1.0.0` — Created the initial skill.
```

If compatibility is uncertain, identify the concrete previously supported behavior that would break. Without such a break, use `PATCH` or `MINOR`, not `MAJOR`.

### Document gaps

Create `gaps.md` only when a requested capability cannot be represented or validated by the current specification or tooling.

- Record one gap per brief bullet: name the missing capability and its practical consequence.
- Keep gaps non-normative. Do not convert them into invented frontmatter, directories, or guarantees.
- Do not record ordinary implementation work, defects the skill can fix, or speculative features without a concrete limitation.
- State a safe current workaround only when one exists.
- Do not link `gaps.md` from `SKILL.md`'s runtime instructions merely to satisfy the orphan-resource check. See [Validate through the wrapper](#validate-through-the-wrapper) for the exemption.
- Remove a gap when supported, then implement and validate the supported behavior.

### Write `README.md`

Create `README.md` beside `SKILL.md` for every skill this workflow creates or updates. `SKILL.md` is the operational instructions an activated agent runs. `README.md` is compact documentation of the same skill's logic for a reader, human or agent, who has not activated it.

- Create `README.md` when the skill is new. Update it whenever a change to `SKILL.md` alters what the skill does, when it activates, its input shape, or how it composes with other skills.
- State the skill's purpose, its trigger conditions, its workflow at a glance, and its relationship to other skills it invokes or is invoked by. Link to those skills' own `README.md` files.
- Link to `SKILL.md` and to any `references/` file for full procedural detail. Do not duplicate that detail in `README.md`.
- Keep `README.md` short enough to read in one sitting.
- Invoke `egai-write-tone` in `prose` mode and follow its full workflow to draft `README.md`. Skip this step only when `egai-write-tone` is unavailable in the current environment.
- Treat a missing `README.md`, or one left stale after a change to `SKILL.md`, as blocking, the same as a missing or mismatched `changelog.md` entry.

### Description

Treat `description` as the primary activation mechanism because agents normally see it before loading the body.

Write it to answer:

- What does this skill enable?
- When should it activate?
- What user language, file types, tools, or task contexts distinguish it?

Put activation guidance in `description`, not in a body section that is unavailable before activation.

### Body

Write direct instructions in imperative form. Include only material needed after activation, such as:

- A step-by-step workflow.
- Decision rules and safety boundaries.
- Commands or references to bundled resources.
- Concise examples where they prevent ambiguity.
- Important edge cases and validation steps.

Do not explain generic facts a capable agent already knows. Avoid filler, duplicated guidance, and historical notes about how the skill was created.

### Language quality

Draft with the `egai-write-tone` skill in `prose` mode, then check the result against these skill-specific rules, which `prose` mode does not cover:

- State the action or rule directly. Remove throat-clearing and commentary.
- Prefer specific verbs and concrete conditions over vague guidance.
- Use one interpretation per instruction. Define any term that could change execution.
- Distinguish requirements from recommendations with `must`, `never`, `should`, and `may` consistently.
- Remove repetition, redundant examples, hedging, and words that do not change behavior.
- Keep examples minimal and include them only when prose could be misread.
- Never use HTML tags, HTML comments, or angle-bracket placeholders in `SKILL.md`. Use plain Markdown and uppercase placeholder names such as `SKILL_DIRECTORY`.
- Read the final text once for ambiguity and shorten it without losing constraints.

## Use progressive disclosure

Design for three loading levels:

1. `name` and `description` are available for discovery.
2. The full `SKILL.md` body loads after activation.
3. Bundled resources load or run only when needed.

Aim for fewer than 300 lines in `SKILL.md`. Never deliver a `SKILL.md` longer than 500 lines. Keep only activation-time workflow, decisions, safety constraints, resource routing, and essential examples in `SKILL.md`.

Use the bundled validation wrapper as the sole length check. Its structure validation reports a warning when `SKILL.md` exceeds 500 lines or 5,000 tokens. Treat a warning that the file exceeds 500 lines as a blocking failure. Move non-core, detailed, or conditional content into focused files under `references/`. Rerun validation until that warning is absent. Do not waive or merely document an over-500-line result. Treat fewer than 300 lines as the authoring target even though the validator does not enforce that preferred size.

Move detailed or conditional material into focused resource files. In `SKILL.md`, state exactly when to read or use each resource.

Reference bundled files with paths relative to the skill root:

```markdown
Read [the API reference](references/api.md) before changing API calls.

Run `scripts/validate.py` from the skill directory.
```

Keep references one level deep from `SKILL.md`. Avoid chains where one reference file points to another required reference.

## Add bundled resources

### `scripts/`

Add a script when execution must be deterministic, the same code would otherwise be rewritten, or a fragile operation benefits from a tested implementation.

- Make scripts self-contained or document their dependencies in `SKILL.md`.
- Emit useful errors and handle expected edge cases.
- Avoid embedding secrets or machine-specific absolute paths.
- Name test files `test_*.py`. `run-tests.py` at the repository root discovers and runs them recursively. Do not link a test file from `SKILL.md`'s runtime instructions merely to satisfy the orphan-resource check. See [Validate through the wrapper](#validate-through-the-wrapper) for the exemption.
- Do not execute scripts created inside a target skill. Inspect them and report runtime testing as skipped. This skill's only executable entry point is its own `scripts/validate.sh` wrapper.

### `references/`

Store detailed documentation, schemas, policies, examples, or variant-specific guidance that is needed only for some tasks.

- Keep each file focused.
- Link every necessary reference directly from `SKILL.md` with a condition for reading it.
- Do not duplicate the same guidance in `SKILL.md` and a reference file.

### `assets/`

Store files used in generated output, such as templates, images, boilerplate, lookup tables, or schemas. Treat assets as materials to copy or transform, not as instructions to load into context.

## Validate through the wrapper

Run this required local-only validation from the `egai-skill-maker` directory after creating or changing a skill:

```bash
scripts/validate.sh SKILL_DIRECTORY
```

Replace `SKILL_DIRECTORY` with the skill directory, not the `SKILL.md` file. The wrapper rejects HTML tags in `SKILL.md`, runs the approved structure, content, and contamination checks, and permits the required root-level `changelog.md` and `README.md`. Permitting those files does not justify adding other unrelated root files.

Never invoke the underlying validator executable directly. Do not bypass the wrapper, reproduce its internal command, or add arguments that the wrapper does not expose.

The default wrapper mode runs:

- `structure`: specification, frontmatter, directory, token, code-fence, internal-link, and orphan-resource checks.
- `content`: deterministic content metrics and quality heuristics.
- `contamination`: language-mismatch and scope-breadth heuristics.

The wrapper downgrades an orphan-resource warning naming a `scripts/test_*.py` file, `changelog.md`, `gaps.md`, or `README.md` to an `info` diagnostic. An activated agent never needs a runtime pointer to these dev-time-only files. Do not add one to `SKILL.md` merely to silence the warning. Reference a bundled file from `SKILL.md` only when an activated agent genuinely needs to read or run it.

Handle the validator result by exit code and diagnostic severity:

- Exit `0`, passed: accept the validator result and continue with script tests and final review.
- Exit `1`, errors: fix every error and rerun the same command. Do not deliver the skill while errors remain.
- Exit `2`, warnings only: inspect every warning. Treat an over-500-line warning as blocking and fix it. Fix other warnings when they identify a real portability or quality problem. Otherwise, report the warning and the reason it is acceptable.
- Exit `3`, command or usage failure: correct the path, invocation, installation, or environment problem and rerun. Do not interpret this as a skill-validation result.

The output may contain `pass`, `info`, `warning`, and `error` diagnostics. `pass` and `info` require no correction. Apply the warning and error rules above. Confirm the language-quality requirements before declaring validation complete.

Also verify that `metadata.version` is valid SemVer, the newest `changelog.md` entry has the same version, and the entry summarizes the current change. These workflow requirements may not be enforced by `skill-validator`.

Do not add `--strict` unless the user or project explicitly requires every warning to fail validation. Strict mode changes warning handling globally and is not needed to enforce the 500-line policy described here.

If the skill contains external HTTP or HTTPS links and network access is appropriate, use the wrapper's link mode:

```bash
scripts/validate.sh --links SKILL_DIRECTORY
```

Treat external-link results as environment-dependent. Do not make them part of deterministic local validation.

Validate `changelog.md` separately. The wrapper's checks do not cover bullet count or length:

```bash
python3 scripts/validate_changelog.py CHANGELOG_PATH
```

Run it from the `egai-skill-maker` directory with `CHANGELOG_PATH` set to the target skill's `changelog.md`. Fix every reported issue: a bullet over 50 words, a version with no bullets, or a duplicate version.

In addition to validator output, review bundled scripts for clear failures and expected edge cases without executing them. For an updated skill, preserve valid behavior and user-authored resources outside the requested change. Report the exact wrapper command run, its result, and any skipped or environment-dependent checks.

After the wrapper passes, run the full repository test suite from the repository root:

```bash
python3 run-tests.py
```

All test suites must pass before delivering the skill.
