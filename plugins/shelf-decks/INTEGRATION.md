# shelf-decks: integration notes for the chief of staff

## Where the pack came from, and what it ships

| Source | Owner and licence | What this pack took |
|---|---|---|
| `navaigate-deck` (Daniel's local skills) | Daniel, private, no licence file | The method only: one point per slide, look at every slide at presentation size, fix crowding by cutting words not shrinking type, every chart states its source, never overwrite (new `_vN`), fonts must exist on the opening machine so send a PDF. No code, template, palette, fonts or layouts copied. |
| `html-deck-export` (Daniel's local skill) | Daniel, private, no licence file | The idea of rendering each slide in headless Chrome for a faithful image. Rewritten in Python with Playwright; no code copied. |
| `presentations`, `powerpoint-html-edit` (Daniel's local skills) | Daniel, private | The HTML-first, PPTX-second order. No code, styles or brand profiles copied. |
| python-pptx | MIT | Not bundled. pip install command given. |
| Playwright for Python | Apache-2.0 | Not bundled. pip install command given. |
| Pillow | MIT-CMU | Not bundled. |

## Left out, and why

| Left out | Why |
|---|---|
| The NavAIgate Editorial and Slate templates, palette, Poppins/Fraunces choice, N logo | NavAIgate brand assets. The brief says no NavAIgate brand assets. Members set their own brand. |
| Brand profiles for Autodesk, Katana, ComXo, SkyRyd, SUSE | Client and venture brands, not Daniel's to give away, and private. |
| `build.mjs` and Codex's `@oai/artifact-tool` presentation runtime | Depends on a Codex-internal runtime under `~/.cache/codex-runtimes`, with no licence to redistribute. |
| Nano Banana image generation | Needs a paid Google key and is a separate skill. Members add their own images as PNG or JPG. |
| The reveal.js engine and the in-browser edit panel | Heavier than needed. The pack's HTML is a small self-contained viewer with keyboard navigation and notes. |
| Keynote mode, charts beyond bar and stat layouts | Planned for a later version. |
| Image-baked PPTX (screenshots in slides) | Members asked for editable decks. The PDF covers pixel-perfect sharing. |

## Shared-file changes needed (I did not edit these)

1. **`.claude-plugin/marketplace.json`**: add the object in `plugins/shelf-decks/MARKETPLACE_ENTRY.json`.
2. **`scripts/install_pack.py`**: covered by `plugins/shelf-video/install_pack.diff` (pack list from the plugins
   folder, `aios` required first, `bin/` linked into `~/.local/bin`). Apply it once for all three shelf packs.
3. **`README.md` and `ROADMAP.md`**: list `shelf-decks` under module 12: "A deck in your own brand: HTML first,
   every slide reviewed, then an editable PowerPoint and a PDF."
4. **Tests in CI**: `python3 -m unittest discover -s tests/shelf-decks` (23 tests). The browser tests need
   `python3 -m playwright install chromium` and skip without it.

## Known limits

- PowerPoint and the browser wrap text with their own engines, so a line can break one word differently.
  The layout leaves room for that, and the review checks the browser version.
- LibreOffice spaces lines slightly wider than PowerPoint. Checked on the sample: nothing overflowed.
- Logos and images must be PNG or JPG, because python-pptx cannot place an SVG.

## Kept out of the repo (Daniel's ruling, 26 October 2026)

The repo holds the pack, its README and install steps, tests and evals. Course content and build evidence live
in the classroom folder on the NAS (local mirror `~/NAS_Local/150_Navbot_Classroom/aios-2/`), never in Git:

| Kept out | Where it lives |
|---|---|
| `lessons/` (lesson Markdown and paste-ready HTML) | `lessons_v2/12-shelf-decks/` |
| `video/` (tutorial scripts, shot lists, SRTs, clips) | `tutorials_v2/12-shelf-decks/`; films in the NavMotion project's `deliver/` |
| `plugins/*/proof/` (sandbox install proof, eval results) | `build-proof/shelf-decks/` |

`tests/shelf-video/sandbox_proof.py` and `tests/shelf-video/eval_report.py` write there by default
(`AIOS2_PROOF_DIR` changes it).
