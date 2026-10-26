---
name: aios
description: Check my AIOS setup, show which packs each harness has, and help me choose the next step. Use for /aios, where do I start, what next, or installing an AIOS pack.
---

# Your AIOS

Ask: **Is this machine empty, halfway, or already running?** Keep existing work.
Inspect the current folder's AGENTS.md, CLAUDE.md and harness folders. Never wipe them.
Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/status.py"` to check packs across
Claude Code, Codex, Cursor and shared agent skills. In Codex or Cursor, resolve
this SKILL.md symlink and use the pack's `scripts/status.py`, two folders above
`skills/aios`. If the script cannot run, report the check as unverified.
Report installed and enabled separately. Skill links and MCP configuration do
not prove that a restarted harness has loaded them. Never print tokens or config values.

If the inventory's `v1` reports old skills or the old marketplace plugin, explain
that v1 stays at its existing paths with fixes-only support until 26 April 2027.
Offer to keep it or review a guided move. Never run a migration merely because
v1 was detected. Show the exact affected links and backup location, ask the
member to confirm, then use `./install.sh aios --migrate-v1` for Codex/Cursor.
It moves only the conflicting start links into `~/.local/share/aios/v1-backups/`
and leaves all other v1 skills and the Claude v1 plugin available. No files are
deleted. Claude Code can install the new pack beside the old namespaced plugin.

Ask which module they are in. Follow this path, one step at a time:

1. Start here: one loop, small context, a check it can run — `aios`.
2. Your folders and your rules — `aios-rules`.
3. The harnesses — `aios-harnesses`.
4. bb as the cockpit — `aios-bb`.
5. Memory you own — `aios-brain`.
6. Skills that earn their place — `aios-skills-kit`.
7. Agents without sprawl — `aios-agents`.
8. Make it verifiable — `aios-verify`.
9. Working methods — `aios-methods`.
10. Models, effort and cost — `aios-models`.
11. Ship it to others — `aios-ship-it`.
12. The shelf — choose video, decks, invoices, voice, design, research or content.

Only `aios` and `aios-brain` ship in phase 1. Say when a pack is planned; do not
try to install it. Give the next lesson's small action while it is being built.
The script's next module is provisional: only the member can confirm a lesson
is complete. If they want progress saved, write their confirmed numbers to
`~/.local/share/aios/progress.json`, as `{"completed_modules":[1,2]}`. Installation
alone never completes a module. Members already running can pick the brain now.

To install one available pack in Claude Code:

```
/plugin marketplace add skyremote/skool-navaigate-install
/plugin install <pack>@navaigate-aios
```

For this unpublished review, add the local checkout path instead of GitHub.
In Codex and Cursor, from the member's checkout run `./install.sh aios`, then
`./install.sh <pack>`. It links only the requested pack into `.codex/skills`,
`.cursor/skills` and `.agents/skills`, preserving other skills and backing up
MCP config before changes. Restart the harness, then run `/aios` again.
Claude Code may expose the namespaced command `/aios:aios`; use that if needed.

Keep the response short: what exists, the next module, one action. British English.
