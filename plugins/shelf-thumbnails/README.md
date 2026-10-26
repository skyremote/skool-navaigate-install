# shelf-thumbnails (AIOS 2.0, module 12: the shelf)

Get four thumbnail concepts side by side from your own photos in your own look, pick one, and get the headline added afterwards as a text layer, never spelled by the image model.

This pack wraps the real `thumbnails` skill from the first-generation course. The skill is a byte-for-byte copy and is not
rewritten. What 2.0 adds is a one-command install, a tour, tested prompts and a check that the copy has not drifted.

Skills in this pack: `thumbnails`.

## Install

Install the start plugin `aios` first.

Claude Code: type `/aios install shelf-thumbnails` (it runs `aios-guide --harness claude install shelf-thumbnails`), then `/reload-plugins`.
Or install it directly:
```
/plugin install shelf-thumbnails@navaigate-aios
```

Codex and Cursor, from your checkout of this repository:
```
./install.sh shelf-thumbnails
./install.sh shelf-thumbnails --check
```

## Keys

Gemini (`GEMINI_API_KEY`) for the images. A small catalogue of your own photos.

Put keys in `~/.claude/.env`, one `NAME=value` per line, and run `chmod 600 ~/.claude/.env`. Never paste a key into a chat.
The optional settings this pack declares are stored in your system keychain; the skill's own scripts read `~/.claude/.env`
or your shell, so the `.env` file is the one that always works.

You need your own photos, tagged by expression and pose (the skill stops and helps you build that first).
The skill does not ship anyone else's face.

## Use

Open `prompts.md` and paste one of the prompts into Claude. The prompts use fictional data (Acme Studio, Northwind
Bakery); swap in your own. `/aios learn 12 thumbnails` walks the steps in `TOUR.md` with you.

## Licence

MIT.
