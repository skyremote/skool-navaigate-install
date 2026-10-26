# shelf-decks: the deck format, the brand and the fixes

## Install the tools once

```sh
python3 -m pip install --user python-pptx Pillow playwright
python3 -m playwright install chromium
```

python-pptx is MIT-licensed, Pillow is MIT-CMU, Playwright is Apache-2.0. None of them needs an account.
Without Playwright the deck still builds and exports, but review cannot measure overflow or make slide images,
so export stops at the review step. Install it.

## Commands

```sh
shelf-decks brand check                      # show your brand and its contrast ratios
shelf-decks brand set colours.accent=#C2410C # change one value
shelf-decks new ~/Decks/q3-review --title "Q3 client review"
shelf-decks build ~/Decks/q3-review          # out/deck_v1.html
shelf-decks review ~/Decks/q3-review         # out/review_v1/ slide images, montage, report
shelf-decks export ~/Decks/q3-review --pdf   # out/deck_v1.pptx and deck_v1.pdf
shelf-decks verify ~/Decks/q3-review         # reads the PowerPoint back
shelf-decks sample ~/Decks/acme-sample       # practice deck for the fictional Acme Studio
```

In the HTML deck, the arrow keys move between slides, N shows speaker notes, and a click moves forward.

## The brand

Default file: `~/.config/aios/shelf-decks.json`. A `brand.json` beside a deck wins over it.

| Key | Example | Used for |
|---|---|---|
| `name` | `Acme Studio` | Footer when `footer` is blank |
| `footer` | `Acme Studio, confidential` | Footer on content slides |
| `colours.background` | `#FBFAF7` | Slide background |
| `colours.text` | `#1F2328` | Titles and body |
| `colours.muted` | `#5B6470` | Subtitles, sources, footer |
| `colours.accent` | `#C2410C` | Bars, numbers, bullets, section slides |
| `colours.accent_text` | `#FFFFFF` | Text on the accent colour |
| `colours.surface` | `#F1EEE8` | Panels behind numbers, footer rule |
| `fonts.heading` / `fonts.body` | `Georgia` / `Arial` | Font names, as PowerPoint knows them |
| `fonts.heading_file` / `fonts.body_file` | `~/Fonts/Brand-Bold.ttf` | Optional: embeds the font in the HTML |
| `logo` | `~/Brand/logo.png` | PNG or JPG, top right of content slides, larger on the title |

The review fails if text on background or muted on background is under 4.5:1, accent on background (used only
for large text) is under 3:1, or accent_text on accent is under 4.5:1. These are WCAG 2.2 contrast levels.

## Layouts

Put the layout in square brackets on the first line of a slide. Without one, the first slide is `[title]` and
the rest are guessed from what they contain. Slides are separated by a line with three dashes.

| Layout | What it needs |
|---|---|
| `[title]` | `# Title`, optional `## subtitle` |
| `[section]` | `# Title`, optional `## subtitle`. Full accent colour. |
| `[bullets]` | `# Title`, up to six `- bullets` (indent two spaces for a second level), or plain lines |
| `[two-column]` | `# Title`, then two `### Heading` groups, each with bullets |
| `[stat]` | `# Title`, one to three `- 38% :: what it means`, and `source:` |
| `[bars]` | `# Title`, two to seven `- Label :: 412`, and `source:` |
| `[quote]` | `> the quote`, `-- Name, role`, optional `# kicker` |
| `[image]` | `# Title`, an optional line of text, `![what it shows](images/file.png)` |
| `[closing]` | `# Thank you`, `## contact line` |

Anywhere: `**bold**` inside a line, and `notes:` for speaker notes (everything after it, to the end of the slide).

```
[stat]
# What changed in twelve weeks
- 38% :: More online bookings
- 6 h :: Staff phone time saved each week
source: Booking system, July to September 2026
notes: Say where the numbers come from.
```

## Common problems

| Message | Fix |
|---|---|
| "the body text does not fit" | Cut words or split the slide. Type size is fixed on purpose. |
| "needs a source: line" | Add `source:` with whose figures and when, or remove the numbers. |
| "deck.md changed after deck_vN was built" | Run build again, then review. |
| "Brand contrast too low" | Darken the text colour or lighten the background, then `brand check`. |
| "Could not start Chromium" | `python3 -m playwright install chromium` |
| The PowerPoint shows a different font | That font is not installed on the computer opening it. Install it, or send the PDF. |
| An SVG logo is refused | Export a PNG at about 600 px wide and set `logo` to it. |
