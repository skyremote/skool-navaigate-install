# Prompts: shelf-podcasts

Paste one of these into Claude. It searches wide, searches YouTube, ranks a shortlist of three, and pulls full transcripts only for what you pick. Supadata is metered, so keep it small.

Every prompt below was run headless in a clean sandbox with this pack installed, on the fictional data shown.
Replace the sample names and figures with your own.

## Prompt 1: A shortlist of three, ranked

**You need:** Exa, Firecrawl and Supadata keys in ~/.claude/.env.

```text
Use the podcasts skill. I run Northwind Bakery. Find the best three podcast episodes from the last two years where café or bakery owners talk about keeping their regular customers coming back. Search the open web and YouTube, rank a shortlist, put the best three at the top and tell me why each made the cut. Do not pull any transcript yet. Keep Supadata use to one search.
```

## Prompt 2: Find it, then pull one full transcript and quote the guest

**You need:** Exa, Firecrawl and Supadata keys in ~/.claude/.env.

```text
Use the podcasts skill. For Acme Studio: find one strong episode (over 30 minutes) where a studio founder talks about pricing creative work. Pull the full transcript of that single episode and save it to transcripts/pricing_episode_v1.txt. Then quote the guest, word for word, on how they decided what to charge. Tell me the episode title, show and link first.
```
