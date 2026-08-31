# Substack (free, no key)

Two-layer Substack research:

1. **Discovery** — find Substack posts on a topic. Routes through this skill's
   `webscrape.py`: **Exa** semantic search (domain-filtered to `substack.com`)
   first, **Firecrawl** `site:substack.com` search as fallback. So discovery uses
   the Exa/Firecrawl keys already in `~/.claude/.env`; nothing new.
2. **Extraction** — pull a post's **full body + metadata** via Substack's public
   `/api/v1` endpoints (undocumented but unauthenticated): `/archive` for a
   publication's post list, `/posts/{slug}` for full content.

Use Substack for **long-form thought leadership and named-author analysis**:
operator essays, founder write-ups, technical deep-dives. Strong for "who are the
credible voices on X and what's their actual argument", weaker for breaking news.

## CLI

```bash
SS=~/.claude/skills/web-scraping/scripts/sources/substack.py

# Discover posts on a topic (Exa semantic, Firecrawl fallback)
python3 $SS search "AI agents in production" --limit 10

# Find publications (newsletters) on a topic
python3 $SS publications "LLM evals" --limit 10

# List a known publication's archive
python3 $SS archive theaiengineer --limit 12 --sort new

# Get one post's full text + metadata (--html for raw HTML body)
python3 $SS post theaiengineer the-ai-agents-stack-2026-edition

# Full pipeline: discover -> extract full content for the top hits
python3 $SS research "AI coding agents" --posts 5 --limit 10
```

Add `--json` (before or after the subcommand) for the raw payload.

## What you get

Discovery results: `title, url, description, publication, slug` (publication+slug are
parsed from the URL, so extraction can follow). A post: `title, subtitle, date, body`
(HTML stripped to clean text by default), `body_length, wordcount, reactions,
comment_count, audience, publication, url, canonical_url`.

## Notes

- Discovery needs `EXA_API_KEY` (preferred) and/or `FIRECRAWL_API_KEY`. Extraction
  via the Substack API needs **no key**.
- The Substack API is rate-limited client-side to 2s between calls and retries once
  on a 429. Some publications on custom domains or with private archives return
  nothing from `/archive` or `/posts` — that's expected, not an error.
- For a publication you already know, skip discovery: go straight to `archive` then
  `post`.
