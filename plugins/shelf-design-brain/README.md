# shelf-design-brain (AIOS 2.0, module 12: the shelf)

Ask design questions and get critiques of your page, deck or chart that cite the entry number and the named source (WCAG, Rams, Vignelli and the rest).

This pack wraps the real `design-brain` skill from the first-generation course. The skill is a byte-for-byte copy and is not
rewritten. What 2.0 adds is a one-command install, a tour, tested prompts and a check that the copy has not drifted.

Skills in this pack: `design-brain`.

## Install

Install the start plugin `aios` first.

Claude Code: type `/aios install shelf-design-brain` (it runs `aios-guide --harness claude install shelf-design-brain`), then `/reload-plugins`.
Or install it directly:
```
/plugin install shelf-design-brain@navaigate-aios
```

Codex and Cursor, from your checkout of this repository:
```
./install.sh shelf-design-brain
./install.sh shelf-design-brain --check
```

## Keys

None. The corpus is a free download from the Design Brain lesson (a zip).

This pack needs no key.

## The corpus is a separate download

The skill is the front door. The 1,119 entries come in a zip from the Design Brain lesson, which the skill links.
Claude Code:
```
curl -L -o ~/Downloads/design-brain_v1.zip "https://f003.backblazeb2.com/file/NavAIgate-Website/navbot-community/downloads/your-aios/design-brain_v1.zip"
unzip -o ~/Downloads/design-brain_v1.zip -d ~/.claude/skills
```
Then restart Claude Code. Codex and Cursor: their skill folder is a link into this checkout, so do not unzip into it.
Unzip to `~/design-brain` instead and tell your agent that is where the corpus is.

## Use

Open `prompts.md` and paste one of the prompts into Claude. The prompts use fictional data (Acme Studio, Northwind
Bakery); swap in your own. `/aios learn 12 design-brain` walks the steps in `TOUR.md` with you.

## Licence

MIT.
