# Tour: module 12, the shelf: decks

`/aios learn 12 decks` follows these steps in the member's own folder, one at a time.
Run each command for the member, or have them type it. Show the real output, then check it before the next step.
Never overwrite a deck. If a check fails, stop, fix that one thing, and check again.

## Step 1: Find the command
- **Do:** check that the pack's command runs.
- **Command:** `shelf-decks --version` (Claude Code: `"${CLAUDE_PLUGIN_ROOT}/bin/shelf-decks" --version`).
- **They should see:** `shelf-decks 2.0.1`.
- **Check:** exit code 0. If the command is missing, run `export PATH="$HOME/.local/bin:$PATH"` (Codex and Cursor),
  or `/aios install shelf-decks` then `/reload-plugins` (Claude Code). If Node is missing or older than 18,
  install it from https://nodejs.org/.

## Step 2: Install the tools
- **Do:** install the three Node packages once, then check.
- **Command:** `shelf-decks setup && shelf-decks check`
- **They should see:** `ok` for node, pptxgenjs, puppeteer-core, pdf-lib and a browser, then `Ready.`
- **Check:** for a `MISSING` browser, install Google Chrome (or `npx playwright install chromium`), then check again.

## Step 3: Practise on the sample
- **Do:** copy the fictional Northwind Bakery deck, which carries its own brand.json and logo.
- **Command:** `shelf-decks sample ~/Decks/northwind`
- **They should see:** `Sample deck: .../northwind/deck.js (fictional Northwind Bakery, with its own brand.json)`.
- **Check:** `ls ~/Decks/northwind` shows `deck.js`, `brand.json`, `logo.png` and `images/`.

## Step 4: Render it, HTML first
- **Do:** render the HTML and the PPTX, then open the HTML.
- **Command:** `shelf-decks render ~/Decks/northwind/deck.js`
- **They should see:** `Profile: member`, then `HTML: .../Northwind_Second_Shop_v1.html (10 slides ...)` and
  `PPTX: .../Northwind_Second_Shop_v1.pptx`.
- **Check:** they open the HTML in a browser: arrow keys move, `T` shows the talk track, the flow diagram animates.

## Step 5: Review every slide
- **Do:** screenshot every slide and look at each one.
- **Command:** `shelf-decks shots ~/Decks/northwind/Northwind_Second_Shop_v1.html`
- **They should see:** `Slides: .../slide-01.png ... slide-10.png` and a contact sheet.
- **Check:** open the contact sheet, then each slide at full size. Name one thing to improve on one slide (for
  example cut a sentence), change `deck.js`, render again, and see `_v2` appear while `_v1` stays.

## Step 6: The PowerPoint and the PDF
- **Do:** open the PPTX, then make the PDF.
- **Command:** `shelf-decks pdf ~/Decks/northwind/Northwind_Second_Shop_v2.html`
- **They should see:** `PDF: .../Northwind_Second_Shop_v2.pdf (10 pages ...)`.
- **Check:** in PowerPoint or Keynote they click into a title and type: it is real text. The PDF matches the HTML.

## Step 7: Set their brand
- **Do:** ask for their real company name, colours, fonts, logo and the look of their images. Never invent them.
- **Command:** `shelf-decks init --name "Their Company" --accent <hex> --ink <hex> --bg <hex> --display "<font>" --body "<font>" --logo <path> --image-style "<one sentence>"`
- **They should see:** `Wrote .../brand.json`, then their brand and a contrast line per colour pair.
- **Check:** every line says `ok`. For a `LOW` line, darken the text colour or lighten the ground and run init again.

## Step 8: Their own deck
- **Do:** agree the slide titles first, one point per slide. Then start the deck and pick a builder per slide
  (`shelf-decks builders` lists them).
- **Command:** `shelf-decks new ~/Decks/<name>`, edit `deck.js`, then `shelf-decks render ~/Decks/<name>/deck.js`
- **They should see:** `Profile: member (<their brand.json>)` and the two files.
- **Check:** six or more builders, no more than three `cards`, every number with its source in the slide footer.

## Step 9: Review, then send
- **Do:** shots, fix, render again until every slide passes the gate in the skill; then the PDF.
- **Command:** `shelf-decks shots <html>` ... `shelf-decks pdf <html>`
- **They should see:** a clean contact sheet, then the PDF.
- **Check:** crowding is fixed by cutting words or splitting slides, never by smaller type. They send the PDF
  outside their team.

## Recap
Setup once, brand once, agree the titles, write the spec, render, look at every slide, fix, render again (a new
`_vN`), then the PPTX and the PDF.
