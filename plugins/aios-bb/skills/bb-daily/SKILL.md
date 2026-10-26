---
name: bb-daily
description: Use for the daily loop in bb - "start my day", "what is waiting on me", "hand this to a thread", "what needs review", "close the day". Runs aios-bb today, hand, card and close for the member's AIOS project.
---

# The daily loop in bb

Find the tool: `"${CLAUDE_PLUGIN_ROOT}/bin/aios-bb"` in Claude Code, `aios-bb` elsewhere. Run it from the AIOS
folder (or pass `--project <id>`). If there is no project yet, use `bb-setup` first.

## 1. Start the day
`aios-bb today` lists, in this order: threads waiting on the member (a question or an approval), Review, In
progress and Backlog. Read it back in that order and suggest the first thing to open. Do not start work yet.

## 2. Hand out work
One job per thread, with the check it must pass written into the brief. Write the brief to a file, then:

```
aios-bb hand "Acme weekly report" --prompt-file brief.md --provider codex
```

It starts the thread in its own worktree and puts its card in In progress. Use `--provider claude` or `codex`
per the harness table from module 3, `--plan` to approve a plan before it builds, and `--no-worktree` only for jobs
that do not change files. Two harnesses on the same job, in two threads, is the cheap second opinion.
The brief must end with: "When there is something for me to check, run: aios-bb card review --note '<what>'".

## 3. Review
Open each Review card. The agent should have shown its result inline (an inline artifact) and the check it ran.
If it passes, the member merges or keeps it and moves the card: `aios-bb card done --thread "<title or id>"`. If not, reply
in the same thread with the one thing to fix; the agent moves it back to In progress.

## 4. Close the day
`aios-bb close` lists what is still in Review, what is still running (leave it), and what is Done.
`aios-bb close --archive-done` archives the Done threads. Archived threads stay searchable (`bb thread search`).

Keep each step short. Never move a card for the member without saying so. British English.
