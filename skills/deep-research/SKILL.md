---
name: deep-research
description: >
  Run a multi-source research pass with the web-scrape helper. Use when
  they type /deep-research or ask to research something properly.
---

# /deep-research

One search box is not research. This is the pass we actually run: scope,
recon, sources in parallel, a critic pass, then a synthesis with
confidence labels.

The helper lives in this plugin under `skills/web-scrape/`. Read
`references/research-method.md` there and follow it. Do not invent a
second orchestrator.

## Keys

Same as `/web-scrape`. Put theirs in `~/.claude/.env`. Missing key → say
which one and stop.

## Do this

1. Scope the question in one sentence they agree with.
2. Recon each source as hot / warm / cold (web, Reddit, papers, Substack,
   YouTube if they asked).
3. Run the live sources. Exa to find, Firecrawl to extract. Academic is
   keyless. Reddit via Composio if they have it, else the public JSON
   fallback. Supadata only when video evidence is wanted — it is paid.
4. Critic pass: recency, source type, specificity, independence.
5. Synthesise with confidence labels. Quote. Do not flatten.

Then `/aios`.
