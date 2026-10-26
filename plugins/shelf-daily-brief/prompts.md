# Prompts: shelf-daily-brief

Paste one of these into Claude from inside your project folder. The brief reads your CLAUDE.md, funnel.md and your SQLite numbers, and writes one file under outputs/daily-brief/. You need one model key (OpenAI, Anthropic, OpenRouter or Gemini) in ~/.claude/.env, and the Python packages from the README.

Every prompt below was run headless in a clean sandbox with this pack installed, on the fictional data shown.
Replace the sample names and figures with your own.

## Prompt 1: Set it up and do a test run, nothing saved

**You need:** A project folder with CLAUDE.md, funnel.md and a SQLite file in data/. One model key.

```text
Use the daily-brief skill in this folder (the Northwind Bakery project). Check the model key first and tell me which provider and model it will use. Then do a test run with the small_team preset so nothing is saved, and show me the brief. Tell me which metrics it found, and which sections it left out and why.
```

## Prompt 2: Run it for real and save it

**You need:** The same project, once you like the test run.

```text
Use the daily-brief skill in this folder. Run the real brief for the most recent day in the data with the solo preset, so it gets saved. Then show me the path of the saved brief and its dashboard image, and read me the three most important lines of the brief.
```

## Prompt 3: Fix a wrong number by changing the funnel map

**You need:** The same project.

```text
Use the daily-brief skill in this folder. The brief says our revenue figure is wrong: revenue should come from the sales_daily table, the column called takings, not the one it is reading now. Open funnel.md, make that change, run a test (nothing saved) and show me the revenue line before and after.
```
