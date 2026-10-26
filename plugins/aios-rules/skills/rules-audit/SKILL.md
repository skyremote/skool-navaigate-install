---
name: rules-audit
description: Run my monthly AIOS rules audit (the budget check, /doctor prompt-audit and /skill-doctor) and save the findings to a dated file. Use for /rules-audit, the monthly audit, a new model release, or "what should I cut from my rules".
---

# The monthly rules audit

Run it on the first working day of each month and on the day a new Claude model ships.
The audit reports. It never edits the member's rules. Changes happen only when they tick them.

## Find the command
- Claude Code: `aios-rules` is on PATH from this plugin's `bin/`.
- Codex or Cursor: `~/.local/bin/aios-rules`, or resolve this SKILL.md's symlink and run
  `python3 <pack>/bin/aios-rules`, two folders above `skills/rules-audit`.

## 1. Run it
From the member's AIOS folder:

```sh
aios-rules audit
```

It writes `80_aios/audits/YYYY-MM-DD_rules-audit_v1.md` (`_v2` if one exists today) with:
1. the budget check for Claude Code, Codex and Cursor;
2. `/doctor prompt-audit`: old-model instructions, dead references, contradictions;
3. `/skill-doctor`: what each skill costs and which are never used;
4. a decisions checklist.

Steps 2 and 3 run `claude -p` on the member's own Claude Code sign-in, with read-only tools
(Read, Glob, Grep; Edit, Write and Bash denied). They use the member's subscription, never an API key.
Each can take several minutes. Use `--out <folder>` for another location and `--no-claude` for
the budget check only.

## 2. Read the file honestly
- The last line gives each step's status: `ok`, `unavailable`, `failed`, `skipped` or `not-run`.
- `unavailable`: the command is not offered in that session (for example, `/skill-doctor`
  needs a terminal session that fetches feature flags). Ask the member to run it in Claude Code
  in their terminal and paste the report under its heading. Never fill a section yourself.
- `failed`: show the error and fix the cause (not signed in, `claude` not on PATH, timeout).

## 3. Decide, then change
Walk the checklist with the member, one finding at a time:
- Cut lines from AGENTS.md that an agent no longer gets wrong. Move procedures to skills and
  one-folder rules to `.claude/rules/` with `paths:`.
- Hide skills `/skill-doctor` shows as unused: `/skills`, then press Space to cycle to
  name-only or off. Plugin skills are turned off in `/plugin`.
- Apply prompt-audit edits only for the findings they tick. Show the diff first.
Then run `aios-rules check` again and record the new totals in the audit file.

## 4. Make it monthly
Offer a calendar reminder first. If they want it automatic on an always-on Mac, show this
crontab line and add it only with their yes (cron needs the full path to `claude`):

```text
0 9 1 * * cd "$HOME/my-aios" && PATH="$HOME/.local/bin:/opt/homebrew/bin:$PATH" aios-rules audit
```

Audit files can hold private details. Keep them out of public repositories.
End with the file path, each step's status, and one next action. British English.
