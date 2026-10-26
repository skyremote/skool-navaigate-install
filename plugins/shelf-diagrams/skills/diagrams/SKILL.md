---
name: diagrams
description: >
  Draw architecture diagrams from plain English with D2. Render, look at
  the PNG, iterate. Use when they type /diagrams or ask for a system /
  pipeline / funnel diagram.
---

# /diagrams

They describe the system. You write D2, render a PNG, look at it, and fix
what is ugly. No canvas. No zip.

## Setup

If `d2` is not on the PATH, install it (https://d2lang.com) and prove it
with a one-box diagram before you touch their real architecture.

No API key. D2 is free.

## Patterns to start from

Pick the closest, then change it:

1. **Master overview** — the five plates and what talks to what
2. **Data pipeline** — source → store → ask
3. **Automation schedule** — trigger → job → human checkpoint
4. **Command system** — harness → skill → outcome
5. **Education / funnel** — attention → lesson → install → result

## Do this

1. Ask what the diagram is for: their own head, a client, or a team doc.
   That changes how much detail you keep.
2. Write the D2 in the project (`diagrams/<slug>.d2`).
3. Render to PNG.
4. **Look at the image.** If labels overlap, boxes are crammed, or the
   flow reads backwards, fix the D2 and render again. Do not hand them
   the first pass if it is ugly.
5. Offer a second version: one glance for a client, one expanded for them.

Then `/aios`.
