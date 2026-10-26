# Module 12 · The shelf: decks: prompts

Paste one prompt at a time into a new Claude chat in bb, opened on your AIOS folder. Run them in order. If a prompt has lines marked "edit", change them to your own details first. Each prompt sets something up, checks it, and shows you the result.

These prompts are instructions to Claude. They also work in Claude Code in a terminal, opened in the same folder.

## Prompt 12d.1 · Show me the shelf, then practise on the sample deck

**What it does:** Shows the shelf packs, sets up the decks pack, and renders the fictional Northwind Bakery sample deck: HTML first, a screenshot of every slide, then the PowerPoint and the PDF.

**How you know it worked:** The report shows the contact sheet of every slide, and the HTML, PPTX and PDF paths.

~~~text
Show me the shelf and recommend the one tool I should install first for my business, in two lines. Then set up the decks pack and practise on the sample deck.

Step 0, get the pack. These commands change Claude's own plugin folder in my home folder, outside this folder. I allow that for these commands only: if the sandbox blocks them, run them outside the sandbox. Run `claude plugin marketplace list`. If `navaigate-aios` is not listed, run `claude plugin marketplace add skyremote/skool-navaigate-install`. Then run `claude plugin install shelf-decks@navaigate-aios` ("already installed" is fine; it also brings the start pack `aios`). Until I restart Claude, call the pack's command by its full path: `"$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/navaigate-aios/shelf-decks/*/bin | tail -1)/shelf-decks"`. Below, `shelf-decks` means that full path.

1. Run `"$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/navaigate-aios/aios/*/bin | tail -1)/aios-guide" list` and show the shelf packs (module 12) with one line each. Recommend one in two lines.
2. Check the command: `shelf-decks --version` should print `shelf-decks 2.0.1` or later. If Node is missing or older than 18, tell me to install it from nodejs.org, and stop.
3. Install the tools once and check them: `shelf-decks setup && shelf-decks check`. It should end with `Ready.` If the browser is MISSING, tell me to install Google Chrome, and stop.
4. Copy the fictional sample into this folder: `shelf-decks sample 40_content/decks/northwind`. Show what is in the folder.
5. Render it, HTML first: `shelf-decks render 40_content/decks/northwind/deck.js`. Show the HTML and PPTX paths it prints.
6. Screenshot every slide: `shelf-decks shots <the HTML path>`. Look at the contact sheet, and name one thing on one slide you would improve.
7. Make the PDF: `shelf-decks pdf <the HTML path>`.
8. In the report, show the contact sheet image by copying it next to the report and using a relative image link.

For this task only: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. If a step below must write outside this folder (for example to Claude's settings, `~/.local` or a folder the step names), I allow exactly that command: if the sandbox blocks it, run it outside the sandbox. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m12-decks-sample_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m12-decks-sample_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~

## Prompt 12d.2 · Make a short deck in my brand, check every slide, then export it

**What it does:** Sets your brand once (name, colours, fonts) with a readability check, agrees five slide titles as a story, builds the deck, screenshots every slide and fixes what is crowded, then makes the PowerPoint and the PDF.

**How you know it worked:** Every colour pair in the brand check says ok, the contact sheet shows five clean slides, and the PPTX and PDF exist.

~~~text
My brand and my deck (edit these lines before you send):
- Company: Acme Studio
- Accent colour: #C2410C. Text colour: #1C1917. Background: #FAF7F2.
- Heading font: Georgia. Body font: Arial.
- How my images should look: warm documentary photography, no text in the image.
- Deck title: How we work with new clients
- The five points, one per slide: who we are; the three things we make; how a project runs, in four steps; what it costs to start; how to book a first call.

Make this deck with the shelf decks pack. If the pack is not set up yet, run prompt 12d.1 first.

Step 0, get the pack. These commands change Claude's own plugin folder in my home folder, outside this folder. I allow that for these commands only: if the sandbox blocks them, run them outside the sandbox. Run `claude plugin marketplace list`. If `navaigate-aios` is not listed, run `claude plugin marketplace add skyremote/skool-navaigate-install`. Then run `claude plugin install shelf-decks@navaigate-aios` ("already installed" is fine; it also brings the start pack `aios`). Until I restart Claude, call the pack's command by its full path: `"$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/navaigate-aios/shelf-decks/*/bin | tail -1)/shelf-decks"`. Below, `shelf-decks` means that full path.

1. Set my brand: `shelf-decks init --name "<Company>" --accent <hex> --ink <text hex> --bg <background hex> --display "<heading font>" --body "<body font>" --image-style "<how my images look>"`. Do not invent a logo: leave it out if I gave none.
2. Read the contrast lines it prints. Every line must say ok. If one says LOW, tell me which colour to change and stop.
3. Start the deck: `shelf-decks new 40_content/decks/new-clients`. Run `shelf-decks builders` to see the slide layouts.
4. Write `deck.js`: one slide per point above, in that order, with the deck title on the first. Use different builders so neighbouring slides do not look the same. Do not invent numbers: if a slide needs one, write "[your price]".
5. Render it: `shelf-decks render 40_content/decks/new-clients/deck.js`, then screenshot every slide: `shelf-decks shots <the HTML path>`.
6. Look at every slide at full size. If something is crowded, cut words or split the slide, never make the text smaller, then render and shoot again (a new `_v2` appears, `_v1` stays).
7. When every slide is clean, make the PDF: `shelf-decks pdf <the latest HTML path>`.
8. In the report, show the contact sheet image by copying it next to the report and using a relative image link.

For this task only: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. If a step below must write outside this folder (for example to Claude's settings, `~/.local` or a folder the step names), I allow exactly that command: if the sandbox blocks it, run it outside the sandbox. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m12-decks-own_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m12-decks-own_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~
