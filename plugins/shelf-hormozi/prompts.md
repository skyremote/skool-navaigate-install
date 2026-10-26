# Prompts: shelf-hormozi

Paste one of these into Claude. This pack is the front door to the Hormozi offer engine. The cited, book-grounded answers need skills you build from your own copies of the books (from the Inner Circle gold lesson); without them, Claude tells you what to install and does not guess.

Every prompt below was run headless in a clean sandbox with this pack installed, on the fictional data shown, except the one marked unproven.
Replace the sample names and figures with your own.

## Prompt 1: Check what you have and what is missing

**You need:** Nothing. Claude looks in your skills folder.

```text
Use the hormozi skill. Check whether the book-grounded Hormozi skills (Grand Slam Offer Builder, Offer Enhancer, Lead Engine Planner, Money Model Architect, Ask Hormozi) are installed on this machine. List which ones are present and which are missing, and tell me exactly what to do next to get the missing ones using my own copies of the books. Do not answer any Hormozi question until I have them.
```

## Prompt 2: Ask about your offer, with citations

**You need:** The book-grounded skills installed from your own books. Without them Claude should say it cannot cite, and stop.

```text
Use the hormozi skill. Northwind Bakery sells a GBP 29 monthly subscription box: a loaf, two pastries and a jar of jam. People cancel after two months. What would Hormozi say about the guarantee and the pricing here? Cite book, chapter and page for every claim, using only the five book-grounded Hormozi skills. If they are not installed, say so and stop. Do not go looking for book files elsewhere on this computer, and do not answer from memory. If you cannot cite it, say so and do not invent anything.
```

**Not proven end to end:** the cited answer needs the member's own book-derived skills, which cannot be in the repo or in a sandbox. The proof run covers the no-corpus path: Claude said the five skills are missing, pointed to the gold lesson, and cited nothing.
