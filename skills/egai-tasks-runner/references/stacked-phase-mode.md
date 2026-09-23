# Stacked Phase Mode

Full procedure for Stacked Phase Mode. Read this only after confirming a caller requested the mode explicitly, per the "Stacked Phase Mode" section of `SKILL.md`.

## Range Input

The same free-text instructions carry the range: a count of phases, or an end phase's path. There is no separate input field for the range.

The classified PATH must be a `phase`, the start of the range. Stop and ask if it classifies as anything else while this mode is requested.

## Resolve the Range

Run one of these from the current workspace:

```text
python3 SKILL_DIRECTORY/scripts/phase-range.py START_PHASE_DIR --count N
python3 SKILL_DIRECTORY/scripts/phase-range.py START_PHASE_DIR --end END_PHASE_DIR
```

Replace `SKILL_DIRECTORY` with the directory containing `egai-tasks-runner`'s `SKILL.md`.

This prints the ordered list of sibling phase directories to run. It classifies every phase it lists. A gap left by a deleted phase is skipped, not treated as an error.

With `--count`, a range shorter than N is not an error. The script caps it at whatever exists under the parent and reports the cap on stderr. With `--end`, a missing end phase is an error.

Stop and ask when the script exits with an error instead of a list. Do not guess.

## Per-Phase Loop

For each phase in the resolved range, in order:

1. **Branch.** Set the phase's checkbox to `[~]` in its parent group's `index.md`. This follows the same ownership rule as Group dispatch in `SKILL.md`. The foreground coordinator spawns one terminal `egai-task-reader` worker and asks it, in plain language, for the phase's branch name and PR title. It waits for that report, then creates a worktree at `/tmp/egai-worktrees/<branch>` (where `<branch>` is the reported branch name) on that branch with `git worktree add`, chained off the base branch. The base branch is the previous phase's branch, or the branch this run started on for the first phase.
2. **Dispatch.** The same foreground coordinator runs the phase in the new worktree using the Phase procedure in `SKILL.md`: the same sequential units and parallel batches, with one terminal `egai-task-impl` worker per task. Give every worker the worktree path explicitly and require it to operate there. Do not spawn a phase-level `egai-tasks-runner`.
3. **Commit.** After each unit's checkbox in the phase's own `index.md` flips to `[x]`, the foreground coordinator commits the worktree's changes. Never let `egai-task-impl` commit. Name the task ID and title in the commit message.
4. **Push and open a PR.** Once every task in the phase is done, the foreground coordinator pushes the branch. If `gh` is installed and authenticated, it spawns one terminal `egai-task-reader` worker and asks it, in plain language, for the phase's finished PR title and body, given the base branch. Open a PR with base set to the phase's base branch. Otherwise, push to a configured remote, or leave the branch local. Report either outcome as the phase's normal result, never as a failure.
5. **Clean up.** Once the branch is pushed or opened as a PR, the foreground coordinator removes the worktree directory with `git worktree remove`. Keep the branch.
6. **Report and advance.** Set the phase's checkbox in its parent group's `index.md` to `[x]` when it completed, or back to `[ ]` when it is blocked. Report the phase's branch name and its PR link or push/local state. Advance immediately to the next phase. Never wait for a phase's PR to be reviewed or merged.

## Reporting and Blockers

Report each phase's outcome as the foreground coordinator completes it, not only at the end of the range.

If a phase is blocked, halt that phase and every phase after it in the range. Do not chain a next phase off a branch whose phase never finished. Record the blocker the same way Phase dispatch in `SKILL.md` does.
