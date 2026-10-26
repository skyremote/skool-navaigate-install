# Module 12 · The shelf: decks: prompts

Paste one prompt at a time into a new Claude chat in bb, opened on your AIOS folder. Run them in order. If a prompt has lines marked "edit", change them to your own details first. Each prompt sets something up, checks it, and shows you the result.

These prompts are instructions to Claude. They also work in Claude Code in a terminal, opened in the same folder.

## Prompt 12d.1 · Practise on the sample deck

**What it does:** Checks the tools, then builds, reviews and exports the fictional Acme Studio sample deck as HTML, an editable PowerPoint and a PDF.

**How you know it worked:** The review says PASS, the export writes `deck_v1.pptx`, and the report shows the slide montage.

~~~text
Set up the decks pack from the shelf and practise on the sample deck.

Step 0, get the pack. Run `claude plugin marketplace list`. If `navaigate-aios` is not listed, run `claude plugin marketplace add skyremote/skool-navaigate-install`. Then run `claude plugin install shelf-decks@navaigate-aios` ("already installed" is fine; it also brings the start pack `aios`). Until I restart Claude, call the pack's command by its full path: `"$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/navaigate-aios/shelf-decks/*/bin | tail -1)/shelf-decks"`. Below, `shelf-decks` means that full path.

1. Check the tools: `python3 -c "import pptx, PIL, playwright; print('ok')"`. If it fails, run `python3 -m pip install --user python-pptx Pillow playwright` and check again. Then run `python3 -m playwright install chromium`.
2. Make the sample in this folder: `shelf-decks sample 40_content/decks/acme-sample`. Show the first slides of its `deck.md`.
3. Build, review and export: `shelf-decks build 40_content/decks/acme-sample && shelf-decks review 40_content/decks/acme-sample && shelf-decks export 40_content/decks/acme-sample --pdf`.
4. Run `shelf-decks verify 40_content/decks/acme-sample` and show the result.
5. In the report, show the review montage image (`out/review_v1/montage.png`) by copying it next to the report and using a relative image link.

Ground rules: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m12-decks-sample_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m12-decks-sample_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~

## Prompt 12d.2 · Make a short deck in your brand

**What it does:** Sets your brand once (name, colours, fonts), plans five slides as a story, builds them, reviews every slide and exports a PowerPoint and a PDF.

**How you know it worked:** `shelf-decks brand check` shows every colour pair as ok, the review says PASS and `shelf-decks verify` lists only your brand fonts.

~~~text
My brand and my deck (edit these lines before you send):
- Company: Acme Studio
- Accent colour: #C8553D. Text colour: #1F1F1F.
- Heading font: Georgia. Body font: Arial.
- Deck title: How we work with new clients
- The five points, one per slide: who we are; the three things we make; how a project runs, in four steps; what it costs to start; how to book a first call.

Make this deck with the shelf decks pack.

Step 0, get the pack. Run `claude plugin marketplace list`. If `navaigate-aios` is not listed, run `claude plugin marketplace add skyremote/skool-navaigate-install`. Then run `claude plugin install shelf-decks@navaigate-aios` ("already installed" is fine; it also brings the start pack `aios`). Until I restart Claude, call the pack's command by its full path: `"$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/navaigate-aios/shelf-decks/*/bin | tail -1)/shelf-decks"`. Below, `shelf-decks` means that full path.

1. Set my brand: `shelf-decks brand set name="<Company>"`, then `colours.accent=<hex>`, `colours.text=<hex>`, `fonts.heading=<font>`, `fonts.body=<font>`. Do not invent a logo; skip it if I gave none.
2. Run `shelf-decks brand check`. Every pair must say ok. If one says TOO LOW, tell me which colour to change and stop.
3. Start the deck: `shelf-decks new 40_content/decks/new-clients --title "<Deck title>"`.
4. Write `deck.md`: one slide per point above, using the layouts in the pack's guide (for example `[section]`, `[bullets]`, `[two-column]`, `[closing]`). Put what I would say under `notes:`. Do not invent numbers; if a slide needs one, write "[your price]".
5. Build and review: `shelf-decks build 40_content/decks/new-clients && shelf-decks review 40_content/decks/new-clients`. For each problem, cut words or split the slide, never shrink the type, then build and review again until it says PASS.
6. Export and verify: `shelf-decks export 40_content/decks/new-clients --pdf && shelf-decks verify 40_content/decks/new-clients`.
7. In the report, show the review montage image by copying it next to the report and using a relative image link.

Ground rules: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m12-decks-own_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m12-decks-own_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~
