# Builders: every option

Every slide is `{ type, ...opts, talk }`. The same options feed the HTML and the PPTX. Sizes such as `top` and
`cardH` are inches on a 13.333 x 7.5 inch slide (the HTML converts them). Titles take either `title: "..."` or
`titleParts: [{ text, c }]` with `c` one of `accent`, `accentD`, `ink`, `coral`, `white`.
Most content slides also take `eyebrow` (small caps line above the title) and `footer` (the centred caption at
the bottom: put the source of any number here).

| Builder | The idea it carries | Key options |
|---|---|---|
| `cover` | Open on the result | `titleParts, eyebrow, image, tagline, promise` |
| `divider` | Section break, name the enemy | `kicker, image, title, sub` |
| `statement` | One conviction | `lines[{text,c}], body, bodyBold, dark` |
| `bigStats` | Three or four hero numbers | `title, dek, items[{num,unit,label,size?}], top?, cardH?` |
| `timelineAlt` | A journey over time | `title, dek, phases[{label,title,desc,mark?}]` |
| `split` | A definition or a place | `titleParts, body, pills[], image` |
| `outcomeBars` | Before and after | `titleParts, outcomes[{title,stat,subLabel,desc,baselineRatio,baselineLabel,withLabel,barCaption}]` |
| `darkGrid` | Four points as a 2x2 | `titleParts, items[{num?,title,desc,tone?}]` (`tone`: `light` or `gold`) |
| `cards` | Three to six parallel items | `title, dek, items[{num?,title,desc}], top?, cardH?` |
| `calculator` | A price or budget | `title, foundation{name,sub,price}, modules[{name,price}], total` |
| `modules` | An ecosystem on a foundation | `numeral, title, sub, items[{name}], foundationLabel, foundationSub, gridCols?` |
| `compare` | Two options side by side | `title, dek, left{title,items[],dark?}, right{title,items[],dark?}` |
| `diagram` | A live diagram | `diagram, kicker, title, footer, image, data{...}, hint?` |
| `hero` | Image with the title over a scrim | `image, eyebrow, titleParts, sub` |
| `art` | A full-bleed picture | `image, edge?` |
| `close` | One action | `kicker, title, promise, sub, ctaPrimary, ctaSub, image` |

## Notes per builder

- **cover**: the image fills the right 58%. The brand logo sits top left. Keep the title to three short lines.
- **divider / close / hero / art**: full-bleed images get a dark overlay so white text reads; choose images with
  calm space where the words go. `close` uses `images/cover` when it has no `image`.
- **statement**: two lines of 58 px display type. `dark: true` makes it a slate slide, good for the turn in the
  argument.
- **bigStats**: numbers of five or more characters get smaller type automatically. Each `label` is one or two
  short sentences. Put the source in `footer`.
- **timelineAlt**: four to six phases. Odd phases sit above the line, even below. `mark` underlines a word in a
  phase title.
- **split**: the image fills the right 46%; `pills` are three or four short tags.
- **outcomeBars**: `baselineRatio` (0 to 1) is the "before" bar against a full "after" bar. Draw it to scale:
  4,100 against 2,400 is 0.59. Say "Scenarios, not forecasts" in `barCaption` when it is a plan.
- **cards**: at most three per deck, never three in a row. `num` ("01") turns them into numbered steps.
- **calculator**: the rows are a budget or a price list; `total` must add up.
- **modules**: `gridCols: 4` makes two rows for eight items.
- **compare**: `dark: true` on one side gives it weight (for example the answer side).

## Diagram kinds and their data

- `flow`: `data: { stages: [{ label, note, color? }] }`, three to six stages, labels of three words or fewer.
- `loop`: `data: { nodes: [{ label, note, edge, in, out }], core }`, three to six nodes; `edge` labels the arc to
  the next node; `core` sits in the middle.
- `relationship`: `data: { hub: { title, sub }, nodes: [{ name, role, note, x, y, link?, color? }], legend }`;
  `x` and `y` place each card on a 1080 x 540 canvas; `link: "dotted"` for a weak tie.
- `matrix`: `data: { rowHead, columns: [], rows: [{ label, cells: ["own" | "open" | { state: "play", title, note }] }], legend }`.
- `checklist`: `data: { rows: [{ label, evidence, color?, glyph? }], legend }`, two columns.

Always give a diagram an `image:` name. `render` bakes the live diagram to `images/<image>.baked.png` for the PPTX
when no `images/<image>.png` exists.
