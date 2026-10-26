# Tour: module 12, the shelf: decks

`/aios learn 12 decks` follows these steps in the member's own folder, one at a time.
Run each command for the member, or have them type it. Show the real output, then check it before the next step.
Never overwrite a deck. If a check fails, stop, fix that one thing, and check again.

## Step 1: Find the command
- **Do:** check that the pack's command runs.
- **Command:** `shelf-decks --version` (Claude Code: `"${CLAUDE_PLUGIN_ROOT}/bin/shelf-decks" --version`).
- **They should see:** `shelf-decks 2.0.0`.
- **Check:** exit code 0. If the command is missing, run `export PATH="$HOME/.local/bin:$PATH"` (Codex and Cursor),
  or restart Claude Code after `/plugin install shelf-decks@navaigate-aios`.

## Step 2: Check the tools
- **Do:** confirm python-pptx, Pillow and Playwright with Chromium.
- **Command:** `python3 -c "import pptx, PIL, playwright; print('ok')" && python3 -m playwright install chromium`
- **They should see:** `ok`, then Chromium already installed or downloading.
- **Check:** if the import fails, run `python3 -m pip install --user python-pptx Pillow playwright`, then again.

## Step 3: Practise on the sample
- **Do:** make the fictional Acme Studio deck, which carries its own brand file and logo.
- **Command:** `shelf-decks sample ~/Decks/acme-sample`
- **They should see:** `Sample deck: .../acme-sample/deck.md`.
- **Check:** `cat ~/Decks/acme-sample/deck.md` shows slides separated by `---`, each starting with a `[layout]`.

## Step 4: Build, review, export the sample
- **Do:** run the full path once.
- **Command:** `shelf-decks build ~/Decks/acme-sample && shelf-decks review ~/Decks/acme-sample && shelf-decks export ~/Decks/acme-sample --pdf`
- **They should see:** `Built .../deck_v1.html`, `PASS: review of deck_v1.html`, `Exported .../deck_v1.pptx`.
- **Check:** they open `out/review_v1/montage.png`, then the PPTX in PowerPoint or Keynote, and click into a title
  to see it is editable text.

## Step 5: Set their brand
- **Do:** ask for their real colours, fonts and logo. Never invent them.
- **Command:** `shelf-decks brand set name="Their Company"`, then `colours.accent=#hex`, `colours.text=#hex`,
  `fonts.heading=<font name>`, `fonts.body=<font name>`, `logo=<path to PNG>`
- **They should see:** the brand printed after each change.
- **Check:** `shelf-decks brand check` lists every pair as `ok`. If one says TOO LOW, change that colour.

## Step 6: Plan their deck
- **Do:** agree one point per slide, as a list of titles, before writing any slide.
- **Command:** `shelf-decks new ~/Decks/<name> --title "<their title>"`
- **They should see:** `Started .../deck.md`.
- **Check:** the titles read as a story on their own. Any number has a source they can name.

## Step 7: Write the slides
- **Do:** fill `deck.md` with the layouts in the guide (`[bullets]`, `[stat]`, `[bars]`, `[two-column]`, `[quote]`,
  `[image]`, `[section]`, `[closing]`). Put what they will say under `notes:`.
- **Command:** `shelf-decks build ~/Decks/<name>`
- **They should see:** `Built .../deck_v1.html (N slides, brand: Their Company)`.
- **Check:** they open the HTML. Arrow keys move, N shows the notes.

## Step 8: Review
- **Do:** render and check every slide.
- **Command:** `shelf-decks review ~/Decks/<name>`
- **They should see:** `PASS`, or problems such as "the body text does not fit".
- **Check:** for each problem, cut words or split the slide, then build and review again. Never shrink the type.
  Then look at `montage.png` together for repeated layouts and crowding.

## Step 9: Export and verify
- **Do:** write the PowerPoint and the PDF, then read it back.
- **Command:** `shelf-decks export ~/Decks/<name> --pdf && shelf-decks verify ~/Decks/<name>`
- **They should see:** `Exported`, then `PASS: deck_v1.pptx, N slides, ... fonts: <their fonts>`.
- **Check:** only their brand fonts are listed. If they send the file outside, they send the PDF too.

## Recap
Brand once, plan the titles, write `deck.md`, build, review until PASS, export, verify. Each build is a new `_vN`.
