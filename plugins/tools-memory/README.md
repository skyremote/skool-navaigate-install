# tools-memory (AIOS 2.0, module 12: the shelf, tools)

Memory beyond the brain. Your chats and notes live in the `aios-brain` pack (module 5). This pack is for two other
kinds: an app's own **SQLite database** kept the same on every machine, on your own free **Turso** account with the
public **db-sync** skill, and your **clipboard**, recalled with **Paste** and pasted cleanly with **rich-clipboard**.

- **Check before you share.** `tools-memory check` reads the database (read-only) and stops you if it sits in a
  file-sync folder or if two machines would collide on row numbers.
- **Your accounts.** Turso free tier, your own credentials file, your own Paste licence.

## Install

1. Install the start plugin `aios` first (module 1).
2. For database sync: the Turso CLI (`brew install tursodatabase/tap/turso`, then `turso auth signup`) and
   `git clone https://github.com/skyremote/db-sync ~/.claude/skills/db-sync`.
3. For the clipboard: Paste from pasteapp.io with its MCP server turned on, then
   `claude mcp add --transport http paste http://127.0.0.1:39725/mcp` (Codex and Cursor: add the same URL as an MCP
   server). Optional: `git clone https://github.com/skyremote/rich-clipboard-skill ~/.claude/skills/rich-clipboard`.

**Claude Code:** `/aios install tools-memory` (or `/plugin install tools-memory@navaigate-aios`), then `/reload-plugins`.

**Codex and Cursor**, from your checkout of this repository:
```
./install.sh tools-memory
./install.sh tools-memory --check
```

Needs Python 3.9 or later.

## Use

```
tools-memory doctor
tools-memory sample ~/Memory-practice
tools-memory check ~/Memory-practice/acme-orders_v1.db
tools-memory check ~/path/to/your-app.db
```

Three starter prompts: [prompts.md](prompts.md). The method: [skills/tools-memory/SKILL.md](skills/tools-memory/SKILL.md).

## Licence

MIT for this pack. db-sync and rich-clipboard are separate public repositories; Turso and Paste are third-party
products with their own terms.
