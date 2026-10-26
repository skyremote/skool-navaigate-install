---
name: tools-tasks
description: Turn the member's briefs, call notes and decision records into tasks in their own ClickUp (through ClickUp's official MCP server), each with a verb, an owner, a due date and a "done when", and pick at most three for today from what is overdue. Use for "put these on my list", "turn this brief into tasks", "what's overdue", "what should I do today", "add this to ClickUp".
---

# Tasks that get done

The member uses their own ClickUp account. The plugin connects ClickUp's official MCP server
(`https://mcp.clickup.com/mcp`); the first use opens ClickUp's sign-in (`/mcp` in Claude Code). Never ask for a
token. This skill is how we turn words into work: every task is checked before it goes in, and "today" is a short list.

## The command

Claude Code: `"${CLAUDE_PLUGIN_ROOT}/bin/tools-tasks"`. Codex and Cursor: `tools-tasks` (in `~/.local/bin`).

| Command | What it does |
|---|---|
| `new <file> --title ... [--source ...]` | An empty task list for one brief or call. |
| `check <file>` | Every task starts with a verb, has an owner, a due date (or "no date") and a "Done when". |
| `today <open-tasks.json> [--on YYYY-MM-DD]` | Overdue grouped by list, and at most three for today. |
| `sample <folder>` | A practice task list and a practice export of open tasks (fictional). |

`today` reads a JSON list: `[{"name", "due": "YYYY-MM-DD" or null, "priority": 1-4, "list", "status"}]`. Fill it from
ClickUp's task tools (name, due date, priority, list name, status), then run it.

## Setup (once)

- Claude Code: the plugin adds ClickUp's server; run `/mcp`, choose clickup, and sign in.
- Codex: in `~/.codex/config.toml`, `[mcp_servers.clickup]` with `url = "https://mcp.clickup.com/mcp"`, or the
  `npx -y mcp-remote https://mcp.clickup.com/mcp` bridge ClickUp documents for clients without HTTP.
- Cursor: Settings, MCP, add `https://mcp.clickup.com/mcp` (or ClickUp in Cursor's marketplace).
- Check: ask for their ClickUp spaces. If nothing comes back, they sign in again.

## From a brief to tasks

1. Read the whole brief, call record (for example from `tools-meetings`) or message.
2. One task per outcome. Start with a verb (Send, Book, Write, Decide, Ask). "Look into" and "work on" are not tasks.
3. Owner: a name from the source, or ask. Due: a date from the source as YYYY-MM-DD, or "no date". Never invent either.
4. "Done when": what anyone could see when it is finished.
5. `new` the list, fill it in, `check` it, show the member.
6. Only after they say yes: find the right ClickUp list (ask if unsure) and create the tasks with ClickUp's tools.
   Read them back and give the links.

## Today

1. Pull open tasks assigned to the member from ClickUp, write the JSON, run `today`.
2. Show overdue by list (client or project), then at most three for today. More than three is a wish list.
3. Ask before changing any due date, status or assignee in ClickUp.

## Optional: Task Master for build projects

For a software build from a product brief, the public `task-master-ai` (npm, licence "MIT WITH Commons-Clause"; check it
) breaks a brief into ordered tasks and picks the next one: `npm i -g task-master-ai`, then add its MCP
server. Use it for the build; keep business work in ClickUp.

## Rules

- Create, change or close ClickUp tasks only when the member asked for that change.
- Never assign work to someone else without the member saying so.
