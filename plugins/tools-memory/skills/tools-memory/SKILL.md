---
name: tools-memory
description: Share one SQLite database between the member's machines on their own free Turso account (with the public db-sync skill), check it is safe to share before anything moves, and recall or paste clipboard content with Paste and rich-clipboard. Use for "sync my database across machines", "use this app on my laptop and desktop", "find what I copied yesterday", "put this table on my clipboard".
---

# Memory beyond the brain

The member's chats and notes are the `aios-brain` pack (module 5). This pack covers the other two kinds of memory we
use every day: an app's own database that must be the same on every machine, and the clipboard.

## The command

Claude Code: `"${CLAUDE_PLUGIN_ROOT}/bin/tools-memory"`. Codex and Cursor: `tools-memory` (in `~/.local/bin`).

| Command | What it does |
|---|---|
| `doctor` | Turso CLI, db-sync, Paste's MCP server and rich-clipboard: ready, or the install line. |
| `check <database>` | Read-only. Is the file outside file-sync folders? Does any table number its own rows? Is an app holding it open? |
| `sample <folder>` | Two practice databases for Acme Studio: one not ready, one ready. |

## One database on every machine (db-sync on their own Turso)

The public tools: Turso (turso.tech, free tier, the member's own account) and the public `db-sync` skill
(`git clone https://github.com/skyremote/db-sync ~/.claude/skills/db-sync`). The method:

1. **Check first.** `check <their database>`. Fix every NOT READY line before anything moves:
   - move the file out of Dropbox, iCloud, Google Drive, OneDrive and similar folders (file sync corrupts live databases);
   - tables that number their own rows need ids made on the machine (ULID or UUIDv7), or two machines will collide.
     Changing the app's schema is the member's decision; explain it, never do it silently.
2. **Back it up.** Copy the file to a dated `_backup` name before setup.
3. **Run db-sync setup** on the machine with the real data, following its `references/setup.md`: one cloud primary,
   a local copy per machine, online writes only (never Turso's offline-write mode), a lock around each sync, and
   credentials in `~/.config/db-sync/db-sync.env` (chmod 600, never committed, never in a chat).
4. **Prove it**: write one test row on machine A, `db-sync now`, read it on machine B. Then two writes at once from
   both machines, and both rows arrive.
5. **Onboard each other machine** with `db-sync onboard`.

## The clipboard (Paste and rich-clipboard)

- **Recall:** Paste (pasteapp.io, the member's own licence) has a local MCP server. Turn it on in Paste's settings,
  then add `http://127.0.0.1:39725/mcp` (Claude Code: `claude mcp add --transport http paste http://127.0.0.1:39725/mcp`).
  The agent can then search and read clipboard history and pinboards. It stays on their Mac.
- **Paste formatted:** the public rich-clipboard skill puts tables, bold and bullets on the clipboard as rich text
  that pastes cleanly into email, Teams and Word
  (`git clone https://github.com/skyremote/rich-clipboard-skill ~/.claude/skills/rich-clipboard`, MIT).

## Rules

- Never sync a database the member has not checked with `check`, and never without a backup.
- Clipboard history holds passwords and private messages. Search it only for what the member asked for, and never
  copy what you find into files or chats beyond the answer.
- Free tiers only; ask before anything that costs money.
