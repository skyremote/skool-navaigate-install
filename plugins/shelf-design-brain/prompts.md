# Prompts: shelf-design-brain

Paste one of these into Claude after you have downloaded the corpus zip from the Design Brain lesson (see the README). Every answer should carry an entry number and a named source.

Every prompt below was run headless in a clean sandbox with this pack installed, on the fictional data shown.
Replace the sample names and figures with your own.

## Prompt 1: Ask a design question and get citations

**You need:** The Design Brain corpus unzipped into your skills folder.

```text
Use the design-brain skill. I am building a menu page for Northwind Bakery. What contrast ratio does the body text need, and what about the large price headings? Cite the entry number and the named source for each answer, and give me the exact numbers the entry states.
```

## Prompt 2: Critique a page of yours

**You need:** The corpus, and a page to critique. This prompt uses a file called pricing.html in the folder you start Claude in.

```text
Use the design-brain skill to critique pricing.html in this folder, the pricing page for Acme Studio. Measure what you can (contrast, font sizes, line length) instead of guessing. Give me findings in severity order. For each one give: the problem, the entry number and title, the rule, the named source and the concrete fix. Then name one thing the page does well, with its entry number.
```

## Prompt 3: Choose a chart type, and say where the corpus is silent

**You need:** The corpus.

```text
Use the design-brain skill. Northwind Bakery wants to show sales by weekday for the last 12 weeks. Should I use a bar chart, a line chart or a pie chart? Answer from the corpus with entry numbers and named sources. If the corpus says nothing about part of my question, say so plainly instead of filling the gap with general advice.
```
