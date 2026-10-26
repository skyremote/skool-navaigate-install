---
name: thumbnails
description: >
  Generate on-brand video thumbnails from THEIR photos. Four concepts, then
  a composited headline so the text is spelled correctly. Use when they type
  /thumbnails or ask for a YouTube / Reels thumbnail.
---

# /thumbnails

The thumbnail is the click. They get four concepts, side by side, in their
look — not Daniel's face, not a Canva midnight job.

## What you need from them

1. A small catalogue of **their** photos, tagged by expression, pose and
   setting. If they have none, stop and get that first. Thirty minutes here
   pays back on every thumbnail.
2. Their brand rules if they have them (colours, type, what they will never
   publish). If they do not, ask three questions and write a one-page rule
   file in this project.
3. A Gemini key in `~/.claude/.env` as `GEMINI_API_KEY` (Nano Banana 2 /
   `gemini-3.1-flash-image`). If the key is missing, tell them exactly
   where to put it.

Do not use Daniel's reference photo. Do not install `social-trio`.

## Do this

1. Research the topic for one or two visual anchors (product, model, place).
   Official sources only. If there is nothing safe, say so and stay source-led.
2. **Stage 1 — image, no text.** Generate four scene concepts in parallel.
   The model must not render words. Feed **their** photo as the identity
   reference when the concept needs a face. 16:9 for YouTube, 9:16 only
   when the output is genuinely portrait.
3. Lay the four out as a 2x2 so they can judge them against each other.
   They pick one in plain English ("the second, warmer, face left").
4. **Stage 2 — headline as a real text layer.** Composite the title after
   the image. If they have `thumbtext.py` or a compositor in this project,
   use that. If they do not, write the headline on with a local overlay
   (heavy condensed sans, white fill, dark stroke) — never let the image
   model spell the words.
5. Save into their working folder as `<topic>_thumbnail.png` plus the three
   runners-up if they want them.

Then `/aios` and they pick the next module.
