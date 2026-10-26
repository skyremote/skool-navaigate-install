---
name: bb-setup
description: Use when someone wants to run their AIOS from bb (getbb.app), install bb, add their AIOS folder as a bb project, or set up the board. Creates the bb project for the folder and the four lanes (Backlog, In progress, Review, Done), and checks bb is ready.
---

# Set up bb for the AIOS folder

bb is the app that runs Claude Code, Codex and other harnesses side by side, one thread each.
Find the tool: in Claude Code run `"${CLAUDE_PLUGIN_ROOT}/bin/aios-bb"`; elsewhere `aios-bb` (in `~/.local/bin`).

## 1. Install bb (the member does this)
1. Download bb from https://getbb.app and open it. It runs a small server on their Mac.
2. Sign in to the harnesses they use inside bb (Claude Code, Codex). bb uses their own subscriptions.
3. Put the `bb` command on PATH for terminals outside bb: `bb settings cli-command install`
   (inside a bb thread, `bb` already works).

## 2. Check, then set up
From the AIOS folder:

```
aios-bb doctor
aios-bb setup --dry-run
aios-bb setup --name "<project name>"
```

`doctor` checks that bb answers, that Claude Code and Codex are available as bb providers, that the folder is a
git repository (worktrees need it), and whether a kanban plugin is installed. `setup` creates one bb project whose
source is the folder (`bb project create --name ... --root <folder>`), or keeps the one that already points there,
and creates four sidebar sections: Backlog, In progress, Review, Done. It never deletes or renames anything.

If the folder is not a git repository, offer the commands and let the member run them:
`git init && git add -A && git commit -m "Start"`. Without git, threads still run, but only in the project folder.

## 3. The board
The four sections are the board, and every thread is a card in one of them. If the member wants a drag-and-drop
board view, a kanban plugin from the bb store adds one: `bb plugin search kanban`, read the description, then
`bb plugin install <name>` (plugins are full-trust code, so pick ones they trust). When a plugin adds a `bb kanban`
command, `aios-bb card` moves cards on it instead of between sections.

## 4. Rules for every thread
bb threads read the folder's AGENTS.md through the harness, so nothing extra is needed. For rules that apply only
inside bb, add `.bb/AGENTS.md` in the folder and commit it, so new worktrees include it.

Finish with: open bb, pick the project in the sidebar, start one thread. Then `bb-daily` for the daily loop.
British English. Never print tokens.
