# shelf-decks: prompts to paste into Claude

Paste one of these into Claude Code (or Codex or Cursor) with the pack installed. Change the words in the
brackets to your own. Claude runs the `shelf-decks` command for you, shows you the HTML deck first, and only then
makes the PowerPoint and the PDF.

## 1. A deck in my brand, HTML first

```
Make me a 10-slide deck for [Northwind Bakery]'s investors about [opening a second shop], in my brand.
Agree the slide titles with me first, one point per slide. Use only the numbers I give you and put a source on
every slide that has one. Show me the HTML first and screenshot every slide so we can review it together.
Only make the PowerPoint and the PDF when I say it looks right.
```

What you get: a list of titles to approve, then `<name>_v1.html` with a screenshot of every slide and a contact
sheet, then (when you approve) `<name>_v1.pptx` and `<name>_v1.pdf`.

## 2. Set up my brand once

```
Set up shelf-decks with my brand. My company is [Acme Studio], my main colour is [#C2410C], my text colour is
[#1C1917], my background is [#FAF7F2], my fonts are [Fraunces] for headings and [Inter] for body text, and my
logo is at [~/Brand/acme-logo.png]. My images should look like [warm documentary photography, no text in the
image]. Then check the colours are readable and render the practice deck in my brand so I can see it.
```

What you get: your `brand.json`, a contrast check with any colour pair that is too faint, and the Northwind
practice deck rendered in your colours, fonts and logo.

## 3. Review and fix a deck before I send it

```
Review my deck at [~/Decks/q3-review/deck.js]. Render it, screenshot every slide and look at each one at full
size. Fix anything crowded by cutting words or splitting the slide, never by making the text smaller. Check every
number has a source on the slide and no two neighbouring slides look the same. Then give me the PowerPoint and
the PDF.
```

What you get: a list of what was wrong on which slide, a new `_v2` (the old version stays), fresh screenshots,
then the PPTX and the PDF.
