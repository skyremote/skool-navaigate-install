---
name: exec-brief
description: >
  Build a cream-paper A4 executive brief as a single HTML file. Use when
  they type /exec-brief, ask for a decision brief, a board paper, or
  "that NavAIgate report style" about THEIR company.
---

# /exec-brief

This is the paper. One self-contained HTML file, A4, print to PDF from
the browser. Their decision, their figures, their names.

It is not a copy of anyone else's brief. Do not pull another operator's
machine inventory, keys, invoices, voice file, inbox, or client pack
into this document.

## Before you write

1. Name the decision in one sentence.
2. Ask who it is **to**. Default: their leadership, not a borrowed addressee.
3. Collect only numbers you can point at. If you did not measure it, label
   it "not yet" or "not measured".
4. Read `assets/template.html` and `references/design-system.md` in this
   skill. Do not invent colours or fonts.

## Pages

1. **Decision.** Running head, short H1, dek, TO/FROM/DATE/SUBJECT/DECISION,
   recommendation with the ask in bold, why it matters, already proven,
   not yet proven, one governing definition.
2. **Measurement.** Metric strip, before/after chart if you have both
   states, evidence table, provenance note.
3. **Plan or library.** The working rule, the table or protocol they
   must follow.
4. **Scope.** Blind spots (three cards), work-to-date ledger, a `next` row.

Three or four pages. One theme per page after page 1.

## Chart law

Grey = before. Green = after, filled only when you re-measured.
A perfect zero draws a 5px sliver and the label "0.000 — clean".
An unmeasured after prints "not yet" on an empty track.
Inline SVG only. No chart library.

## File it

Build in `/tmp`, then copy the final into **their** project:

`briefs/<Name>_Brief_vN.html`

Version. Never overwrite. `_v1`, then `_v2` when the facts change.
If the numbers will move again, write a small generator (JSON → HTML)
instead of hand-editing.

British English. No emojis. No metaphors. No "unlock".

## Never put in the paper

- Another person's API keys, voice, face, or photo catalogue
- Private chat history, bank feeds, or register numbers
- Client hostnames, SHAs, or delivery internals they did not ask to share
- A zip as the install path for a skill

If they want this paper about Your AIOS itself, the shelf belongs in it:
`/aios` is the picker; the remade modules are the install path; keys stay theirs.
