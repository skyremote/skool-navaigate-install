# tools-tasks: integration notes for the chief of staff

## The ClickUp decision

The brief said: use ClickUp's own public MCP server if one exists, never our private one. It exists:
`https://mcp.clickup.com/mcp`, documented at developer.clickup.com ("Connect an AI assistant to ClickUp's MCP server"),
with sign-in through the client's MCP flow. `.mcp.json` connects it; no token is stored.

## Where the pack came from

| Source | Owner and licence | What this pack took |
|---|---|---|
| ClickUp official MCP server | ClickUp | Connected in `.mcp.json` (HTTP, sign-in on first use). |
| Our task habits (the `workspace_todo` habit, our ClickUp use) | Ours | The method: verb first, owner, due date, "done when", nothing invented, three for today, ask before changing anything. |
| `task-master-ai` (npm) | Third party | Mentioned as optional for software builds, with its install line; its licence is the member's to check. Not bundled. |

## Left out, and why

| Left out | Why |
|---|---|
| `skyremote/clickup-mcp` (our private server), its token and team id | Private. |
| Our spaces, lists, task names and the contractor space | Private. |
| bb Kanban | Covered by the bb module (module 4). |

## Shared-file changes needed (I did not edit these)

1. **`.claude-plugin/marketplace.json`**: add `plugins/tools-tasks/MARKETPLACE_ENTRY.json`.
2. **`scripts/build_catalogue.py`**, `CAPABILITIES`: `'tools-tasks':['tasks','clickup','to do','overdue','project plan']`.
3. **`README.md` and `ROADMAP.md`**: list `tools-tasks` under module 12, tools.
4. **Tests in CI**: `python3 -m unittest discover -s tests/tools-tasks`.

## Known limits

- ClickUp's server was not signed in during the sandbox (no member account); its tool names are ClickUp's and can change.
