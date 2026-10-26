---
name: harness-check
description: Use whenever Claude Code, Codex, Cursor or Grok Bot behave differently, miss a skill or MCP server, or follow an old rules file. Runs /harness-check, which proves all four see the same rules, skills and MCP servers and prints what differs and how to fix it.
---

# Harness check

Find the tool first. In Claude Code run `"${CLAUDE_PLUGIN_ROOT}/bin/harness"`.
In Codex, Cursor or a terminal run `harness` (installed at `~/.local/bin/harness`).
If neither works, resolve this SKILL.md symlink and run `bin/harness`, two folders above `skills/harness-check`.
If the tool cannot run, say the check is unverified. Never guess a result.

Run it from the member's AIOS folder (or pass `--folder <path>`):

```
harness check
```

It prints one row each for rules, skills and MCP servers, and one column per harness:
- **OK**: this harness sees the same thing as the others.
- **WARN**: worth knowing, but not a mismatch (for example a personal rules file, or a server waiting for approval).
- **DIFF**: a real mismatch. The exit code is 1 while any DIFF remains.
- **ASK**: Grok Bot. It runs on its own computer, so it is checked from a pasted answer.

Then report:
1. The table, as printed.
2. Each line under "What differs", with its fix.
3. One next action.

Fix each difference with the member, one at a time, then run the check again until it says "all harnesses match":
- Rules: AGENTS.md is the one rules file. CLAUDE.md is the one line `@AGENTS.md`. Fold any extra file
  (`AGENTS.override.md`, `.cursorrules`, an always-applied `.cursor/rules/*.mdc`, `CLAUDE.local.md`) into AGENTS.md,
  then delete it. Ask before deleting, and show the member the lines that move.
- Skills: shared skills live in `~/.agents/skills`. Codex and Cursor read that folder directly. `harness sync` links
  each one into `~/.claude/skills` for Claude Code. A skill that lives only in one harness's folder is moved into
  `~/.agents/skills` by the member.
- MCP servers: `.aios/mcp.json` is the one list. `harness sync` writes it to `.mcp.json` (Claude Code),
  `.codex/config.toml` (Codex) and `.cursor/mcp.json` (Cursor). Add or remove a server for all three with
  `harness mcp add <name> -- <command> [args]` or `harness mcp remove <name>`.
- Grok Bot: run `harness grok`. It prints what to paste into Grok Bot's settings and a probe prompt. The member saves
  Grok Bot's answer as `.aios/grok-bot.txt`, and the next check compares it.

`harness check --live` also asks each installed CLI for the rules check phrase and its MCP list. It costs one short
prompt per harness, so offer it, do not run it by default. `--json` gives the same result for scripts.

After any change, tell the member to restart the harness so it reloads. Never print MCP env values or tokens.
Keep the reply short. British English. End with `/aios` for the next module.
