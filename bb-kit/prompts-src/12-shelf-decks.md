# 12 · The shelf: decks
pack: shelf-decks
cmd: shelf-decks

## 12d.1 · Practise on the sample deck
what: Checks the tools, then builds, reviews and exports the fictional Acme Studio sample deck as HTML, an editable PowerPoint and a PDF.
check: The review says PASS, the export writes `deck_v1.pptx`, and the report shows the slide montage.
~~~
Set up the decks pack from the shelf and practise on the sample deck.

<<INSTALL>>

1. Check the tools: `python3 -c "import pptx, PIL, playwright; print('ok')"`. If it fails, run `python3 -m pip install --user python-pptx Pillow playwright` and check again. Then run `python3 -m playwright install chromium`.
2. Make the sample in this folder: `shelf-decks sample 40_content/decks/acme-sample`. Show the first slides of its `deck.md`.
3. Build, review and export: `shelf-decks build 40_content/decks/acme-sample && shelf-decks review 40_content/decks/acme-sample && shelf-decks export 40_content/decks/acme-sample --pdf`.
4. Run `shelf-decks verify 40_content/decks/acme-sample` and show the result.
5. In the report, show the review montage image (`out/review_v1/montage.png`) by copying it next to the report and using a relative image link.

<<RULES>>

<<FINISH m12-decks-sample>>
~~~

## 12d.2 · Make a short deck in your brand
what: Sets your brand once (name, colours, fonts), plans five slides as a story, builds them, reviews every slide and exports a PowerPoint and a PDF.
check: `shelf-decks brand check` shows every colour pair as ok, the review says PASS and `shelf-decks verify` lists only your brand fonts.
~~~
My brand and my deck (edit these lines before you send):
- Company: Acme Studio
- Accent colour: #C8553D. Text colour: #1F1F1F.
- Heading font: Georgia. Body font: Arial.
- Deck title: How we work with new clients
- The five points, one per slide: who we are; the three things we make; how a project runs, in four steps; what it costs to start; how to book a first call.

Make this deck with the shelf decks pack.

<<INSTALL>>

1. Set my brand: `shelf-decks brand set name="<Company>"`, then `colours.accent=<hex>`, `colours.text=<hex>`, `fonts.heading=<font>`, `fonts.body=<font>`. Do not invent a logo; skip it if I gave none.
2. Run `shelf-decks brand check`. Every pair must say ok. If one says TOO LOW, tell me which colour to change and stop.
3. Start the deck: `shelf-decks new 40_content/decks/new-clients --title "<Deck title>"`.
4. Write `deck.md`: one slide per point above, using the layouts in the pack's guide (for example `[section]`, `[bullets]`, `[two-column]`, `[closing]`). Put what I would say under `notes:`. Do not invent numbers; if a slide needs one, write "[your price]".
5. Build and review: `shelf-decks build 40_content/decks/new-clients && shelf-decks review 40_content/decks/new-clients`. For each problem, cut words or split the slide, never shrink the type, then build and review again until it says PASS.
6. Export and verify: `shelf-decks export 40_content/decks/new-clients --pdf && shelf-decks verify 40_content/decks/new-clients`.
7. In the report, show the review montage image by copying it next to the report and using a relative image link.

<<RULES>>

<<FINISH m12-decks-own>>
~~~
