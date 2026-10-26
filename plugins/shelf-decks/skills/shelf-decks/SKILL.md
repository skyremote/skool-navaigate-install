---
name: shelf-decks
description: Build a presentation in the member's own brand from one deck spec, HTML first (an animated reveal.js deck reviewed slide by slide), then a matching editable PowerPoint and a PDF. Use for "make me a deck", "slides for my investors/client", "turn this into a presentation", "export it to PowerPoint or PDF", or /shelf-decks.
---

# Shelf: decks

One deck spec (`deck.js`) renders two matching outputs: an animated reveal.js HTML deck that you review, and an
editable PPTX. The PDF comes from the HTML. The member's brand (colours, fonts, logo, label, image style) lives
in one `brand.json`. Never write slides by hand in HTML or PowerPoint; write the spec and render it.

## Find the command

- Claude Code: `"${CLAUDE_PLUGIN_ROOT}/bin/shelf-decks"`.
- Codex or Cursor: `shelf-decks` on PATH, or resolve this SKILL.md symlink; the command is `../../bin/shelf-decks`.

First time on a machine: `shelf-decks check`. If it lists missing Node packages, run `shelf-decks setup` (installs
pptxgenjs, puppeteer-core and pdf-lib; no browser download). It needs Node 18+ and a Chrome, Edge, Brave or
Chromium for screenshots and the PDF. If the session cannot run commands, give the member the commands in order.

## The method (HTML first)

1. **Brand.** `shelf-decks brand` shows the saved brand and a contrast check. No brand yet: ask for their real
   colours, fonts, logo and company label, never invent them, then
   `shelf-decks init --name "Acme Studio" --accent C2410C --ink 1C1917 --bg FAF7F2 --display "Fraunces" --body "Inter" --logo ~/Brand/logo.png --image-style "..."`.
   Fix every `LOW` contrast line before building.
2. **Story.** Agree the slide titles first, one point per slide, as a list. The titles alone should tell the story.
   Lead with the payoff, close on one action.
3. **Spec.** `shelf-decks new <folder>` copies the sample spec in the member's brand. Pick a builder per slide
   from the map below, then write `deck.js`. Each slide is `{ type, ...opts, talk }`.
4. **Render.** `shelf-decks render <folder>/deck.js` writes `<name>_vN.html` and `<name>_vN.pptx` (a new N
   every time; nothing is overwritten).
5. **Review every slide.** `shelf-decks shots <name>_vN.html` writes one 1920x1080 PNG per slide and a
   contact sheet. Open and look at **every** slide image at full size, then the contact sheet as a sequence. Check
   the gate below. Fix the spec and render again until it passes. Show the member the HTML (arrow keys,
   `T` talk track, `S` speaker view) before any export.
6. **Send.** The PPTX is already there. `shelf-decks pdf <name>_vN.html` makes the PDF. Send the PDF outside the
   team: fonts must exist on the opening machine, and the PDF carries them.

`shelf-decks sample <folder>` copies the fictional Northwind Bakery deck (10 slides, its own brand.json) for
practice.

## The spec

```js
module.exports = {
  profile: "member",          // brand.json (beside the spec, or the member's saved one); "editorial-light" = neutral
  name: "Q3_Review",          // output base name -> Q3_Review_v1.html / .pptx
  title: "Q3 review",         // browser tab
  imagesDir: "images",        // images beside the spec
  profileOverrides: { accent: "1F6F5C" },   // optional one-deck tweak, bare hex
  slides: [ { type: "cover", ..., talk: "stage direction\n\n\"what you say out loud\"" } ],
};
```

- Colours in titles are semantic: `titleParts: [{ text: "From " }, { text: "£1.2m", c: "accent" }]`, with
  `c` one of `accent`, `accentD`, `ink`, `coral`, `white`. Put `\n` in a part for a line break.
- Images: `image: "cover"` finds `images/cover.png`; `image: "shop.jpg"` keeps the extension.
- `talk` becomes the speaker note in both outputs and the on-screen talk-track drawer in the HTML.

## Builder catalogue

Full options for each builder: [references/builders.md](references/builders.md).

| Builder | The idea it carries |
|---|---|
| `cover` | Open on the result. Title, tagline, promise, image right. |
| `divider` | Section break, or name the enemy. Full-bleed image, big white title. |
| `statement` | One conviction, said plainly. Two big lines (`dark: true` for a rhythm break). |
| `bigStats` | Three or four hero numbers as proof. |
| `timelineAlt` | A journey or plan over time; the last node is highlighted. |
| `split` | Define a concept or show a place. Text left, image right, pills. |
| `outcomeBars` | Before and after: two outcomes with bars. |
| `darkGrid` | Four punchy points or a model, as a 2x2. |
| `cards` | Three to six parallel items or steps. The workhorse: use sparingly. |
| `calculator` | A price or budget: foundation, line items, total. |
| `modules` | An ecosystem on a foundation. |
| `compare` | Two options, two roles, risk and answer, side by side. |
| `diagram` | A live animated flow, loop, relationship, matrix or checklist. |
| `hero` | Full-bleed image with the title over a soft scrim. |
| `art` | A full-bleed picture, no text. |
| `close` | Land on one action, with a call-to-action button. |

