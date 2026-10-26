# shelf-daily-brief (AIOS 2.0, module 12: the shelf)

Every morning, one file tells you what happened yesterday and what to do about it, from your own numbers, for a few pence a day.

This pack wraps the real `daily-brief` skill from the first-generation course. The skill is a byte-for-byte copy and is not
rewritten. What 2.0 adds is a one-command install, a tour, tested prompts and a check that the copy has not drifted.

Skills in this pack: `daily-brief`.

## Install

Install the start plugin `aios` first.

Claude Code: type `/aios install shelf-daily-brief` (it runs `aios-guide --harness claude install shelf-daily-brief`), then `/reload-plugins`.
Or install it directly:
```
/plugin install shelf-daily-brief@navaigate-aios
```

Codex and Cursor, from your checkout of this repository:
```
./install.sh shelf-daily-brief
./install.sh shelf-daily-brief --check
```

## Keys

One model key, any of OpenAI, Anthropic, OpenRouter or Gemini, in `~/.claude/.env`. Python 3.10+ with `requests`, `python-dotenv` and `matplotlib`.

Put keys in `~/.claude/.env`, one `NAME=value` per line, and run `chmod 600 ~/.claude/.env`. Never paste a key into a chat.
The optional settings this pack declares are stored in your system keychain; the skill's own scripts read `~/.claude/.env`
or your shell, so the `.env` file is the one that always works.

Install the Python packages once: `python3 -m pip install --user requests python-dotenv matplotlib`.

If pip answers `externally-managed-environment` (Homebrew Python does), use a virtual environment instead:
```
python3 -m venv ~/.venvs/aios
~/.venvs/aios/bin/python -m pip install requests python-dotenv matplotlib
export PATH="$HOME/.venvs/aios/bin:$PATH"
```
Put that `export` line in your shell profile so `python3` finds the packages every time.
The scripts run from your project folder, which is where the brief reads context and writes `outputs/daily-brief/`.

## Use

Open `prompts.md` and paste one of the prompts into Claude. The prompts use fictional data (Acme Studio, Northwind
Bakery); swap in your own. `/aios learn 12 daily-brief` walks the steps in `TOUR.md` with you.

## Licence

MIT.
