---
name: daily-brief
description: >
  A morning brief they will actually read: their numbers, yesterday's
  meetings and Slack, what needs attention, written by one model call and
  saved to their project. Use when they type /daily-brief or ask for a
  daily / morning brief on layer 3.
---

# /daily-brief

Every morning, before they open a tab, one file tells them what happened
yesterday and what to do about it. One model call, a few pence a day.
This is the "brief they will read" from `/layer-3`, built.

## Keys

Any of these in `~/.claude/.env`. The first one present is used, in this
order:

```
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
OPENROUTER_API_KEY=...
GEMINI_API_KEY=...
```

`BRIEF_MODEL=` overrides the model name if the default for that provider
has moved on. Python 3.10+. `pip install -r scripts/requirements.txt`
(requests, python-dotenv, matplotlib). The scripts run **from their
project folder**; that is where the brief reads context and writes
`outputs/daily-brief/`.

## What it reads

- `CLAUDE.md` / `AGENTS.md` and anything in `context/*.md`. That is the
  business context. `/layer-1` should have written it.
- `funnel.md` (copy `templates/funnel.md`, fill it in). Each line maps a
  label to `table.column` in their SQLite file. `/layer-2` decided which
  three numbers matter; this is where they go.
- The SQLite file: `DB_PATH` in `.env`, or the first `.db` under `data/`.
  Tables need a `date` column for the 7-day averages.
- A `meetings` table and a `slack_messages` table, **if they exist**. If
  not, those sections are simply left out.

## Do this

1. Check the folder. If there is no `CLAUDE.md`, send them to `/layer-1`
   first. If there are no numbers at all, the brief still runs on context
   alone; say so, do not fake a dashboard.
2. Check the key: `python3 ~/.claude/skills/daily-brief/scripts/model.py`
   says which provider and model will be used. None found: stop and ask
   for one.
3. Pick a preset with them: `solo` (numbers, signals, actions),
   `small_team` (adds meetings, Slack, recommendations), `agency` (adds
   per-department and cross-stream patterns). Put it in `.env` as
   `BRIEF_PRESET`.
4. First run, nothing saved:
   ```bash
   cd <their project>
   python3 ~/.claude/skills/daily-brief/scripts/daily_brief.py --test
   ```
   Read it with them. Too long, too short, wrong sections, wrong metric
   mapping: fix `funnel.md` or the preset and run again. Do not automate
   until they like it.
5. Real run: same command without `--test`. It saves
   `outputs/daily-brief/YYYY-MM-DD.md` and a PNG dashboard next to it.
6. Schedule it after their data lands. macOS:
   `templates/com.aios.daily-brief.plist` (fill `__PYTHON__`, `__HOME__`,
   `__WORKSPACE__`, then `cp` to `~/Library/LaunchAgents/` and
   `launchctl load`). Linux:
   `0 7 * * * cd /path/to/project && python3 ~/.claude/skills/daily-brief/scripts/daily_brief.py >> data/daily-brief.log 2>&1`.
   The machine has to be awake.
7. Add one line to their `CLAUDE.md`: where the briefs live and what time
   they run. If they want it somewhere other than a file, that is a
   `/new-capability` job on top of `outputs/daily-brief/`.

## Known gaps

- Nothing in this plugin fills a `meetings` or `slack_messages` table.
  Those came from a collector we do not ship. If they capture meetings
  (Granola, a transcript folder), wiring that into SQLite is a
  `/new-capability` job. The brief works without them.
- Default model names per provider are today's; if a provider says the
  model does not exist, set `BRIEF_MODEL`.
- The OpenAI and OpenRouter calls send no output cap (the newer models
  reject the old parameter); the prompt's word budget does that job.

Then `/aios`.
