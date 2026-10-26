# shelf-decks 2.0.1: integration notes for the chief of staff

2.0.1 replaces the 2.0.0 "method only" Python rebuild. It ships a port of Daniel's real deck pipeline: his shared
deck engine (one spec, an animated reveal.js HTML deck plus a matching PPTX), his headless-Chrome export, and the
house rules from his deck skills, de-branded, with the member's own brand in `brand.json`.

## Sources, owners and licences

| Source | Owner and licence | What this pack took |
|---|---|---|
| Deck engine (`~/.claude/deck-engine/engine/`: `profiles.js`, `builders-html.js`, `builders-pptx.js`, `diagrams.js`, `render.js`, `README.md`) | Daniel's own code; its package licence is ISC (permissive, compatible with the repo's MIT). Shipped in this MIT repo by its owner. | **Copied**, then edited: brand profiles removed, `member` profile added, logo support, versioned outputs, diagram bake, cross-platform image sizing. The builder catalogue, content-to-builder map and de-samey rules (engine README) went into SKILL.md. |
| Vendored reveal.js 5.1.0 (`reveal-runtime/`: `reveal.js`, `reveal.css`, `notes.js`, `reset.css`) | Hakim El Hattab, MIT (header in `reveal.js` and `reveal.css`; `notes.js` is reveal's notes plugin from the same release). `reset.css`: Eric Meyer, public domain. | **Copied unchanged**, plus `reveal-runtime/LICENSE`. |
| `html-deck-export` skill (`scripts/export-deck.mjs`) | Daniel's own code, no licence file | **Ported** into `engine/capture.js`: the Chrome finder, the step-through-every-slide capture and the pdf-lib PDF. Used for `shots`, `pdf` and the diagram bake. Its image-only PPTX path was not taken (the engine writes an editable PPTX). |
| `navaigate-deck` skill and `references/keynote-mode.md` | Daniel's own, private | The house rules (one point per slide, look at every slide at presentation size, cut words not type, every chart states its source, numbers are evidence only, never overwrite, send a PDF), the visual acceptance gate and keynote mode, rewritten without his brand, paths or client examples. |
| `presentations` skill | Daniel's own, private | The routing: every build goes through the shared engine, HTML first, review, then PPTX. |
| pptxgenjs | MIT | Not bundled. `shelf-decks setup` installs it. |
| puppeteer-core | Apache-2.0 | Not bundled. Installed by `setup`; it drives the member's own Chrome, no browser download. |
| pdf-lib | MIT | Not bundled. Installed by `setup`. |
| Northwind Bakery sample, logo and three illustrations | Made for this pack (SVG drawn by hand, rasterised in Chrome) | Fictional. Every figure on the slides is labelled as made up. |

## What changed in the copied engine

- `profiles.js`: only `editorial-light` remains. `memberProfile(brand)` builds the `member` profile from
  `brand.json` (bare hex colours, `#` tolerated; display and body fonts with a web-font href and optional PPTX font
  names; logo; label; `imageStyle`). Missing `accentD`/`accentL` are derived from `accent`.
- `brand.js` (new): finds `brand.json` (beside the spec, `$SHELF_DECKS_BRAND`, then
  `~/.config/shelf-decks/brand.json`) and runs a WCAG contrast check on the colour pairs the builders use.
- `render.js`: HTML first, then the PPTX; outputs are `<name>_vN.*` and never overwritten; diagram slides with no
  PNG are baked in Chrome to `images/<image>.baked.png`; exports `renderDeck()`; exposes `window.deck` so capture
  can drive the deck.
- `builders-pptx.js`: the macOS-only `sips` calls are now optional (`images.js` reads PNG/JPEG sizes; without
  `sips` pptxgenjs crops with `sizing: cover`); brand logo on light slides and the cover; split-slide captions
  stay on the text panel; title parts are inline like the HTML (they were joined with line breaks on the split,
  dark-grid and hero slides, so the two outputs differed).
- `builders-html.js`: logo in the footer and on the cover; images may carry an extension (`close.jpg`); the `dek`
  line gets its top margin back (it was overridden by `.reveal p`); default labels "With AIOS"/"AIOS" became
  "After"/"Foundation".
- `diagrams.js`: `flow` boxes shrink with the stage count so arrows never overlap the boxes.

## Left out, and why

| Left out | Why |
|---|---|
| The two house profiles and the two client-brand profiles in `profiles.js` | House and client brands. Members bring their own `brand.json`; `editorial-light` is the neutral default. |
| The engine's "house default look" art direction (one image generator, one dark isometric style) | Image style is now a brand setting (`imageStyle`). The pack generates no images and needs no image key. |
| `deck.example.js` and the HTML/PPTX rendered from it | Daniel's own playbook content, with his figures. Replaced by the fictional Northwind sample. |
| The Editorial template build (`90_Presentations/NavAIgate_Editorial_Template_v2/build.mjs`) | It runs on Codex's private `@oai/artifact-tool` runtime under `~/.cache/codex-runtimes`, which has no licence to redistribute and cannot ship. Not ported. |
| Every client-branded deck skill (the client and venture deck skills in Daniel's library) | Client brands and private material. |
| The presentations skill's legacy templates, styles and per-client brand notes | Superseded by the engine; they carry client fonts and colours. |
| `html-deck-export`'s image-only PPTX | The engine writes a native, editable PPTX. |

## Shared-file changes needed (I did not edit these)

1. **`.claude-plugin/marketplace.json`**: replace the `shelf-decks` entry with `MARKETPLACE_ENTRY.json`
   (version 2.0.1, new description).
2. **`scripts/install_pack.py`**: no change. `bin/shelf-decks` is a Node script; `main` already links `bin/`.
   (The `shelf-video/install_pack.diff` no longer applies and is not needed for this pack.)
3. **`README.md` and `ROADMAP.md`**: module 12 line for shelf-decks: "Decks in your own brand: one spec renders an
   animated HTML deck to review, a matching editable PowerPoint and a PDF."
4. **CI**: `cd plugins/shelf-decks && npm install && node --test ../../tests/shelf-decks/*.test.js`. The bake test
   needs Chrome; set `SHELF_DECKS_SKIP_BROWSER=1` on runners without it.
5. **`.gitignore`**: the pack has its own `.gitignore` (node_modules, rendered sample outputs). No root change.

## Known limits

- The PPTX shows brand fonts only where they are installed; the sample sets `displayPptx: Georgia` and
  `bodyPptx: Arial` so it opens cleanly anywhere. The HTML and PDF use web fonts.
- PowerPoint and the browser wrap text with different engines; the PPTX cover title is tuned per deck with
  `titleSize`/`titleY` (see the sample).
- Screenshots, the PDF and the diagram bake need a local Chrome, Edge, Brave or Chromium.
- Logos and images must be PNG or JPEG.

## Kept out of the repo

Lessons, tutorial scripts, the sandbox proof, prompt proofs and eval results live on the NAS under
`150_Navbot_Classroom/aios-2/` (`lessons_v2/12-shelf-decks/`, `tutorials_v2/12-shelf-decks/`,
`build-proof/shelf-decks/`), never in Git.
