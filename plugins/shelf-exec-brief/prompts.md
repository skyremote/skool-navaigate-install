# Prompts: shelf-exec-brief

Paste one of these into Claude from your project folder. You get a single HTML file in briefs/ that prints to a 3 to 4 page A4 PDF. Only figures you give it appear as figures; anything unmeasured says "not yet".

Every prompt below was run headless in a clean sandbox with this pack installed, on the fictional data shown.
Replace the sample names and figures with your own.

## Prompt 1: A decision brief from the figures you have

**You need:** Nothing to install. Open the HTML in a browser to read or print it.

```text
Use the exec-brief skill. Write a decision brief for the leadership team of Acme Studio. The decision: move our website hosting from Provider A to Provider B. What I know: we pay GBP 480 a month now (GBP 5,760 a year); Provider B quotes GBP 310 a month on a 12-month term; we have had 2 outages in the last 12 months, both under 40 minutes; we have not measured page speed on Provider B. Recommend moving, with the ask in bold. Anything I have not measured must say "not yet" or "not measured". Save it as briefs/Acme_Studio_Hosting_Brief_v1.html.
```

## Prompt 2: Update the brief when the facts change, without overwriting

**You need:** The brief from prompt 1 in the same folder.

```text
Use the exec-brief skill. New facts for the Acme Studio hosting brief: we ran a speed test on Provider B and the home page loaded in 1.4 seconds against 2.1 seconds on Provider A, both measured on 26 October 2026. The before-and-after chart should now have both states. Make it version 2 and do not overwrite version 1. Tell me exactly what changed between the two files.
```

## Prompt 3: A second brief on a different decision

**You need:** Nothing to install.

```text
Use the exec-brief skill. Decision brief for Sam, the owner of Northwind Bakery: should we open a Saturday-only market stall? Known: a stall pitch costs GBP 65 a Saturday; our shop does about GBP 1,350 on a normal Saturday; we have not run a stall before so we have no stall sales figures; one baker could staff it without hiring. The recommendation is a 6-week trial, not a commitment. Mark everything unmeasured as "not yet". Save it as briefs/Northwind_Stall_Brief_v1.html.
```
