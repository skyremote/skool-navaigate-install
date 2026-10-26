---
name: new-app
description: >
  Turn a design into a phased build plan, then implement one phase at a
  time. Use when they type /new-app or hand over a mockup and say build this.
---

# /new-app

Do not ask an agent to hold a whole application in its head. Scope first.
Then one phase, then the next.

There is no `/prime`. Context is `/layer-1` and the files already in the
folder. Do not invent a priming ritual.

## Do this

1. Take the design (Pencil, Figma, a screenshot, a sketch) and one sentence
   about what the app is for.
2. Write a **plan file** in this project: stack, data shape, auth, pages,
   what talks to what, and the build sliced into ordered phases. The plan
   is the output of this step. Not code.
3. Each phase must fit in one honest session — database, then auth, then
   the core views, and so on. If a phase is too big, split it.
4. Generate a detailed plan per phase (`plans/phase-01.md`, then 02…).
5. **Build phase 1 to completion before phase 2.** Sequential is slower by
   an hour and saves a day. Later phases assume earlier ones exist.
6. Fresh session per phase if the harness lets them. Point that session at
   that phase file only.

If they do not have a design yet, stop and get one. Do not invent screens.

Then `/aios`.
