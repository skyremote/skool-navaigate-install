# shelf-podcasts (AIOS 2.0, module 12: the shelf)

Find episodes where operators actually talk about your topic, get a ranked shortlist of three with reasons, and pull their full transcripts.

This pack wraps the real `podcasts` skill from the first-generation course. The skill is a byte-for-byte copy and is not
rewritten. What 2.0 adds is a one-command install, a tour, tested prompts and a check that the copy has not drifted.

Skills in this pack: `podcasts`, `web-scrape`.

## Install

Install the start plugin `aios` first.

Claude Code: type `/aios install shelf-podcasts` (it runs `aios-guide --harness claude install shelf-podcasts`), then `/reload-plugins`.
Or install it directly:
```
/plugin install shelf-podcasts@navaigate-aios
```

Codex and Cursor, from your checkout of this repository:
```
./install.sh shelf-podcasts
./install.sh shelf-podcasts --check
```

## Keys

Exa (`EXA_API_KEY`), Firecrawl (`FIRECRAWL_API_KEY`) and Supadata (`SUPADATA_API_KEY`, paid and metered).

Put keys in `~/.claude/.env`, one `NAME=value` per line, and run `chmod 600 ~/.claude/.env`. Never paste a key into a chat.
The optional settings this pack declares are stored in your system keychain; the skill's own scripts read `~/.claude/.env`
or your shell, so the `.env` file is the one that always works.

Podcasts have no separate API. The path that works today is a web search plus YouTube search and transcripts, so
this pack carries a copy of the `web-scrape` skill for its helpers. It needs `python3` and `requests` (`python3 -m pip install --user requests`).

If pip answers `externally-managed-environment` (Homebrew Python does), use a virtual environment instead:
```
python3 -m venv ~/.venvs/aios
~/.venvs/aios/bin/python -m pip install requests
export PATH="$HOME/.venvs/aios/bin:$PATH"
```
Put that `export` line in your shell profile so `python3` finds the packages every time.

## Use

Open `prompts.md` and paste one of the prompts into Claude. The prompts use fictional data (Acme Studio, Northwind
Bakery); swap in your own. `/aios learn 12 podcasts` walks the steps in `TOUR.md` with you.

## Licence

MIT.
