---
name: harness-setup
description: Use whenever someone runs two or more of Claude Code, Codex, Cursor or Grok Bot and wants them to share the same rules, skills or MCP servers, or asks which one to use for what. Sets up one AGENTS.md, one shared skills folder and one MCP list, plus model and effort defaults.
---

# Harness setup

Ask first: which harnesses does the member have, and where is their AIOS folder? Keep their existing files.
Find the tool as in `harness-check`: `"${CLAUDE_PLUGIN_ROOT}/bin/harness"` in Claude Code, `harness` elsewhere.

## Install the harnesses they are missing
Give only the lines they need, and let them run them:

| Harness | Install | Check |
|---|---|---|
| Claude Code | `curl -fsSL https://claude.ai/install.sh \| bash` | `claude --version` |
| Codex | `npm install -g @openai/codex` (or `brew install codex`) | `codex --version` |
| Cursor | Download from cursor.com, then `curl https://cursor.com/install -fsS \| bash` for the CLI | `cursor-agent --version` |
| Grok Bot | Download the app from its official site and sign in | Open it and start a chat |

## Set up the folder (one command)
From the AIOS folder run `harness setup --dry-run`, show the member the plan, then run `harness setup`. It:
1. Creates `AGENTS.md` from a short template if there is none, with a rules check phrase at the end.
   It never overwrites an existing AGENTS.md; it only adds the phrase line.
2. Creates `CLAUDE.md` as the one line `@AGENTS.md`. An existing CLAUDE.md is left alone and reported.
3. Creates `.aios/mcp.json`, the one list of MCP servers.
4. Creates `~/.agents/skills` and links each shared skill into `~/.claude/skills` (Codex and Cursor read
   `~/.agents/skills` themselves).
5. Writes the MCP list into `.mcp.json`, `.codex/config.toml` and `.cursor/mcp.json` in the folder.
   Files it did not write last are backed up first.

Then help them fill the brackets in AGENTS.md. Keep it short: under 200 lines, and much less on day one.

## Add an MCP server to every harness
`harness mcp add <name> -- <command> [args]` for a local server, or `harness mcp add <name> --url <https-url>`.
Secrets go in the shell, never in a file: `--env 'ACME_TOKEN=${ACME_TOKEN}'`, in single quotes so the shell does not paste the value in. The tool refuses a literal key.
Grok Bot is added by hand: `harness grok` prints the name, command and arguments to type into its settings.
First time only: Claude Code asks to approve a project server (say yes), and Codex asks to trust the folder.

## Which harness for which job
Read `reference.md` in this folder for the table and the model and effort defaults. Short version:
Claude Code or Codex to build in a repo, the other one for a second opinion, Cursor to try another model,
Grok Bot for jobs that keep running while you are away, and bb to run several at once.

## Defaults
`harness defaults` shows the model and effort each harness uses. Start at medium effort. `harness defaults --apply`
writes medium into this folder's `.claude/settings.json` and `.codex/config.toml`. Raise effort for one hard job only.

Finish with `harness check` (the `harness-check` skill) and one next action. British English.
