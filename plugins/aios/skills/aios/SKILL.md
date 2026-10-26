---
name: aios
description: Check my AIOS, show my next module, install any AIOS pack with its dependencies, and teach a module step by step in my own folder. Use for /aios, /aios learn <module>, where do I start, what next, or "set up my brain" style requests.
---

# Your AIOS

## The command
Every action goes through one command, `aios-guide`:
- **Claude Code:** `"${CLAUDE_PLUGIN_ROOT}/bin/aios-guide"`.
- **Codex and Cursor:** `aios-guide` (linked into `~/.local/bin` by `./install.sh aios`).
  If it is not on PATH, use `~/.local/bin/aios-guide`.
Below, `aios-guide` means whichever applies. Pass `--harness claude` or `--harness codex` when unsure.
If the command cannot run, say the check is unverified. Never guess an install state.

## 1. First visit: empty, halfway or already running?
Ask: **Is this machine empty, halfway, or already running?** Keep existing work.
Look at the current folder's AGENTS.md, CLAUDE.md and harness folders. Never wipe them.
Then run `aios-guide next`. It reads the catalogue (every pack, its module, dependencies,
hooks, MCP servers and settings) and what each harness has installed.
- **Empty:** start at module 1. Offer `aios-guide learn 1`.
- **Halfway:** ask which modules they finished. Record only the ones they confirm.
- **Already running:** show `aios-guide list`, then offer the pack they ask for.
Report installed and enabled separately. Installed does not mean loaded until a reload or restart.
Never print tokens or config values.

## 2. v1 members
If `aios-guide next` reports v1 skills, explain that v1 keeps working at its old paths,
with fixes only until 26 April 2027. Offer to keep it or review a guided move.
Never migrate because v1 was found. For a guided move, show the affected links and the
backup folder, ask the member to confirm, then run `./install.sh aios --migrate-v1` from
the checkout. It moves only the conflicting start links into `~/.local/share/aios/v1-backups/`.
Nothing is deleted. Claude Code can install the new packs beside the old plugin.

## 3. Install on demand
Install when the member reaches a module, or asks for a capability ("set up my brain").
1. Find the pack: `aios-guide find <their words>`, or a module number, or `aios-guide list`.
2. Say what it adds: skills, commands, hooks, MCP servers and any settings it asks for.
   Sensitive settings (keys, tokens) are asked by Claude Code and kept in the keychain. Never put them in files.
3. Ask before installing. Then run `aios-guide install <pack>`. It does the right thing per harness:
   - **Claude Code:** `claude plugin install <pack>@navaigate-aios`. Dependencies come with it.
     Then it runs `claude plugin details <pack>` as proof. Tell the member to type `/reload-plugins`.
   - **Codex and Cursor:** `install.sh <pack>` from the recorded checkout. The installer installs
     dependencies first, in order, once each, and stops on a cycle. Then `install.sh <pack> --check`
     proves it. Tell the member to restart Codex or Cursor.
4. Show the proof lines. If the proof fails, say so and show the failing line.

The whole framework in one go: `aios-guide install aios-complete`. It brings `aios`,
`aios-brain` and every core pack for modules 2 to 11. Shelf packs (module 12) stay optional.

## 4. Hooks
- **Claude Code** runs a pack's hooks itself. `aios-guide verify <pack>` checks they are active.
- **Cursor:** the installer merges the pack's hooks into `~/.cursor/hooks.json`, after a backup,
  and keeps every existing entry. It names any hook Cursor has no event for.
- **Codex:** the installer writes the same rule into `~/.codex/AGENTS.md` as a written rule.
  Say plainly that Codex does not enforce it. The member, or the agent, has to follow it.

## 5. /aios learn <module>
Teach the module inside the member's own folder, one step at a time.
1. Run `aios-guide learn <module>`. It prints the lesson link and the next unchecked step:
   what to do, the command, what they should see, and the check.
2. If the pack is not installed, offer to install it first (section 3).
3. Explain the step in one or two sentences. Let the member run the command, or run it with
   their permission inside their folder.
4. Run the step's check. Compare the result with "You should see". Only when it matches, run
   `aios-guide learn <module> --done <step>`. If it does not match, help fix it before moving on.
5. Repeat until every step is checked. Then ask if the module is finished. Only if they say yes,
   run `aios-guide progress --complete <module>`.
If a pack has no tour yet, give the Skool lesson link and its skills, and keep to one small action.

## The twelve modules
1. Start here — `aios`. 2. Your folders and your rules — `aios-rules`. 3. The harnesses —
`aios-harnesses`. 4. bb as the cockpit — `aios-bb`. 5. Memory you own — `aios-brain`.
6. Skills that earn their place — `aios-skills`. 7. Agents without sprawl — `aios-agents`.
8. Make it verifiable — `aios-verify`. 9. Working methods — `aios-methods`. 10. Models,
effort and cost — `aios-models`. 11. Ship it to others — `aios-ship`. 12. The shelf — optional
`shelf-*` packs. `aios-guide list` shows which have shipped. Offer only packs it lists.

## First-time install (for members who ask how they got here)
- Claude Code: `/plugin marketplace add skyremote/skool-navaigate-install`, then
  `/plugin install aios@navaigate-aios`.
- Codex and Cursor: clone the repository, then run `./install.sh aios` in it. That records the
  checkout so `aios-guide` can install every later pack.

Keep replies short: what exists, the next module, one action. British English.
