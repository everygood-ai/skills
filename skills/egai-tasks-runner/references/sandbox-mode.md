# Sandbox Mode

Full procedure for Sandbox Mode. Read this only after `SKILL.md`'s "Sandbox Mode" section confirms a caller triggered it.

## What Triggering Replaces

Sandbox Mode replaces normal dispatch entirely. Once triggered:

1. Build the run's configuration.
2. Run the preflight checks on `srt` and the configuration file.
3. Print the command, or a warning, and stop.

Do not classify the path further, read task files, spawn any sub-agent, or perform Group, Phase, or Task dispatch for this invocation. The fresh sandboxed session the printed command starts performs the actual run, in its own process.

## Build the Configuration

Run this command, replacing `SKILL_DIRECTORY` with the directory that contains this skill's `SKILL.md`:

```text
python3 SKILL_DIRECTORY/scripts/build-sandbox-config.py
```

Run it from the current project root. It defaults to the current working directory when given no argument. It writes `.srt-settings.generated.json` to that directory and prints that path on success.

## Preflight Checks

Before printing any command, confirm both:

- `srt` resolves on `PATH` (`command -v srt`).
- `.srt-settings.generated.json` exists — the build step above should have created it.

If either check fails, report the failure instead of printing a command. Never print a command that would fail to run.

## The Reminder

Alongside the printed command, always state that the generated configuration is a best-effort default. The build script does not inspect the project at all — it writes a straight copy of the shipped baseline. `network.allowedDomains` in that copy therefore holds only the agent's own backend domain(s) plus GitHub. It has no package-registry domains, no third-party API domains, and nothing else specific to this project's actual needs. Adding whatever the project's tasks actually require to `.srt-settings.generated.json` before running is the user's responsibility, not this skill's.

## Recovering from a Blocked Domain

`srt` has no interactive fallback mid-run, so a domain the generated config is missing fails the sandboxed run partway through, with a clear "connection blocked" (or equivalent network-denied) error naming the domain — not a silent hang. This is expected, not a bug. State these recovery steps alongside the printed command so the caller has them before the run, not only after it fails:

1. Open `.srt-settings.generated.json` and add the blocked domain to `network.allowedDomains`.
2. Re-run the exact `srt --settings .srt-settings.generated.json ...` command directly — do not re-trigger Sandbox Mode for this. Re-triggering it re-runs the build step, which overwrites `.srt-settings.generated.json` with a fresh copy of the baseline and discards this edit.

One case worth naming: pushing over an SSH remote. `srt`'s `network.allowedDomains` entries match any port unless suffixed with `:port` (for example, `github.com:22` to restrict to that port). The shipped baseline's plain `github.com` and `api.github.com` entries already cover SSH's port 22 to those hosts — no addition needed.

`ssh-agent`'s socket is separate. On macOS, `srt` gates Unix-socket access through a `network.allowUnixSockets` array of literal paths. `$SSH_AUTH_SOCK` is a fresh, randomized path each session, so it cannot be baked into the shipped baseline or the generated configuration ahead of time. A user relying on SSH remotes must add their own session's `$SSH_AUTH_SOCK` to `allowUnixSockets` in `.srt-settings.generated.json` before running.

## Composing the Command

The printed command must contain, in order:

1. **The CLI for the product currently running this skill** — `claude` for Claude Code, `codex` for Codex CLI, `opencode` for OpenCode. No detection step needed: the model composing this command already knows which product it is running as.
2. **`srt --settings <path>`**, where `<path>` is the `.srt-settings.generated.json` file from the build step. Never point `srt` at the shipped baseline template directly.
3. **The re-issued prompt** — the original request, reconstructed for the fresh session: the resolved node path, the forwarded additional instructions, and, if the caller also requested Stacked Phase Mode, the same range language (for example, "ending at phase 20"). Drop the sandboxing trigger phrase itself (for example, "sandboxed") from the re-issued prompt — the fresh session should just do the work, not evaluate Sandbox Mode again.

Offer both forms:

- **Interactive** — a normal session the user watches and can steer.
- **Headless** — a non-interactive run that exits when done. Claude Code: add `-p "<prompt>" --output-format stream-json`. Codex CLI: `codex exec "<prompt>" --json`. OpenCode: `opencode run "<prompt>" --format json`.

## Worked Example

Request, received by a Claude Code session on a plan rooted at `.orch/tasks/checkout/phase-10`: "build me phases 10 to 20 in stacked phase mode, sandboxed."

Interactive:

```bash
srt --settings .srt-settings.generated.json claude "run egai-tasks-runner on .orch/tasks/checkout/phase-10 in stacked phase mode, ending at phase 20"
```

Headless:

```bash
srt --settings .srt-settings.generated.json claude -p "run egai-tasks-runner on .orch/tasks/checkout/phase-10 in stacked phase mode, ending at phase 20" --output-format stream-json
```

Both forms drop "sandboxed" from the re-issued prompt. The fresh session just runs the work.
