# 12 · The shelf: decks
pack: shelf-decks
cmd: shelf-decks

## 12d.1 · Show me the shelf, then practise on the sample deck
what: Shows the shelf packs, sets up the decks pack, and renders the fictional Northwind Bakery sample deck: HTML first, a screenshot of every slide, then the PowerPoint and the PDF.
check: The report shows the contact sheet of every slide, and the HTML, PPTX and PDF paths.
~~~
Show me the shelf and recommend the one tool I should install first for my business, in two lines. Then set up the decks pack and practise on the sample deck.

<<INSTALL>>

1. Run `"$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/navaigate-aios/aios/*/bin | tail -1)/aios-guide" list` and show the shelf packs (module 12) with one line each. Recommend one in two lines.
2. Check the command: `shelf-decks --version` should print `shelf-decks 2.0.1` or later. If it prints an older version, update the pack (this also changes Claude's plugin folder, and I allow it): `claude plugin marketplace update navaigate-aios`, then `claude plugin update shelf-decks@navaigate-aios`, and check again. If Node is missing or older than 18, tell me to install it from nodejs.org, and stop.
3. Install the tools once and check them: `shelf-decks setup && shelf-decks check`. It should end with `Ready.` If the browser is MISSING, tell me to install Google Chrome, and stop.
4. Copy the fictional sample into this folder: `shelf-decks sample 40_content/decks/northwind`. Show what is in the folder.
5. Render it, HTML first: `shelf-decks render 40_content/decks/northwind/deck.js`. Show the HTML and PPTX paths it prints.
6. Screenshot every slide: `shelf-decks shots <the HTML path>`. Look at the contact sheet, and name one thing on one slide you would improve.
7. Make the PDF: `shelf-decks pdf <the HTML path>`.
8. In the report, show the contact sheet image by copying it next to the report and using a relative image link.

<<RULES>>

<<FINISH m12-decks-sample>>
~~~

## 12d.2 · Make a short deck in my brand, check every slide, then export it
what: Sets your brand once (name, colours, fonts) with a readability check, agrees five slide titles as a story, builds the deck, screenshots every slide and fixes what is crowded, then makes the PowerPoint and the PDF.
check: Every colour pair in the brand check says ok, the contact sheet shows five clean slides, and the PPTX and PDF exist.
~~~
My brand and my deck (edit these lines before you send):
- Company: Acme Studio
- Accent colour: #C2410C. Text colour: #1C1917. Background: #FAF7F2.
- Heading font: Georgia. Body font: Arial.
- How my images should look: warm documentary photography, no text in the image.
- Deck title: How we work with new clients
- The five points, one per slide: who we are; the three things we make; how a project runs, in four steps; what it costs to start; how to book a first call.

Make this deck with the shelf decks pack, version 2.0.1 or later. If the pack is not set up yet, or `shelf-decks --version` is older, run prompt 12d.1 first.

<<INSTALL>>

1. Set my brand: `shelf-decks init --name "<Company>" --accent <hex> --ink <text hex> --bg <background hex> --display "<heading font>" --body "<body font>" --image-style "<how my images look>"`. Do not invent a logo: leave it out if I gave none.
2. Read the contrast lines it prints. Every line must say ok. If one says LOW, tell me which colour to change and stop.
3. Start the deck: `shelf-decks new 40_content/decks/new-clients`. Run `shelf-decks builders` to see the slide layouts.
4. Write `deck.js`: one slide per point above, in that order, with the deck title on the first. Use different builders so neighbouring slides do not look the same. Do not invent numbers: if a slide needs one, write "[your price]".
5. Render it: `shelf-decks render 40_content/decks/new-clients/deck.js`, then screenshot every slide: `shelf-decks shots <the HTML path>`.
6. Look at every slide at full size. If something is crowded, cut words or split the slide, never make the text smaller, then render and shoot again (a new `_v2` appears, `_v1` stays).
7. When every slide is clean, make the PDF: `shelf-decks pdf <the latest HTML path>`.
8. In the report, show the contact sheet image by copying it next to the report and using a relative image link.

<<RULES>>

<<FINISH m12-decks-own>>
~~~
