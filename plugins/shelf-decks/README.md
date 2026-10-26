# shelf-decks (AIOS 2.0, module 12: the shelf)

Decks in your own brand. You (or Claude) write one deck spec, and it renders two matching outputs: an animated
reveal.js HTML deck that you review slide by slide, and an editable PowerPoint. The PDF comes from the HTML.

- **HTML first.** Review the real deck in a browser: arrow keys to move, `T` for the talk track, `S` for the
  speaker view. `shelf-decks shots` screenshots every slide at 1920x1080 plus a contact sheet.
- **Your brand.** Colours, fonts (with web fonts for the HTML), logo, footer label and image style live in one
  `brand.json`. No house brand is included; the neutral default is `editorial-light`.
- **Sixteen builders, chosen on purpose.** Cover, statement, big numbers, timeline, split, before-and-after bars,
  calculator, compare, live diagrams and more, with rules that stop a deck going samey.
- **Editable PowerPoint.** Every word is real text. Live diagrams are baked to a picture for the PPTX.
- **Never overwrites.** Every render is a new `_vN`.

## Install

Install the start plugin `aios` first. You need Node 18 or newer (https://nodejs.org/) and Google Chrome (or
Edge, Brave or Chromium) for screenshots and the PDF.

Claude Code: type `/aios install shelf-decks`, then `/reload-plugins`. Or directly:
```
/plugin install shelf-decks@navaigate-aios
```

Codex and Cursor, from your checkout of this repository:
```
./install.sh shelf-decks
./install.sh shelf-decks --check
```

Then, once:
```
shelf-decks setup     # installs pptxgenjs, puppeteer-core and pdf-lib (no browser download)
shelf-decks check
```
In Claude Code the command is `"${CLAUDE_PLUGIN_ROOT}/bin/shelf-decks"` if `shelf-decks` is not on your PATH.

## Use

```
shelf-decks init --name "Acme Studio" --accent C2410C --ink 1C1917 --bg FAF7F2 \
  --display "Fraunces" --body "Inter" --logo ~/Brand/acme-logo.png \
  --image-style "warm documentary photography, no text in the image"
shelf-decks new ~/Decks/q3-review              # a starting spec in your brand
shelf-decks render ~/Decks/q3-review/deck.js    # q3-review_v1.html + q3-review_v1.pptx
shelf-decks shots ~/Decks/q3-review/q3-review_v1.html
shelf-decks pdf ~/Decks/q3-review/q3-review_v1.html
```

Practise first on the fictional Northwind Bakery deck (10 slides, its own brand):
```
shelf-decks sample ~/Decks/northwind
shelf-decks render ~/Decks/northwind/deck.js --pdf
```

Prompts to paste into Claude: [prompts.md](prompts.md). The method, the builders and the house rules:
[skills/shelf-decks/SKILL.md](skills/shelf-decks/SKILL.md). Every builder option:
[skills/shelf-decks/references/builders.md](skills/shelf-decks/references/builders.md).

## Fonts

The HTML and the PDF load your web fonts, so they look right anywhere. The PowerPoint uses the font names in
`brand.json` and shows them only where those fonts are installed. Set `fonts.displayPptx` and `fonts.bodyPptx`
to installed fonts if your web fonts are not on the machines that open the file, and send the PDF outside your
team.

## Licence

MIT. The vendored reveal.js 5.1.0 runtime in `reveal-runtime/` is MIT (Hakim El Hattab), see
`reveal-runtime/LICENSE`. Installed by `shelf-decks setup`: pptxgenjs (MIT), puppeteer-core (Apache-2.0),
pdf-lib (MIT). The Northwind Bakery sample, its logo and its illustrations are fictional and made for this pack.
