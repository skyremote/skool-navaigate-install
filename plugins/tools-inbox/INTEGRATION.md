# tools-inbox: integration notes for the chief of staff

## Where the pack came from

| Source | Owner and licence | What this pack took |
|---|---|---|
| `inbox-scout` (our agent) | Ours | The method: read-only, Action needed then Waiting on then FYI, quote sender and date, never guess an email's content, never send. Rewritten as a skill and a `check` command. |
| `composio-scheduled-email` (our local skill) | Ours | The Composio v3 send call, the connected-account lookup and the hosting advice, rewritten in Python with tests. Narrowed: reminders go only to the member's own address. |
| Composio | Third party, composio.dev | Not bundled. The member makes their own account, connects their own Gmail and adds their own MCP URL. |
| `jev` skill (dbreunig/building-with-jev-skill) | Third party, public, no licence file | Linked with the clone command. Not copied. |

## Left out, and why

| Left out | Why |
|---|---|
| Our three Composio Gmail connections and their MCP entries | Our inboxes. |
| NavAIgate Mail (the Apple Mail companion app and its server) | Our private app and server. |
| The Google service-account email tool and domain-wide delegation | Our Workspace and credentials. |
| Venture grouping (four company names) | Private; the member's piles are generic. |

## Shared-file changes needed (I did not edit these)

1. **`.claude-plugin/marketplace.json`**: add `plugins/tools-inbox/MARKETPLACE_ENTRY.json`.
2. **`scripts/build_catalogue.py`**, `CAPABILITIES`: `'tools-inbox':['email','inbox','gmail','triage','reply','drafts']`.
3. **`README.md` and `ROADMAP.md`**: list `tools-inbox` under module 12, tools.
4. **Tests in CI**: `python3 -m unittest discover -s tests/tools-inbox`.

## Known limits

- The Composio MCP URL cannot go in `userConfig` safely as an MCP entry (an empty URL would fail for every member who
  has not set it), so members add it with `claude mcp add` themselves.
- The guard matches tool names. A mail tool named without SEND, REPLY or FORWARD would not be caught; the skill's
  rule still applies. Codex gets the rule as written guidance only.
