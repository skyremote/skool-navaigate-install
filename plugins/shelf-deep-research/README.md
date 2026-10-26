# shelf-deep-research (AIOS 2.0, module 12: the shelf)

Research a question properly across web, papers, Reddit, newsletters and video, with a critic pass and a write-up that labels how sure each claim is.

This pack wraps the real `deep-research` skill from the first-generation course. The skill is a byte-for-byte copy and is not
rewritten. What 2.0 adds is a one-command install, a tour, tested prompts and a check that the copy has not drifted.

Skills in this pack: `deep-research`, `web-scrape`.

## Install

Install the start plugin `aios` first.

Claude Code: type `/aios install shelf-deep-research` (it runs `aios-guide --harness claude install shelf-deep-research`), then `/reload-plugins`.
Or install it directly:
```
/plugin install shelf-deep-research@navaigate-aios
```

Codex and Cursor, from your checkout of this repository:
```
./install.sh shelf-deep-research
./install.sh shelf-deep-research --check
```

## Keys

Exa (`EXA_API_KEY`) and Firecrawl (`FIRECRAWL_API_KEY`). Supadata (`SUPADATA_API_KEY`, paid) only if you want video evidence. Academic papers and Substack need no key. Reddit needs none, but Reddit blocks some networks (a 403): the skill reports it and carries on.

Put keys in `~/.claude/.env`, one `NAME=value` per line, and run `chmod 600 ~/.claude/.env`. Never paste a key into a chat.
The optional settings this pack declares are stored in your system keychain; the skill's own scripts read `~/.claude/.env`
or your shell, so the `.env` file is the one that always works.

This pack carries a copy of the `web-scrape` skill because the deep-research method runs on its helper.
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
Bakery); swap in your own. `/aios learn 12 deep-research` walks the steps in `TOUR.md` with you.

## Licence

MIT.
