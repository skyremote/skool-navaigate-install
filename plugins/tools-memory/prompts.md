# Prompts: tools-memory

Paste one into Claude Code, Codex or Cursor.

## 1. Is my database safe to share between machines?

```text
Use tools-memory. Check whether ~/path/to/my-app.db is safe to keep in step across my two Macs, and explain anything that has to change first in plain English. Do not change the database.
```

**What it does:** reads the database without changing it and lists what would break if two machines shared it.
**How you know it worked:** you get `READY to share` or a short list of fixes, and the file's modified time has not changed.

## 2. One database, two machines

```text
Use tools-memory and db-sync. Set up my database at ~/Apps/orders.db to sync between this Mac and my laptop on my own free Turso account. Back it up first, then prove it with one test row.
```

**What it does:** checks the database, backs it up, runs db-sync setup on your Turso account and writes one test row.
**How you know it worked:** the test row written on this Mac shows up on the laptop after `db-sync now`.

## 3. Find what I copied

```text
Use tools-memory and Paste. Find the client address I copied yesterday, then put this table on my clipboard so it pastes properly into an email: <paste the table>
```

**What it does:** searches your Paste history for the address, then puts the table on the clipboard as rich text.
**How you know it worked:** it shows the address it found, and the table pastes into your email with its columns intact.
