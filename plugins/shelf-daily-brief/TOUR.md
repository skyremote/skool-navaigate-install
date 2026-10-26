# Tour: module 12, the shelf: daily brief

`/aios learn 12 daily-brief` follows these steps in the member's own folder, one at a time.
Run each command for the member, or have them type it. Show the real output, then check it before the next step.
Never print a key value. If a check fails, stop, fix that one thing, and check again.

## Step 1: Find the skill
- **Do:** check that the skill is installed.
- **Command:** `ls "${CLAUDE_PLUGIN_ROOT}/skills/daily-brief/SKILL.md"` (Codex: `ls ~/.codex/skills/daily-brief/SKILL.md`; Cursor: `~/.cursor/skills`).
- **They should see:** the path of `SKILL.md`.
- **Check:** if it is missing, run `aios-guide --harness claude install shelf-daily-brief` (what `/aios install shelf-daily-brief` runs), then `/reload-plugins`. For Codex and Cursor run `./install.sh shelf-daily-brief` from the checkout and restart.

## Step 2: Install the Python packages
- **Do:** install the three packages the script needs.
- **Command:** `python3 -m pip install --user requests python-dotenv matplotlib`
- **They should see:** `Successfully installed ...` or `Requirement already satisfied`.
- **Check:** `python3 -c "import requests, dotenv, matplotlib; print('ok')"` prints `ok`.

## Step 3: Check the keys, by name only
- **Do:** confirm the key names are in the member's `~/.claude/.env`. Never print a value.
- **Command:** `grep -oE '^(OPENAI_API_KEY|ANTHROPIC_API_KEY|OPENROUTER_API_KEY|GEMINI_API_KEY)' ~/.claude/.env`
- **They should see:** one line per key, for example `OPENAI_API_KEY`.
- **Check:** a missing name means: say which key, say where to get it, add `NAME=value` to `~/.claude/.env` (then `chmod 600 ~/.claude/.env`), and stop until it is there.

## Step 4: First run, nothing saved
- **Do:** run it in test mode in a project folder that has a `CLAUDE.md`, `funnel.md` and a SQLite file in `data/`.
- **Command:** `python3 "${CLAUDE_PLUGIN_ROOT}/skills/daily-brief/scripts/daily_brief.py" --test`
- **They should see:** a log line naming the provider and model it used (for example `openai / gpt-5.4-mini`), then a brief printed to the screen, not saved.
- **Check:** read it with the member. Wrong sections or numbers: fix `funnel.md` or the preset, run again. Do not schedule yet. Do not rely on `model.py` alone to learn the provider: it sees only keys exported in the shell, not those in `~/.claude/.env`.

## Step 5: Real run
- **Do:** run it for real once the member likes it.
- **Command:** `python3 "${CLAUDE_PLUGIN_ROOT}/skills/daily-brief/scripts/daily_brief.py"`
- **They should see:** a saved file `outputs/daily-brief/YYYY-MM-DD.md` and a PNG dashboard beside it.
- **Check:** `ls outputs/daily-brief` shows both. Scheduling comes last, and only if the member asks.

## Recap
Packages and one key, model check, test run, fix, real run, then schedule.
