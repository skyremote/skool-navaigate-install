# Harness reference (October 2026)

## What each harness reads

| | Claude Code | Codex | Cursor | Grok Bot |
|---|---|---|---|---|
| Rules | `CLAUDE.md` (make it `@AGENTS.md`); reads `AGENTS.md` itself when there is no CLAUDE.md (2.1.277+) | `AGENTS.md` (`AGENTS.override.md` wins if present) | `AGENTS.md`, plus `.cursor/rules/` and the old `.cursorrules` | Paste AGENTS.md into its instructions |
| Skills | `~/.claude/skills`, `.claude/skills`, plugins | `~/.agents/skills`, `.agents/skills` | `~/.agents/skills`, `~/.cursor/skills`, and the Claude and Codex folders | Its own plugins and skills |
| MCP (this pack) | `.mcp.json` (project) | `.codex/config.toml` (trusted project) | `.cursor/mcp.json` (project) | Added in the app or by asking it in chat |
| Also reads | `~/.claude.json` (user servers) | `~/.codex/config.toml` | `~/.cursor/mcp.json` | |

Sources: code.claude.com/docs/en/memory and /skills; the Codex docs on skills and MCP; cursor.com/docs/context/skills.

## Which harness for which job

| The job | Reach for | Why |
|---|---|---|
| Build or fix something in a repo | Claude Code or Codex | Both read AGENTS.md and both run your tests |
| A second opinion on that build | The other one of those two | A different model on the same files catches different things |
| Try Grok or another model | Cursor | Same folder, same AGENTS.md, a different model |
| A job that keeps running while you are away | Grok Bot | It is always on and has its own computer |
| Several of these at once | bb (module 4) | One thread each, side by side, in one window |

## Model and effort defaults

| Harness | Where it is set | Start with |
|---|---|---|
| Claude Code | `settings.json`: `model`, `effortLevel` | The default model at `medium` effort |
| Codex | `config.toml`: `model`, `model_reasoning_effort` | The default model at `medium` |
| Cursor | The model picker, or `/model` in `cursor-agent` | Pick per job |
| Grok Bot | The app's settings | The default |

Medium is Anthropic's default for the 5.5 models. Raise effort for one hard job, then put it back.
