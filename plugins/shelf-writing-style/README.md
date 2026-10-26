# shelf-writing-style (AIOS 2.0, module 12: the shelf)

Hand it a draft and get the slop graded and rewritten out, with your names, numbers and claims untouched.

This pack wraps the real `writing-style` skill from the first-generation course. The skill is a byte-for-byte copy and is not
rewritten. What 2.0 adds is a one-command install, a tour, tested prompts and a check that the copy has not drifted.

Skills in this pack: `writing-style`.

## Install

Install the start plugin `aios` first.

Claude Code: type `/aios install shelf-writing-style` (it runs `aios-guide --harness claude install shelf-writing-style`), then `/reload-plugins`.
Or install it directly:
```
/plugin install shelf-writing-style@navaigate-aios
```

Codex and Cursor, from your checkout of this repository:
```
./install.sh shelf-writing-style
./install.sh shelf-writing-style --check
```

## Keys

None.

Put keys in `~/.claude/.env`, one `NAME=value` per line, and run `chmod 600 ~/.claude/.env`. Never paste a key into a chat.
The optional settings this pack declares are stored in your system keychain; the skill's own scripts read `~/.claude/.env`
or your shell, so the `.env` file is the one that always works.

This is the editor, not your voice. For your own rhythm on the page, build a voice skill first and run this after.

## Use

Open `prompts.md` and paste one of the prompts into Claude. The prompts use fictional data (Acme Studio, Northwind
Bakery); swap in your own. `/aios learn 12 writing-style` walks the steps in `TOUR.md` with you.

## Licence

MIT.
