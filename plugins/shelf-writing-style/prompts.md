# Prompts: shelf-writing-style

Paste one of these into Claude. The editor keeps your names, numbers and claims and removes the slop.

Every prompt below was run headless in a clean sandbox with this pack installed, on the fictional data shown.
Replace the sample names and figures with your own.

## Prompt 1: Grade a pasted draft and rewrite it

**You need:** Nothing. Swap the sample paragraph for your own.

```text
Use the writing-style skill on this draft for the Northwind Bakery newsletter. List which rules it breaks, then rewrite it. Keep every name, number and claim exactly as they are.

"At Northwind Bakery, we are thrilled to unveil our transformative new loyalty scheme — it's not just a card, it's a game-changer. Furthermore, we leverage a robust, seamless app to empower every customer to unlock rewards. In March, Saturday sales rose 38% to £4,200. In conclusion, we believe this will elevate the whole high street."
```

## Prompt 2: Clean a file and keep the original

**You need:** A file called launch-note.md in the folder you start Claude in.

```text
There is a file called launch-note.md in this folder. Use the writing-style skill on it. In your reply, list the hits first. Then save the cleaned version as launch-note_v2.md and leave launch-note.md as it is.
```

## Prompt 3: Grade only, no rewrite

**You need:** Nothing. Swap the paragraph for your own.

```text
Use the writing-style skill, but only grade this paragraph from the Acme Studio proposal. Do not rewrite it. Give me a numbered list of the rule hits and the exact words that triggered each one.

"It could be argued that Acme Studio's holistic approach to branding is, in many ways, rather innovative. Our team meticulously crafts identities that resonate. The result? A brand that is not merely seen, but felt. We embark on every project with fresh eyes."
```
