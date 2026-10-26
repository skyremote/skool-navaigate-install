# shelf-hormozi (AIOS 2.0, module 12: the shelf)

Build and pressure-test your offer with the Grand Slam, Offer Enhancer, Lead Engine, Money Model and Ask Hormozi skills, with every claim cited to a book, chapter and page.

This pack wraps the real `hormozi` skill from the first-generation course. The skill is a byte-for-byte copy and is not
rewritten. What 2.0 adds is a one-command install, a tour, tested prompts and a check that the copy has not drifted.

Skills in this pack: `hormozi`.

## Install

Install the start plugin `aios` first.

Claude Code: type `/aios install shelf-hormozi` (it runs `aios-guide --harness claude install shelf-hormozi`), then `/reload-plugins`.
Or install it directly:
```
/plugin install shelf-hormozi@navaigate-aios
```

Codex and Cursor, from your checkout of this repository:
```
./install.sh shelf-hormozi
./install.sh shelf-hormozi --check
```

## Keys

None. You need your own copies of the three books for the cited answers.

Put keys in `~/.claude/.env`, one `NAME=value` per line, and run `chmod 600 ~/.claude/.env`. Never paste a key into a chat.
The optional settings this pack declares are stored in your system keychain; the skill's own scripts read `~/.claude/.env`
or your shell, so the `.env` file is the one that always works.

This pack is the front door. The cited answers need the Hormozi skills built from **your own** copies of the books,
which you get from the Inner Circle gold lesson. Nothing in this pack contains the books, and it never will.
Without them it tells you what to install and does not guess.

## Use

Open `prompts.md` and paste one of the prompts into Claude. The prompts use fictional data (Acme Studio, Northwind
Bakery); swap in your own. `/aios learn 12 hormozi` walks the steps in `TOUR.md` with you.

## Licence

MIT.
