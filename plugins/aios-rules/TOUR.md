# Tour: module 2, your folders and your rules

`/aios learn 2` follows these steps in the member's own AIOS folder, one at a time.
Run each command for the member, or have them type it. Show the real output, then check it before the next step.
Never overwrite a member's file. If a check fails, stop, fix that one thing, and run the check again.

## Step 1: Find the command
- **Do:** check that the pack's command runs.
- **Command:** `aios-rules --version` (Codex or Cursor: `~/.local/bin/aios-rules --version`).
- **They should see:** `aios-rules 2.0.0`.
- **Check:** exit code 0. If the command is missing, run `export PATH="$HOME/.local/bin:$PATH"` (Codex and Cursor),
  or restart Claude Code after `/plugin install aios-rules@navaigate-aios`.

## Step 2: Ask where they are
- **Do:** ask "empty, halfway or already running?" Then list the folder.
- **Command:** `ls -A`
- **They should see:** their own files. Note any `AGENTS.md`, `CLAUDE.md`, `CLAUDE.local.md` and `.claude/rules/`.
- **Check:** you can name each top-level folder. If they have their own folders, use `--no-folders` in step 3.

## Step 3: Preview the set-up
- **Do:** show what would be created, without writing anything.
- **Command:** `aios-rules init --business "Their Business" --owner "Their Name" --dry-run`
- **They should see:** one line per folder and file, each `CREATED` or `KEPT`.
- **Check:** `ls -A` shows nothing new yet.

## Step 4: Set it up
- **Do:** run the same command without `--dry-run`, after they say yes.
- **Command:** `aios-rules init --business "Their Business" --owner "Their Name"` (add `--no-folders` if halfway)
- **They should see:** `CREATED` for what was missing and `KEPT` for what was there.
- **Check:** `cat CLAUDE.md` prints `@AGENTS.md`. If their old CLAUDE.md was kept, show them the one line to add at
  the top, and add it only when they say yes.

## Step 5: Fill in AGENTS.md
- **Do:** ask one question at a time: what the business does, who buys, one line per folder, the rules that must
  never break, and one check this folder can run. Replace each `{{...}}` line with the answer.
- **Command:** `grep -n "{{" AGENTS.md`
- **They should see:** no lines once every gap is filled.
- **Check:** `wc -l AGENTS.md` is under 150.

## Step 6: Read a path-scoped rule
- **Do:** open the finance rule and point at the `paths:` block.
- **Command:** `head -5 .claude/rules/finance.md`
- **They should see:** `paths:` and `- "30_finance/**"` between two `---` lines.
- **Check:** they can say when this rule loads (only for files in `30_finance/`).

## Step 7: Add their own rule
- **Do:** copy the finance rule for one of their own folders, then change the path and the lines.
- **Command:** `cp .claude/rules/finance.md .claude/rules/<topic>.md`
- **They should see:** the new file in `ls .claude/rules`.
- **Check:** step 8 lists it under "On demand", not in the always-loaded list.

## Step 8: Run the budget check
- **Do:** count everything Claude Code loads into every session.
- **Command:** `aios-rules check`
- **They should see:** `CLAUDE CODE: OK`, the always-loaded files with lines and approximate tokens, and the rules
  under "On demand".
- **Check:** exit code 0 (`echo $?`). If it says OVER, move steps into skills and one-folder rules into
  `.claude/rules/`, then run it again.

## Step 9: Check the other harnesses
- **Do:** mirror the rules for Cursor, then check all three harnesses.
- **Command:** `aios-rules cursor-rules` then `aios-rules check --harness all`
- **They should see:** `WRITTEN` lines for `.cursor/rules/*.mdc`, then OK for Claude Code, Codex and Cursor.
- **Check:** Cursor's on-demand list shows the same rules. Codex reads only AGENTS.md, so its must-hold rules live there.

## Step 10: Prove the agent reads it
- **Do:** ask Claude Code, without opening any file, where invoices go.
- **Command:** `claude -p "Without reading any file, quote the line in your instructions that says where invoices go."`
- **They should see:** the `30_finance/` line from their AGENTS.md.
- **Check:** in a session, `/context` lists CLAUDE.md and AGENTS.md under Memory files.

## Step 11: Run the first audit
- **Do:** run the monthly audit. It takes a few minutes and uses their own Claude Code sign-in.
- **Command:** `aios-rules audit`
- **They should see:** `Wrote ./80_aios/audits/<date>_rules-audit_v1.md` and a status for each part.
- **Check:** open the file. Each part says ok, unavailable, failed or skipped. If `/skill-doctor` is unavailable,
  they run it in their own terminal session and paste the report under its heading. Nothing in their rules changed.

## Step 12: Make it a habit
- **Do:** agree the first working day of each month, and the day a new model ships, as audit days.
- **Command:** none, or a calendar reminder. Offer the crontab line in `/rules-audit` only if they want it automatic.
- **They should see:** the next audit date written in section 4 of the audit file.
- **Check:** they can say where a new line goes: everywhere (AGENTS.md), one folder (`.claude/rules/`), or a process (a skill).

Finish with the check's real totals, then `/aios` for module 3.
