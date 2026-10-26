# shelf-diagrams (AIOS 2.0, module 12: the shelf)

Describe how something works and get a rendered diagram, with Claude looking at the picture and fixing overlaps before it hands it over.

This pack wraps the real `diagrams` skill from the first-generation course. The skill is a byte-for-byte copy and is not
rewritten. What 2.0 adds is a one-command install, a tour, tested prompts and a check that the copy has not drifted.

Skills in this pack: `diagrams`.

## Install

Install the start plugin `aios` first.

Claude Code: type `/aios install shelf-diagrams` (it runs `aios-guide --harness claude install shelf-diagrams`), then `/reload-plugins`.
Or install it directly:
```
/plugin install shelf-diagrams@navaigate-aios
```

Codex and Cursor, from your checkout of this repository:
```
./install.sh shelf-diagrams
./install.sh shelf-diagrams --check
```

## Keys

None. D2 is free and installs from d2lang.com.

Put keys in `~/.claude/.env`, one `NAME=value` per line, and run `chmod 600 ~/.claude/.env`. Never paste a key into a chat.
The optional settings this pack declares are stored in your system keychain; the skill's own scripts read `~/.claude/.env`
or your shell, so the `.env` file is the one that always works.

D2 is a command-line tool. Install it first: `curl -fsSL https://d2lang.com/install.sh | sh -s --`
(or `brew install d2` on macOS). The skill will prove it with a one-box diagram before it draws yours.

## Use

Open `prompts.md` and paste one of the prompts into Claude. The prompts use fictional data (Acme Studio, Northwind
Bakery); swap in your own. `/aios learn 12 diagrams` walks the steps in `TOUR.md` with you.

## Licence

MIT.
