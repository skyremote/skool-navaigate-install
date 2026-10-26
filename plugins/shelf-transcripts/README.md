# shelf-transcripts (AIOS 2.0, module 12: the shelf)

Pull the actual words of a video from its URL, then do the job you asked for with them: decisions, objections, quotes.

This pack wraps the real `transcripts` skill from the first-generation course. The skill is a byte-for-byte copy and is not
rewritten. What 2.0 adds is a one-command install, a tour, tested prompts and a check that the copy has not drifted.

Skills in this pack: `transcripts`, `web-scrape`.

## Install

Install the start plugin `aios` first.

Claude Code: type `/aios install shelf-transcripts` (it runs `aios-guide --harness claude install shelf-transcripts`), then `/reload-plugins`.
Or install it directly:
```
/plugin install shelf-transcripts@navaigate-aios
```

Codex and Cursor, from your checkout of this repository:
```
./install.sh shelf-transcripts
./install.sh shelf-transcripts --check
```

## Keys

Supadata (`SUPADATA_API_KEY`). It is paid and metered, so pull only what you need.

Put keys in `~/.claude/.env`, one `NAME=value` per line, and run `chmod 600 ~/.claude/.env`. Never paste a key into a chat.
The optional settings this pack declares are stored in your system keychain; the skill's own scripts read `~/.claude/.env`
or your shell, so the `.env` file is the one that always works.

This pack carries a copy of the `web-scrape` skill because the transcript client (`supadata.py`) lives in it.
It needs `python3` and `requests` (`python3 -m pip install --user requests`).

If pip answers `externally-managed-environment` (Homebrew Python does), use a virtual environment instead:
```
python3 -m venv ~/.venvs/aios
~/.venvs/aios/bin/python -m pip install requests
export PATH="$HOME/.venvs/aios/bin:$PATH"
```
Put that `export` line in your shell profile so `python3` finds the packages every time.

## Use

Open `prompts.md` and paste one of the prompts into Claude. The prompts use fictional data (Acme Studio, Northwind
Bakery); swap in your own. `/aios learn 12 transcripts` walks the steps in `TOUR.md` with you.

## Licence

MIT.
