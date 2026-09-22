# Inject self-contained tone guidance

Use this workflow only when the target skill must carry its own tone rules. If `egai-write-tone` is available whenever the target skill runs, invoke it at runtime instead.

The bundled injector reads the pinned contracts already compiled into this public skill. It does not need this repository, capability sources, or any external compiler.

From the installed `egai-skill-maker` directory, run:

```bash
python3 scripts/inject-tone-contracts.py SKILL_DIRECTORY --profile PROFILE --heading "## PURPOSE tone"
```

- Replace `SKILL_DIRECTORY` with the target skill directory.
- Select `prose` for long-form reader-facing output, `terse` for procedures and technical output, `compact` for dense context or requirement files, or `terse-report` for concise delivery reports.
- Replace `PURPOSE` with the target output's role. The heading must begin with `##`.

The command creates `SKILL_DIRECTORY/references/tone.md`. It refuses to replace an existing file unless `--replace` is explicit. Then add a direct link from the target `SKILL.md` that says when to read and apply the new reference. Do not add versioned capability comment markers or a requirement to run this injector after the target skill has been delivered.

Example:

```bash
python3 scripts/inject-tone-contracts.py ../release-notes --profile terse-report --heading "## Delivery report tone"
```

Then the target `SKILL.md` can say:

```markdown
Read [references/tone.md](references/tone.md) before drafting the delivery report. Apply its Kernel and Delivery report tone.
```
