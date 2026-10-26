---
name: your-brain
description: >
  Help them start THEIR memory and keep it in step across machines. Use when
  they type /your-brain. Never install brain-sync or turso-search.
---

# /your-brain

They get a short pack back from an old chat or a notes folder — not a dumped
transcript — and if they use more than one machine, that database stays in
step. Daniel's Turso replica, `brain-sync` and `torso-search` stay on his
machines.

The public kit for the sync job is `db-sync`:
https://github.com/skyremote/db-sync

Same idea as his Torso sync. Their SQLite or libSQL. Their Turso. Not his
brain.

## Do this

1. If they already have Obsidian, a notes folder, or exported transcripts,
   start there. Do not make them adopt his cloud.
2. Write the smallest useful store they own — a folder convention or a local
   SQLite. Secrets stay local. The file must sit **off** Google Drive /
   Dropbox / iCloud.
3. If they have two machines, clone `skyremote/db-sync` and run
   `/db-sync setup` on the machine that holds the file, then
   `/db-sync onboard` on the others. `/db-sync now` when they want a push.
4. Never clone `brain-sync` or `turso-search` into their project.

Then `/aios`.
