# Prompts: shelf-content-pipeline

Paste these into Claude in order, from inside your project folder. Each one builds on the last: set up, capture and develop an idea, then pick what to make next. Nothing is published; it plans and tracks.

Every prompt below was run headless in a clean sandbox with this pack installed, on the fictional data shown.
Replace the sample names and figures with your own.

## Prompt 1: Set up the pipeline with your strategy

**You need:** A project folder with a CLAUDE.md. No key. Python with python-dotenv.

```text
Use the content-pipeline skill to set up my content pipeline in this folder (the Northwind Bakery project). Read CLAUDE.md first and do not ask me what it already answers. Platform: Instagram. To save time, here are my answers so you do not need to interview me: we post 3 times a week; pillars are "behind the bake", "regulars and neighbourhood" and "running a small shop"; our peers are two other Bristol bakeries who post mostly product photos while we show the people; rule: never post a price we have not confirmed. Positioning: the bakery where the baker knows your name. Audience: local regulars, new neighbours, and other small shop owners. Offers: the loyalty card is free and the Saturday box is GBP 18. Write the three strategy documents under content/, run the foundation commands and show me the empty pipeline.md.
```

## Prompt 2: Capture an idea, then develop it

**You need:** The same folder, after prompt 1.

```text
Use the content-pipeline skill. Capture this idea: "Why we stamp every card by hand and what it does to the Saturday queue". Check for duplicates, classify it against my strategy and go ahead without waiting for me to confirm. Then develop it as #1: positioning, packaging, a priority and a concept document. Show me pipeline.md afterwards.
```

## Prompt 3: Schedule what to make next

**You need:** The same folder, after prompt 2.

```text
Use the content-pipeline skill to schedule. I can make about three pieces of content a week and Saturday is the busiest trading day, so no filming on Saturdays. Give the developed idea a publish date and a make-by date in the next two weeks, then run the schedule review and tell me what is overdue and what is not. Do not use Notion.
```
