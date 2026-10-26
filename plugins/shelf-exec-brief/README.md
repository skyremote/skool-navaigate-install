# shelf-exec-brief (AIOS 2.0, module 12: the shelf)

Get a three-to-four page A4 decision brief as a single HTML file that prints cleanly to PDF, with only figures you can point at.

This pack wraps the real `exec-brief` skill from the first-generation course. The skill is a byte-for-byte copy and is not
rewritten. What 2.0 adds is a one-command install, a tour, tested prompts and a check that the copy has not drifted.

Skills in this pack: `exec-brief`.

## Install

Install the start plugin `aios` first.

Claude Code: type `/aios install shelf-exec-brief` (it runs `aios-guide --harness claude install shelf-exec-brief`), then `/reload-plugins`.
Or install it directly:
```
/plugin install shelf-exec-brief@navaigate-aios
```

Codex and Cursor, from your checkout of this repository:
```
./install.sh shelf-exec-brief
./install.sh shelf-exec-brief --check
```

## Keys

None.

This pack needs no key.

The brief is one self-contained HTML file. Open it in a browser and print to PDF. It never uses a chart library.

## Use

Open `prompts.md` and paste one of the prompts into Claude. The prompts use fictional data (Acme Studio, Northwind
Bakery); swap in your own. `/aios learn 12 exec-brief` walks the steps in `TOUR.md` with you.

## Licence

MIT.
