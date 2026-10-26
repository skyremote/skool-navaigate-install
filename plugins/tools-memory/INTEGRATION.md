# tools-memory: integration notes for the chief of staff

## Scope, and the overlap with aios-brain

The tools map's "memory you own" row predates `aios-brain` (module 5, on main), which now covers chat capture, search
and the member's own Turso sync. This pack does not repeat it. It covers the two other memory tools we use: db-sync
for any app's SQLite database, and Paste plus rich-clipboard for the clipboard.

## Where the pack came from

| Source | Owner and licence | What this pack took |
|---|---|---|
| `db-sync` (skyremote, public) | Ours, no licence file | Not copied. The member clones it. Its file-sync-folder rule and its unique-id rule became `tools-memory check`. |
| `rich-clipboard` (skyremote/rich-clipboard-skill) | Ours, MIT | Linked with the clone command. |
| Paste | Third party | The member's own app and its local MCP server. |

## Left out, and why

| Left out | Why |
|---|---|
| `brain-sync`, `turso-search`, the brain MCP and our Turso database | Our brain and its credentials. |
| `graphify` | Rarely used; not part of this pack. |

## Shared-file changes needed (I did not edit these)

1. **`.claude-plugin/marketplace.json`**: add `plugins/tools-memory/MARKETPLACE_ENTRY.json`.
2. **`scripts/build_catalogue.py`**, `CAPABILITIES`: `'tools-memory':['database','sqlite','sync my database','clipboard','paste','turso db']`.
   Keep `'brain'`, `'memory'` and `'remember'` on `aios-brain`.
3. **`README.md` and `ROADMAP.md`**: list `tools-memory` under module 12, tools.
4. **Tests in CI**: `python3 -m unittest discover -s tests/tools-memory`.
