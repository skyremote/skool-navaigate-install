# tools-social: integration notes for the chief of staff

## Where the pack came from

| Source | Owner and licence | What this pack took |
|---|---|---|
| `blotato-publish` (private team plugin) | Ours | The release-clock gate (draft, ready, scheduled, live; approval is not a time; the exact question), the comment-for-link rules, and the verification states. The gate is now enforced by a hook against Blotato's `scheduledTime`. |
| `social-captions` (private team plugin) | Ours | The platform rules (three hooks, lengths, X limit, YouTube titles, no invented links) as a `check` command. |
| Blotato official MCP (`https://mcp.blotato.com/mcp`) | Third party | Connected in `.mcp.json` with the member's key from `userConfig` (header `blotato-api-key`). |

## Left out, and why

| Left out | Why |
|---|---|
| Our Blotato account, account ids, campaign registry and automation ids | Ours. |
| The NavAIgate hero images, logo, fonts and the copy-page template | House brand. |
| The `daniel-voice` step | Private. Members use `tools-voice`. |
| The ClickUp audit task step | Our task system. |

## Shared-file changes needed (I did not edit these)

1. **`.claude-plugin/marketplace.json`**: add `plugins/tools-social/MARKETPLACE_ENTRY.json`.
2. **`scripts/build_catalogue.py`**, `CAPABILITIES`: `'tools-social':['social','post','linkedin','schedule','blotato','instagram']`.
3. **`README.md` and `ROADMAP.md`**: list `tools-social` under module 12, tools.
4. **Tests in CI**: `python3 -m unittest discover -s tests/tools-social`.

## Known limits

- With no key set, the plugin's Blotato MCP entry fails to connect until the member adds one. The skill says so.
- The installer cannot write URL MCP servers for Codex and Cursor; the README gives the entries.
- The release receipt lasts 30 minutes; a long session asks again.
