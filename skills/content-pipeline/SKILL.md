---
name: content-pipeline
description: >
  Their content ideas as a pipeline they can see: capture a raw idea,
  develop it into a positioned and packaged concept, schedule it with a
  make-by date. A local SQLite file, three strategy docs, one pipeline.md.
  Use when they type /content-pipeline, say they have ideas everywhere and
  no system, or ask what to make next.
---

# /content-pipeline

Ideas stop living in their notes app. Every one is captured, classified,
developed against their strategy, and given a date. The pipeline is one
markdown file they can open, backed by one SQLite file they own.

`/content-coach` is how we run LinkedIn week to week; this is the store
underneath it. `/thumbnails` makes the image once a video concept exists.

## Keys

None required. Optional, in `~/.claude/.env`:

```
NOTION_API_TOKEN=...          # only for a team-visible calendar
NOTION_PIPELINE_DB_ID=...     # set after --create-db
```

Python 3.10+. `pip install -r scripts/requirements.txt`. Every command
runs **from their project folder**; that is where `data/content.db` and
`content/` live.

## Modes

| They type | What happens | Detail |
|---|---|---|
| `/content-pipeline setup` | Foundation plus the strategy interview | below |
| `/content-pipeline capture <idea>` | Classify, check duplicates, store a stub | `references/capture.md` |
| `/content-pipeline develop #N` | Positioning, packaging, priority, concept doc | `references/develop.md` |
| `/content-pipeline schedule` | Pick, date, make-by, optional Notion | `references/schedule.md` |
| `/content-pipeline schedule review` | Overdue and status changes | same file |

## Setup

1. Check they have a `CLAUDE.md` (from `/layer-1`). Read it. Do not ask
   what it already answers.
2. Foundation, from their project folder:
   ```bash
   S=~/.claude/skills/content-pipeline/scripts
   python3 $S/db.py                  # data/content.db, two tables
   python3 $S/db.py --check
   python3 $S/context_aggregator.py  # counts; empty is fine
   mkdir -p content/concepts && python3 $S/generate_pipeline.py
   ```
3. Platform: YouTube or LinkedIn (or both). Ask once.
4. The strategy interview. Two or three questions at a time, not twenty.
   After each doc, show it and get a yes before the next.
   - `content/strategy.md` from `templates/strategy.md`: cadence, the
     3-5 pillars, peers and how they differ, rules, how they like to plan.
   - `content/brand-and-audience.md` from `templates/brand-and-audience.md`:
     one-line positioning, why anyone should listen, voice, 3-5 audience
     segments (who, what they want, what they need), proof points with
     real numbers.
   - `content/offers-and-funnels.md` from `templates/offers-and-funnels.md`:
     what they sell from free to top tier, the path from content to
     customer, how they mention offers, anything running right now.
   - YouTube only: the titles-and-thumbnails method is taught in the
     classroom (The shelf), not shipped here. If they have their own
     packaging notes, save them as `content/packaging-strategy.md` and
     `develop` reads them.
5. Test it with one real idea: `capture`, then `develop` on that stub.
   Walk both stops with them.
6. Notion, only if they have editors or a designer who needs the
   calendar. Otherwise `content/pipeline.md` is the calendar.

## What it reads for context

`context_aggregator.py` pulls the last seven days from
`published_content`, plus a `youtube_videos` or `meetings` table if some
other `.db` under `data/` has one. Meetings are optional; nothing here
creates them.

## Known gaps

- Capture is from the terminal. An inbox from their phone or a form is
  a `/new-capability` job that calls `write_content_idea`.
- No packaging method ships in this repo; `develop` still asks for
  titles and thumbnails on YouTube and uses `content/packaging-strategy.md`
  only if they wrote one.
- Nothing publishes. This is planning and tracking. `/content-coach` and
  their own hands do the posting.

Then `/aios`.
