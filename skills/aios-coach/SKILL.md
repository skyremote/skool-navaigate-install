---
name: aios-coach
description: >
  Copy the Your AIOS coach onto the member's machine, load the course
  knowledge pack, and put it online on their host. Use when they type
  /aios-coach, ask for a browser coach, or want the classroom in a tab.
---

# /aios-coach

They build it. They put it online. Their OpenAI key. Same twenty-six
lessons we wrote in this course.

This is **not** GPLS. Do not copy anything from `NavAIgate-2.0` GPLS
routes, cookies, cities, or coach files. This is **not** on navaigate.dev
yet. Do not add a site route. Do not invent a public demo URL.

## Before you speak

Find this plugin root. The skill you are reading lives at
`skills/aios-coach/`. The template is `templates/aios-coach/`.

Read `references/never-ship.md` from the plugin root. Never copy
daniel-voice, brain-sync, turso-search, invoices, Qonto, Autodesk, or
Daniel's chats into the coach.

## Do this

1. Ask where they want the app. Default: a new folder next to their
   project, or `~/Documents/GitHub/aios-coach`. Never Drive. Never
   `NavAIgate-2.0`.
2. Copy `templates/aios-coach/` into that folder. If the destination
   already has their edits, do not wipe it. Refresh `knowledge/your-aios.json`
   only if they ask.
3. The pack is already built from the authored lessons and the skill
   fronts. That **is** the scrape of everything we have been doing in
   this classroom. Do not log into Skool and scrape the live pages.
   If they want extra pages, they add markdown under `knowledge/extra/`
   or a URL list in `knowledge/extra-urls.txt`, then run
   `python3 scripts/build-knowledge.py` from the app folder. Extra URLs
   use **their** `/web-scrape` keys, not yours.
4. They set `OPENAI_API_KEY` on the host (Vercel env, or `.env` locally).
   Optional `OPENAI_MODEL` — try `gpt-5.6-luna`, fall back to `gpt-4o-mini`.
   Never paste Daniel's key.
5. Put it online:

   ```bash
   cd "<their-aios-coach>"
   npx vercel --yes
   ```

   Or connect the folder to their own Vercel / Netlify / Cloudflare
   project. The API route is `POST /api/ask`. Static UI is `public/`.

6. Give them the URL **their** host printed. Write that URL into a
   `DEPLOY.md` in their folder. Do not put it on navaigate.dev.

Then `/aios`.

## What you say

British English. No emojis. No "platform", no "unlock".

If they wanted this on the NavAIgate website: not yet. The cell is
this plugin and their host. Website later, if Daniel says so.
