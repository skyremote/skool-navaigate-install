# tools-tasks (AIOS 2.0, module 12: the shelf, tools)

Briefs into tasks that get done, in your own **ClickUp**. The plugin connects ClickUp's official MCP server
(`https://mcp.clickup.com/mcp`, you sign in through ClickUp). This pack gives your agent our way of working: every task
starts with a verb and has an owner, a due date and a "done when", it is checked before it goes in, and "today" is
never more than three things.

## Install

1. Install the start plugin `aios` first (module 1).
2. A ClickUp account.

**Claude Code:** `/aios install tools-tasks` (or `/plugin install tools-tasks@navaigate-aios`), then `/reload-plugins`,
then `/mcp`, choose clickup and sign in.

**Codex and Cursor**, from your checkout of this repository:
```
./install.sh tools-tasks
./install.sh tools-tasks --check
```
Then add ClickUp's server yourself. Codex, in `~/.codex/config.toml`:
```
[mcp_servers.clickup]
url = "https://mcp.clickup.com/mcp"
```
Cursor: Settings, MCP, add the same URL (or install ClickUp from Cursor's marketplace). Sign in when asked.

Needs Python 3.9 or later.

## Use

```
tools-tasks sample ~/Tasks-practice
tools-tasks check ~/Tasks-practice/northwind_tasks_v1.md
tools-tasks today ~/Tasks-practice/open-tasks_v1.json --on 2026-10-26
```

Three starter prompts: [prompts.md](prompts.md). The method: [skills/tools-tasks/SKILL.md](skills/tools-tasks/SKILL.md).

## Licence

MIT. ClickUp and its MCP server belong to ClickUp, with their own terms.
