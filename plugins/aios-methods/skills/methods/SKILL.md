---
name: methods
description: Pick and run a working method for a piece of work, such as /loop with a check, a git worktree for parallel work, interview before you build, GSD or compound engineering. Use for /methods, "run this in parallel", "keep checking", "loop this", or "which method should I use".
---

# Working methods

Pick one method for the job in front of the member. Do not stack them all.

| The job | Method | First command |
|---|---|---|
| The idea is vague, or the words are fuzzy | Interview before you build | `/grill` (this pack) |
| A second feature while the first is still running | Git worktree | `aios-methods worktree new <name>` |
| Re-run a check or a small step on a timer, while the session is open | `/loop` | `/loop 10m <prompt>` |
| A multi-phase project with a roadmap | GSD Core (third party) | `npx @opengsd/gsd-core@latest` |
| You want every fix to teach the next one | Compound engineering (third party) | `/ce-plan`, then `/ce-compound` |

The order for one feature: interview, spec, worktree, loop, merge, clean up.

## Interview before you build

Run the `grill` skill. It asks one question at a time, writes the answers into
`docs/specs/<slug>.md` and the shared words into `GLOSSARY.md`. Do not write code
until `aios-methods spec check docs/specs/<slug>.md` exits 0.

## Git worktrees

A worktree is a second folder on its own branch that shares one git history.
Each harness session works in its own folder, so two agents never edit the same files.

- Create: `aios-methods worktree new <name>`. It makes `../<repo>-<name>` on branch `work/<name>`.
- Or let the harness do it: `claude -w <name>`, `codex --worktree`, `cursor-agent -w <name>`.
- In bb, every thread already runs in its own worktree. Use one thread per feature.
- See them all: `aios-methods worktree list` (shows clean or changes for each).
- Finish: merge the branch, then `aios-methods worktree done <name>`.
  It refuses if the folder has changes or the branch is not merged. Never force it.

In Claude Code use `aios-methods` from this plugin's `bin/`. In Codex and Cursor use
`~/.local/bin/aios-methods` after `./install.sh aios-methods`.

## /loop

`/loop` is built into Claude Code. It re-runs a prompt while the session stays open.

- `/loop 5m check whether the deploy finished and tell me what happened` runs on a fixed interval.
- `/loop check CI and fix what fails` lets Claude pick the interval.
- Bare `/loop` runs `.claude/loop.md` if it exists. Create one with `aios-methods loop init`.
  The template does one unit per run, runs that unit's check, commits, and stops when all checks pass.
- Stop a loop by asking: "cancel the deploy check loop". Esc does not stop it.
- Limits: it fires only while Claude Code is open and idle, there is no catch-up for missed runs,
  and a recurring loop expires after seven days.
- For work that must run with the laptop shut, use a cloud routine or a Desktop scheduled task instead.

Every loop needs a check it can run each time, and a stop condition. A loop with no check
only repeats the same mistake on a timer. Never let a loop push, deploy or delete.

Codex and Cursor have no `/loop`. There, run the check in a shell loop the member can see,
for example `while sleep 600; do npm test || break; done`, or use the harness's own scheduler.

## Third-party methods

Link to them and give the install line. Do not copy their files into the member's repo.
Read `references/third-party.md` for the links, install commands, licences and the core commands.

## Check that it worked

- Worktree: `aios-methods worktree list` shows the new folder as `clean` before work starts.
- Interview: `aios-methods glossary check` and `aios-methods spec check <file>` both exit 0.
- Loop: the transcript shows each run's command and its real output.

End with the method chosen, the one next command, and `/aios` for the next module. British English.
