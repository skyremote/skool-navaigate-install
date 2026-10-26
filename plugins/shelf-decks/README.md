# shelf-decks (AIOS 2.0, module 12: the shelf)

Build a presentation in your own brand. You write one Markdown file, the pack turns it into an HTML deck,
reviews every slide in a real browser, and then exports an editable PowerPoint and a PDF that match it.

- **Your brand.** Colours, fonts, logo and footer live in one settings file. No house brand is included.
- **HTML first.** A browser shows exactly what each slide looks like and measures whether the text fits.
- **Editable PowerPoint.** Every word is real text in your fonts, not a picture of a slide.
- **Checked.** Export refuses until review passes. Verify reads the PowerPoint back against your deck.

## Install

Install the start plugin `aios` first.

Claude Code:
```
/plugin marketplace add skyremote/skool-navaigate-install
/plugin install shelf-decks@navaigate-aios
```

Codex and Cursor, from your checkout of this repository:
```
./install.sh aios
./install.sh shelf-decks
```

Then the tools, once:
```
python3 -m pip install --user python-pptx Pillow playwright
python3 -m playwright install chromium
```

## Use

```
shelf-decks brand set name="Acme Studio"
shelf-decks brand set colours.accent=#C2410C
shelf-decks brand set logo=~/Brand/acme-logo.png
shelf-decks new ~/Decks/q3-review --title "Q3 client review"
shelf-decks build ~/Decks/q3-review
shelf-decks review ~/Decks/q3-review
shelf-decks export ~/Decks/q3-review --pdf
shelf-decks verify ~/Decks/q3-review
```

`shelf-decks sample ~/Decks/acme-sample` makes a ten-slide practice deck for the fictional Acme Studio.

The deck format, every layout, the brand keys and the fixes: [skills/shelf-decks/references/deck-format.md](skills/shelf-decks/references/deck-format.md).

## Licence

MIT. Dependencies are installed by you: python-pptx (MIT), Pillow (MIT-CMU), Playwright (Apache-2.0).
