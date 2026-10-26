---
name: verify-setup
description: Give a project checks the agent can run itself (tests, build, screenshot), a gate that stops it finishing while they fail, and hooks for three hard rules. Use when someone asks to make their work verifiable, add tests or a verify step, stop the agent saying done too early, or block secrets, force pushes or surprise deploys.
---

# Make it verifiable

The agent should prove a change works, not say it does. This pack gives a project four things.

## 1. Checks it can run
From the project folder:
```
aios-verify init
```
It writes, and never overwrites:
- `.aios/verify.json`: the checks, guessed from `package.json`, Python tests or a Makefile.
  Open it and make each `run` command right for this project.
- `.claude/skills/verify/SKILL.md`: a project skill named `verify`. Claude Code (2.1.286 or
  later) runs a project skill with that name right before each commit.
- `REVIEW.md`: what a review checks, and who approves by risk.
- `.github/pull_request_template.md`: What changed, Testing, Risk, How to revert.
Then run `aios-verify run`. Every check must print PASS before you rely on the gate.
Add `--git-hook` to also install a git pre-commit hook, which works for Codex, Cursor and people.

## 2. The Stop gate
With this plugin enabled, a project that has `.aios/verify.json` gets a gate: when the agent
tries to finish a turn after changing files, the checks run, and if one fails the agent is
sent back with the failure output. It skips unchanged files, ignores projects without the
file, and gives up after 3 failed attempts on the same files, telling the person the work
is not done. Checks marked `"gate": false` (such as the screenshot) run only in `aios-verify run`.

## 3. Three hard rules as hooks
Always on while the plugin is enabled, in every project:
| Rule | What happens |
|---|---|
| No secrets in commits | `git commit` is denied if the staged change adds a key, token, private key or `.env` file |
| No destructive git | force push, `reset --hard`, `clean -f`, `checkout -- .`, `branch -D`, stash drop and history rewrites are denied |
| Confirm before live production | deploys and publishes (Vercel `--prod`, `npm publish`, push to main, Terraform apply and more) ask the person first |
Test any command without running it: `aios-verify try "git push --force"`.
Add the project's own deploy commands as regular expressions in `production_commands` in `.aios/verify.json`.
The hooks act on the agent's Bash tool only. A person can still run anything in their own terminal.

## 4. Review in layers
Checks first, then an AI review (module 7's `code-reviewer`), then a person approving by risk
as `REVIEW.md` says. Use the `pr-ready` skill to write the pull request.

## Codex and Cursor
`aios-verify init --git-hook` gives them the same secret scan and checks at commit time.
The Stop gate and the PreToolUse hooks are Claude Code features.

## Never
- Never weaken a test to make the gate pass. Fix the code, or say plainly that it fails.
- Never call work done while `aios-verify run` fails.
- Never print a secret's value; the scanner reports only the file and the kind.

Finish with the result of `aios-verify run` and one next action. British English.
