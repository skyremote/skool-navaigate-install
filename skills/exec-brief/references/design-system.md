# Executive brief — design contract

The template (`../assets/template.html`) is the executable form of this
contract. Do not freelance new colours or fonts.

## Tokens

```css
--paper: #faf9f5;
--paper-raised: #f1efe9;
--paper-sunk: #e6e2da;
--ink: #1a1c20;
--quiet: #5c5a54;
--faint: #8f887f;
--rule: #dedbd1;
--rule-strong: #c4bcae;
--accent: #8fa9c4;
--accent-ink: #3a5573;
--slate: #25303f;
--coral: #c9785a;
--green: #5d755f;
```

Type: Poppins 400/500/600/700, fallbacks "Avenir Next", "Helvetica Neue",
Arial. Base 9.2pt / 1.48. Tabular numbers. H1 34pt on the decision page,
~27pt on section pages.

## Page skeleton

`main.document` → `section.page` (210mm × min 297mm). Slate bar on top.
Running head left (NavAIgate + accent dash) and context · date right.
Footer: label left, `NN / NN` right.

`@page { size: A4; margin: 0 }`. Print colours pinned.

## Components (compose, do not invent)

Eyebrow + H1 + dek. `dl.meta`. `.recommendation`. Intro / two / three
column grids. `.plain-list` and `.risks`. `.formula`. `.metric-strip`.
`.chart-card` + inline SVG. Tables with `.recommended`. `.callout-line`.
`.decision-band`. `ol.scope-list`. `.blind-spots`. `.work-table`.

## Content laws

1. A number appears when it was measured.
2. Unknowns are labelled.
3. Recommendation on page 1, ask in bold.
4. Three blind-spot cards.
5. Work-to-date with receipts and a `next` row.
6. Provenance under data tables.
7. Version `_v1` / `_v2`. British English. No emojis.
