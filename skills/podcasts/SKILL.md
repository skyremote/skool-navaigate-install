---
name: podcasts
description: >
  Find the right podcast episodes, rank them, and pull full transcripts.
  Use when they type /podcasts or ask for interviews / episode transcripts.
---

# /podcasts

The sharp stuff is said, not blogged. Find the episode, rank it, pull the
words.

This uses the same helper as `/web-scrape`. Exa / Firecrawl for the open
web. Supadata for YouTube search and transcripts. Podcasts do not have a
separate API — YouTube plus a web search is the path that works today.

## Keys

In `~/.claude/.env`, one per line:

```
EXA_API_KEY=...
FIRECRAWL_API_KEY=fc-...
SUPADATA_API_KEY=...
```

If a key is missing, say which one and stop. Supadata is paid and
metered — keep research small.

Helper (from this plugin):

```bash
python3 <plugin>/skills/web-scrape/scripts/webscrape.py search "..." --text
python3 <plugin>/skills/web-scrape/scripts/sources/supadata.py search "..." --limit 10
python3 <plugin>/skills/web-scrape/scripts/sources/supadata.py transcript "<youtube-url>" --lang en
```

## Do this

1. Search the open web (Firecrawl / Exa) for the topic on Apple, Spotify
   and show sites. That is the wide net.
2. Search YouTube via Supadata with recency and length if they asked
   ("last six months", "over forty minutes"). That is the deep net.
3. Rank a shortlist, not a dump. Score view count, duration, and whether
   the show actually interviews operators. Best three at the top, with
   why.
4. Pull **full transcripts** of the ones they pick. Not a summary. The
   specifics are the point.
5. If they asked for themes, quote the guests. Do not flatten it.

Then `/aios`.