### Content to builder

- A metric or proof point: `bigStats` (several) or `outcomeBars` (before and after).
- A story over time, a plan, a path: `timelineAlt`.
- A definition ("X is really Y") or a place: `split` or `statement`.
- A price, a budget, a package: `calculator`.
- An ecosystem, a platform, "everything rests on this": `modules`.
- A contrast, two routes, risk and answer: `compare` (calm) or `darkGrid` (punchy).
- A process: `cards` (numbered) or `diagram` with `diagram: "flow"`.
- A hard truth or a turn in the argument: `statement` or `divider`.

### De-samey rules (enforce them)

1. No more than two `cards` slides in a row, and three at most in the whole deck.
2. Use at least six distinct builders in a 10 to 14 slide deck.
3. Vary the rhythm: alternate dense slides (`cards`, `calculator`, `compare`) with open ones (`statement`,
   `divider`, `split`). Never three dense slides back to back.
4. One image world: every image follows the brand's `imageStyle` (see `shelf-decks brand`). Prompt every
   generated image with it, and keep text out of images.
5. Lead with the payoff (`cover`), close on the action (`close`).

### Diagrams

`{ type: "diagram", diagram: "flow", kicker, title, footer, image: "flow", data: { stages: [{ label, note }] } }`.
Kinds: `flow` (stages), `loop` (nodes on a cycle), `relationship` (hub and nodes), `matrix` (rows of cells),
`checklist` (rows with evidence). The HTML draws them live and animated, with notes on hover. The PPTX needs a
picture: if `images/<image>.png` does not exist, `render` bakes the live diagram to `images/<image>.baked.png` in
headless Chrome and uses that. Without Chrome the PPTX slide is blank and render warns you.

## House rules

- **One point per slide.** One clear point, with the visual it needs. Not a heading on an empty frame.
- **Look at every slide at presentation size.** The contact sheet is for the sequence; the full-size PNG is for
  the slide. A passing render proves nothing about how it looks.
- **Fix crowding by cutting words or splitting the slide, never by shrinking the type.**
- **Every chart and every number states its source on the slide** (the `footer` line), for example
  "Source: till data, Oct 2025 to Sep 2026".
- **Numbers are evidence only.** Label estimates as estimates. Scenarios say "Scenarios, not forecasts".
  Unknowns are labelled, never guessed. Never invent a figure; ask the member for it, or leave a marked gap.
- **Fictional examples are visibly fictional** wherever an audience could take them as fact.
- **Never overwrite.** Every render is a new `_vN`; `pdf` refuses to replace a file.
- **Fonts must exist on the opening machine.** The HTML and PDF use the web fonts; the PPTX needs the fonts
  installed. Send the PDF outside the team.
- British English, no emojis, short declarative titles. No placeholder text ships.

## Visual acceptance gate

Before any export, for the sequence and then each slide:

- Can a viewer get the slide's point without the speaker? If it is a title plus empty space, add the evidence,
  comparison, diagram or example, or make it a deliberate pause.
- Does any text crowd, clip, overlap the footer, or run into the corner mark or the image?
- Do neighbouring slides vary in composition and density? Repeated card slides mean the story is not built yet.
- Are logos and images real and appropriate, and does generated imagery illustrate rather than pretend to
  document?
- Are evidence, illustration, fiction and forecast distinguishable where the audience meets them?
- Is every number sourced on the slide?

Then open the PPTX once (PowerPoint, Keynote or LibreOffice) and spot-check the cover, a dense slide and the
close: fonts and image crops can differ from the HTML. Report exactly what you checked.

## Keynote mode

For a stage talk, keynote or TED-style talk, read [references/keynote-mode.md](references/keynote-mode.md) before
choosing builders. The spoken story sets the slide count, density and pacing.

## Common problems

| Problem | Fix |
|---|---|
| `Missing Node packages` | `shelf-decks setup`, then `shelf-decks check`. |
| `No Chrome or Chromium found` | Install Google Chrome, or `npx playwright install chromium`, or set `CHROME_PATH`. |
| `profile "member" needs a brand.json` | `shelf-decks init ...`, or use `profile: "editorial-light"`. |
| A diagram slide is blank in the PPTX | Chrome was missing at render time: install it and render again, or add `images/<image>.png`. |
| The PPTX shows a different font | The brand font is not installed on that machine. Install it, or send the PDF. |
| Text does not fit | Cut words or split the slide. Do not shrink the type. |
| An image is missing in the HTML | The file must sit in `images/` beside the spec; check the name and extension. |
