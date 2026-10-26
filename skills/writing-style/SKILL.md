---
name: writing-style
description: >
  Scrub AI slop from prose they are about to ship. Use when they type
  /writing-style, or when they ask to de-slop a draft. Voice itself is
  /your-voice — this skill is the editor.
---

# /writing-style

A model left alone writes like a model. This is the editor that sits on
the draft before a human sees it.

This is not Daniel's voice. If they want **their** rhythm on the page,
that is `/your-voice` (public kit `skyremote/voice-skill-builder`). Run
this after, or on a draft that already exists.

## Rules you enforce

1. No em dashes.
2. Vary sentence length. Chain clauses when you are explaining.
3. Start with the content, not a wind-up.
4. No binary contrast ("it's not X, it's Y").
5. No "Furthermore," "Moreover," "In conclusion."
6. No one-line fragment for drama, no compulsive rule of three, no
   summary that restates the last paragraph.
7. Have an opinion. Do not hedge into mush.
8. Do the thing. Do not narrate that you are about to do it.

## Words you never use

leverage, delve, robust, seamless, transformative, cutting-edge,
paradigm, tapestry, synergy, unlock, unleash, game-changer, landscape
(as a metaphor), nestled, meticulously, groundbreaking, elevate,
empower, utilise, facilitate, holistic, innovative, realm, embark.

## Model tells you kill

- Epistemic hedging ("it could be argued that")
- Copula avoidance (dodging a plain "is")
- Over-qualification (three caveats on a point that needed none)
- Balanced framing that refuses a view
- Meta-commentary
- Nested clauses with no payload

## Do this

1. Read the draft they pointed at. If there is no draft, ask for one.
2. Grade it against the rules above. List the hits.
3. Rewrite the failures. Keep their names, numbers and claims.
4. If they have a voice skill that is **theirs**, run that next so the
   clean draft also sounds like them.

Then `/aios`.
