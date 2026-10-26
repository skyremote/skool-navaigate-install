# shelf-content-pipeline (AIOS 2.0, module 12: the shelf)

Every idea is captured, developed against your strategy and given a date, kept in a SQLite file you own and a pipeline.md you can read.

This pack wraps the real `content-pipeline` skill from the first-generation course. The skill is a byte-for-byte copy and is not
rewritten. What 2.0 adds is a one-command install, a tour, tested prompts and a check that the copy has not drifted.

Skills in this pack: `content-pipeline`.

## Install

Install the start plugin `aios` first.

Claude Code: type `/aios install shelf-content-pipeline` (it runs `aios-guide --harness claude install shelf-content-pipeline`), then `/reload-plugins`.
Or install it directly:
```
/plugin install shelf-content-pipeline@navaigate-aios
```

Codex and Cursor, from your checkout of this repository:
```
./install.sh shelf-content-pipeline
./install.sh shelf-content-pipeline --check
```

## Keys

None. Notion (`NOTION_API_TOKEN`) is optional, only for a team-visible calendar.

This pack needs no key.

Python 3.10+ with `python-dotenv` (`python3 -m pip install --user python-dotenv`; if pip answers `externally-managed-environment`, use a virtual environment as described under the other packs' install steps: `python3 -m venv ~/.venvs/aios`, then `~/.venvs/aios/bin/python -m pip install python-dotenv`, and put `~/.venvs/aios/bin` first on your PATH). Every command runs from your
project folder, where `data/content.db` and `content/` live. Nothing here publishes anything.

## Use

Open `prompts.md` and paste one of the prompts into Claude. The prompts use fictional data (Acme Studio, Northwind
Bakery); swap in your own. `/aios learn 12 content-pipeline` walks the steps in `TOUR.md` with you.

## Licence

MIT.
