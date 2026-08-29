---
name: layer-1
description: >
  Build layer 1 context: the machine knows their business. Write or tighten CLAUDE.md / AGENTS.md from what they tell you. Use when they type /layer-1 or say they are on the Context plate.
---

# /layer-1 — Context

The machine should know the business before it starts guessing.

This is not ContextOS. That zip was nine kilobytes and an interview that
wrote four stubs. Use the file their harness already reads (`CLAUDE.md`,
`AGENTS.md`, `.cursor/rules`) and a first pass at **their** voice, not
Daniel's.

## Do this

1. Read what is already in the folder. If it is tight, say so and stop.
2. If empty, write the smallest useful context file from what they tell you:
   who they are, what the company sells, who it is for, how they speak,
   what must never happen. British English if that is their language.
3. If halfway, fill holes only. Do not delete their notes.
4. Git belongs here if they already use it. Do not force a remote on a
   folder that is not ready.
5. Do not install `daniel-voice`. If they want a voice file, `/your-voice`.

When the file would make sense to a stranger on their team, tell them to
type `/aios`.
