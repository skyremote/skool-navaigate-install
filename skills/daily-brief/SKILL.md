---
name: daily-brief
description: >
  A morning brief they will actually read: their numbers, yesterday's
  meetings and Slack, what needs attention, written by one model call and
  saved to their project (Telegram optional). Use when they type
  /daily-brief or ask for a daily / morning brief on layer 3.
---

# /daily-brief

Every morning, before they open a tab, one file tells them what happened
yesterday and what to do about it. One Gemini call, roughly a cent a day.
This is the "brief they will read" from `/layer-3`, built.

## Keys

In `~/.claude/.env`:

```
GEMINI_API_KEY=...            # required, free tier at aistudio.google.com/apikey
TELEGRAM_BOT_TOKEN=...        # optional, from /telegram-command-bot
TELEGRAM_GROUP_ID=...         # optional
```

Python 3.10+. `pip install -r scripts/requirements.txt` (aiogram only if
Telegram is on). The scripts run **from their project folder**; that is
where the brief reads context and writes `outputs/daily-brief/`.

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
2. Pick a preset with them: `solo` (numbers, signals, actions),
   `small_team` (adds meetings, Slack, recommendations), `agency` (adds
   per-department and cross-stream patterns). Put it in `.env` as
   `BRIEF_PRESET`.
3. First run, nothing saved:
   ```bash
   cd <their project>
   python3 ~/.claude/skills/daily-brief/scripts/daily_brief.py --test
   ```
   Read it with them. Too long, too short, wrong sections, wrong metric
   mapping: fix `funnel.md` or the preset and run again. Do not automate
   until they like it.
4. Real run: same command without `--test`. It saves
   `outputs/daily-brief/YYYY-MM-DD.md` and a PNG dashboard next to it. If
   the Telegram keys are set it also sends the brief to a "Daily Brief"
   topic in their group.
5. Schedule it after their data lands. macOS: `templates/com.aios.daily-brief.plist`
   (fill `__PYTHON__`, `__HOME__`, `__WORKSPACE__`, then
   `cp` to `~/Library/LaunchAgents/` and `launchctl load`). Linux:
   `0 7 * * * cd /path/to/project && python3 ~/.claude/skills/daily-brief/scripts/daily_brief.py >> data/daily-brief.log 2>&1`.
   The machine has to be awake.
6. Add one line to their `CLAUDE.md`: where the briefs live and what time
   they run.

## Known gaps

- Nothing in this plugin fills a `meetings` or `slack_messages` table.
  Those came from a collector we do not ship. If they capture meetings
  (Granola, a transcript folder), wiring that into SQLite is a
  `/new-capability` job. The brief works without them.
- Reply-to-drill-in needs `/telegram-command-bot` running with the brief
  topic registered. Without it the brief is one-way.
- Gemini is the only engine wired. Pricing in `daily_brief.py` is a
  static table; update it if Google changes the list.

Then `/aios`.
