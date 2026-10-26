---
name: bb-cockpit
description: Use when someone asks how bb works or how to use it well - threads, sections, the kanban board, a worktree per thread, inline artifacts, slash commands, mods (plugins), or seeing every Mac's threads in one place. Explains each with the exact bb command.
---

# bb as the cockpit

Answer the member's question with the part below that fits, the exact command, and one thing to try.
For anything not covered, run `bb guide` or `bb guide <chapter>` and quote it. Never guess a bb command.

## The words
- **Project**: one folder or repo. The AIOS folder is one project (`aios-bb setup` makes it).
- **Thread**: one agent conversation, the unit of work. Each thread picks its harness (provider), for example
  Claude Code or Codex, and its model. Start one with the New thread button, or
  `bb thread spawn --project <id> --title "..." --prompt-file brief.md --provider codex`.
- **Environment**: where a thread runs. Project checkout (the folder itself), Worktree (a fresh git worktree,
  so two threads never edit the same files at the same time) or Personal workspace (no project).
- **Section**: a group of threads in the sidebar. `bb thread section create Review`,
  `bb thread update <thread> --section <section-id>`.
- **Machine**: a computer bb runs threads on. One machine runs the bb server.

## Threads side by side
Start one thread in Claude Code and one in Codex on the same small job, each in its own worktree, and open them
in split panes to compare. A thread can start another thread and is told when it finishes (`--parent-self`).

## The kanban board
Four lanes: Backlog, In progress, Review, Done. A card moves to Review when there is something for the member to
check, and to Done when it is finished. `aios-bb card review --note "Report ready"` moves the current thread's card
(inside a bb thread it knows which thread it is). With a kanban plugin it moves the card on the plugin's board;
without one it moves the thread into the section with the same name. Agents should move their own card.

## A worktree per thread
Pick Worktree when starting a thread (or `--new-environment worktree`). bb makes a new git branch and folder, so
the main folder stays clean until the member merges. Commit `.bb-env-setup.sh` at the folder root if new worktrees
need setup, and `.worktreeinclude` to copy untracked files such as `.env` into them.

## Inline artifacts
An agent can show an HTML or Markdown file inside the chat, rendered, instead of a path. It writes the file, then
puts this on its own line, outside a code block: `::inline-vis{file="reports/weekly_v1.html"}` (a path inside the
thread's workspace). Files saved in the thread's own storage use
`::inline-vis{source="thread-storage" file="artifacts/weekly_v1.html"}`. `bb thread open <path>` opens a file in
the side panel.

## Slash commands
Type `/` in the composer. The list holds the harness's own commands, every skill (each skill is a slash command),
and bb's commands. A folder skill at `.bb/skills/<name>/SKILL.md` becomes `/<name>` in every thread of that project.
`bb thread commands <thread>` lists what a running thread offers.

## Mods (plugins)
bb plugins add panels, boards, commands and tools. `bb plugin search <word>`, `bb plugin install <name>`,
`bb plugin list`, `bb plugin disable <id>`. They are full-trust code: install only what the member trusts, and
`bb plugin safe-mode on` stops every installed plugin if something misbehaves.

## The fleet: every Mac in one place
One Mac runs the bb server, and other Macs join as machines (Settings, Machines), so their threads show in the
same window and a thread can be started on a chosen machine (`--machine <name>`). `bb machine list` shows them.
Keep the server Mac awake. For the phone and other browsers, `bb account login` turns on remote access at
`https://<handle>.getbb.app`, and `bb settings mobile-app` prints the phone app links.

End with one thing to try now. British English. Use fictional names in examples.
