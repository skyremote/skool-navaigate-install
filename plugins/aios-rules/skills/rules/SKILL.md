---
name: rules
description: Set up my AIOS folder map, a short AGENTS.md, the one-line CLAUDE.md bridge and path-scoped rules, then check how much is always loaded. Use for /rules, my folders, my rules file, AGENTS.md, CLAUDE.md, or "is my context too big".
---

# Your folders and your rules

The goal: one folder, one short rules file every harness reads, and a check that proves
the always-on part stays small. Keep the member's existing work. Never wipe or rewrite it.

## Find the command
- Claude Code: `aios-rules` is on PATH from this plugin's `bin/`.
- Codex or Cursor: run `~/.local/bin/aios-rules` if it exists. Otherwise resolve this
  SKILL.md's symlink and run `python3 <pack>/bin/aios-rules`, two folders above `skills/rules`.
- If it cannot run, say so. Never report a check you did not run.

## 1. Ask where they are
Ask: **empty, halfway, or already running?** Then look at the folder: `AGENTS.md`,
`CLAUDE.md`, `CLAUDE.local.md`, `.claude/rules/`, `.cursor/rules/` and the top-level folders.

## 2. Set up (only what is missing)
Show the dry run first, then run it when they say yes:

```sh
aios-rules init --dir . --business "Their Business" --owner "Their Name" --dry-run
aios-rules init --dir . --business "Their Business" --owner "Their Name"
```

- `init` creates the folder map (`00_inbox` to `90_archive`), a starter `AGENTS.md`, a
  `CLAUDE.md` that holds only `@AGENTS.md`, and three rules in `.claude/rules/` with `paths:`.
- It never overwrites a file. Existing files are reported as KEPT.
- Halfway or already running: add `--no-folders` if they have their own folders. Map their
  folders into the AGENTS.md table instead of creating new ones.
- If their `CLAUDE.md` lacks `@AGENTS.md`, `init` changes nothing. Show them the one line
  to add at the top, and add it only when they say yes.

## 3. Fill in AGENTS.md together
Interview, one question at a time: what the business does, who buys, one line per folder,
the rules that must never break, and one check the folder can run. Replace each `{{...}}`.
Keep it under 150 lines. Gotchas only: a line earns its place when an agent got it wrong twice.
Move any step-by-step procedure to a skill. Move a rule for one folder to `.claude/rules/<topic>.md`:

```markdown
---
paths:
  - "30_finance/**"
---
# Finance folder
- One rule per line.
```

A rule without `paths:` loads in every session, so it counts against the budget.

## 4. Run the check
```sh
aios-rules check            # Claude Code view
aios-rules check --harness all
```

It counts the lines and approximate tokens (characters / 4) of everything always loaded:
`~/.claude/CLAUDE.md`, CLAUDE.md files from the folder up, imports (`@file`, four hops),
AGENTS.md, rules without `paths:`, the auto-memory index and skill descriptions.
Exit 0 means within budget. Exit 1 means OVER: name the file and what to move.
Defaults: 150-line target and 200-line limit per file, 300 lines and about 4,000 tokens in total.
WARN lines (placeholders, a missing import, a long skill description) do not fail the check.

## 5. Other harnesses
- Codex reads `AGENTS.md` from the repository root down to the working folder. It does not read
  `CLAUDE.md` or `.claude/rules/`, so keep must-hold rules in the root `AGENTS.md`.
- Cursor reads `AGENTS.md`. Run `aios-rules cursor-rules` to mirror `.claude/rules/` into
  `.cursor/rules/*.mdc` with the same globs. It never overwrites a Cursor rule it did not write.

## Finish
Report the check's real numbers and status, the one next action, then point to the monthly
audit (`/rules-audit`) and `/aios`. Keep it short. British English.
