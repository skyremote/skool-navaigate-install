---
name: tools-images
description: Plan and make images and AI video on the member's own Higgsfield account (with Higgsfield's own published skills and CLI), writing video prompts shot by shot, checking them before credits are spent, and logging every generation. Use for "make a product photo", "make a video of", "write a Seedance prompt", "animate this image", "an ad clip".
---

# Images and AI video, planned before you pay

The member uses their own Higgsfield account (higgsfield.ai, credits) and Higgsfield's own skills, which drive the
`higgsfield` CLI: `higgsfield-generate`, `higgsfield-product-photoshoot`, `higgsfield-marketplace-cards` and
`higgsfield-soul-id`. This skill is how we use them: brief first, the prompt written shot by shot, a check before
anything costs credits, and a manifest so every output keeps its prompt and model.

## The command

Claude Code: `"${CLAUDE_PLUGIN_ROOT}/bin/tools-images"`. Codex and Cursor: `tools-images` (in `~/.local/bin`).

| Command | What it does |
|---|---|
| `doctor` | Higgsfield CLI installed? Signed in? Higgsfield's skills installed? |
| `sample <folder>` | A practice 10-second video prompt (fictional Northwind Bakery). |
| `check <prompt.txt> [--seconds N]` | Four sections, shots back to back, shot count for the length, one signature shot, no hype words. |
| `log <folder> --prompt <file> --model <m> [--job id] [--result url]` | Adds the generation to `manifest_v1.jsonl` in that folder. |

## Setup (once)

1. Higgsfield's CLI: `curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh`, then
   `higgsfield auth login` (opens the browser, their own account).
2. Higgsfield's skills (MIT): `npx skills add higgsfield-ai/skills`, or in Claude Code
   `/plugin marketplace add higgsfield-ai/skills` then `/plugin install higgsfield@higgsfield`.
3. `doctor` until all three say ready.

## The method

1. **Brief.** What it is for, where it will be seen (aspect ratio), how long, what must be in it, what must not.
   Ask one question if something essential is missing; otherwise decide and say what you decided.
2. **Images:** product shots go to `higgsfield-product-photoshoot`, listing images to `higgsfield-marketplace-cards`,
   everything else to `higgsfield-generate`. Ask for the member's own product photos as references.
3. **Video:** write the prompt in four sections (read `references/video-prompts.md`):
   1. the shot-by-shot timeline, `SHOT 1 (0:00-0:02) — name` with an `EFFECT:` line, what happens, the camera and the
      transition;
   2. a master effects inventory;
   3. an effects density map;
   4. the energy arc.
   Then `check <prompt> --seconds <target>` and fix every line. Show it to the member.
4. **Cost.** Before a video or a batch, tell them which model and how many generations. Video costs far more than
   images. Wait for their go on anything beyond a single test image.
5. **Generate** with Higgsfield's skill, then `log` it. Save outputs as `_v1`, `_v2`; never overwrite.
6. **Look at it.** Check hands, text and faces before calling it done. Say what is off.

## People and likeness

- Soul characters (`higgsfield-soul-id`) only from the member's own face, or someone who gave written consent.
- Never a real public figure, never a lookalike of one, never a living artist's name as a style.
- This pack ships no characters, faces, prompts or brand assets of ours. The member brings their own.
