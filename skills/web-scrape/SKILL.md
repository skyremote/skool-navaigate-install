---
name: web-scrape
description: >-
  Search the web semantically and pull clean content from pages, including
  JavaScript-heavy ones. Use whenever you need live web data during a task:
  finding docs, API references, code examples, articles, papers, or current info
  (Exa semantic search), or extracting the readable content of a specific URL —
  especially a JS-rendered, dynamic, or paywalled-by-script page a plain fetch
  returns empty (Firecrawl). Trigger even when the tools aren't named: "scrape
  this page", "search the web for", "pull the content from this URL", "find
  docs/articles about", "extract data from this site", "what does this page say",
  "research X online", "get me the latest on". Also bundles source clients —
  keyless Reddit (practitioner sentiment), Academic (OpenAlex papers + Unpaywall
  free PDFs, citations), Substack (newsletters, long-form), and paid Supadata
  (YouTube search + multi-platform transcripts) — plus a multi-source
  deep-research method: reach here for "what do people on Reddit say", "find
  research papers / citations on", "read this Substack / newsletter", "YouTube
  transcript", "video transcript", or "do a rigorous deep research pass on X".
---

# /web-scrape

Community copy of how we read the web today. **Their** keys in
`~/.claude/.env` — never Daniel's. Reddit via Composio uses
`COMPOSIO_USER_ID` from that file (falls back to the machine user). After
this command, they type `/aios` and pick the next module.

Two providers behind one helper script, picked by job:

- **Exa** — *semantic* web search. You describe what you want in natural
  language and get back the most relevant pages, optionally with excerpts,
  full text, summaries, or a grounded structured answer. Use it to **find**
  things and to answer "where is X / what's the best source on Y".
- **Firecrawl** — a real headless-browser **scraper**. It executes JavaScript
  and returns clean markdown. Use it to **read** a specific URL, especially a
  single-page app, infinite-scroll page, or anything where the raw HTML is a
  shell that fills in via JS.

Rule of thumb: **Exa to discover, Firecrawl to extract.** If you already have
the URL and just need its rendered text, go straight to `scrape`. If you need
the *content of pages Exa already found*, Exa can return it inline (`--text`)
— you don't always need a second Firecrawl call.

## Setup (one-time)

Keys live in `~/.claude/.env`, one `KEY=VALUE` per line:

```
EXA_API_KEY=...
FIRECRAWL_API_KEY=fc-...
```

The helper auto-loads that file, so you don't need to export anything. It uses
`requests` over REST — no `exa-py` or `firecrawl` SDK install required. If a
key is missing the script tells you exactly which one and where to put it.

## The helper

All web work goes through one script. Run it with `python3`:

```bash
python3 ~/.claude/skills/web-scraping/scripts/webscrape.py <command> [options]
```

Add `--json` to any command for the raw API response (use when you need
fields the human view drops, e.g. publish dates, scores, screenshots, or
`output`/`grounding` from a structured search). Run any command with
`--help` for its full option list.

### Exa — search

```bash
# Default: balanced semantic search, query-relevant highlights per result.
python3 .../webscrape.py search "Next.js route handler authentication example"

# Full page text capped to control tokens; restrict to authoritative sources.
python3 .../webscrape.py search "supabase row level security policies" \
  --text --max-chars 6000 --include-domains supabase.com github.com

# Research-grade synthesis (slower) with a grounded structured payload.
python3 .../webscrape.py search "compare vector databases for RAG in 2026" \
  --type deep --system-prompt "Prefer official docs; collapse duplicates." \
  --output-schema '{"type":"object","required":["options"],"properties":{"options":{"type":"array","items":{"type":"object","properties":{"name":{"type":"string"},"tradeoff":{"type":"string"}}}}}}' \
  --json
```

Picking `--type` (see `references/exa.md` for the full table):

| Want | Use |
|------|-----|
| Most queries — balanced relevance/speed | `auto` *(default)* |
| Chat/autocomplete/quick lookup | `instant` or `fast` |
| Research, enrichment, hard comparisons | `deep` or `deep-reasoning` |

Content flags (`--highlights` default, `--text`, `--summary`): start with
**highlights** for agent workflows — they keep token usage predictable. Reach
for `--text --max-chars N` only when downstream reasoning needs broad page
context, and always cap it.

### Exa — contents / answer

```bash
# You already have URLs and want their clean content (no search step).
python3 .../webscrape.py contents https://a.com/post https://b.com/doc --text --max-chars 8000

# Question-first: a grounded answer with citations.
python3 .../webscrape.py answer "What changed in the React 19 compiler?"
```

### Firecrawl — scrape (JS-heavy pages)

```bash
# Render a page and print clean markdown (main content only).
python3 .../webscrape.py scrape "https://example.com/spa-dashboard"

# Give a slow SPA time to hydrate, and keep the full page (nav/footer too).
python3 .../webscrape.py scrape "https://example.com/app" --wait 3000 --full

# Other formats when you need them.
python3 .../webscrape.py scrape "https://example.com" --formats markdown links
```

`scrape` already executes JavaScript, so it handles most dynamic pages on its
own. If a page needs **clicks, form fills, or login** before the content
exists, that's Firecrawl's `actions` feature — not wired into this helper;
see `references/firecrawl.md` for how to add an `actions` array, or fall back
to the project's interactive-browser tooling.

### Firecrawl — search

```bash
# Firecrawl's own web search; --scrape also pulls each result to markdown.
python3 .../webscrape.py crawl-search "best practices structured logging" --num 5 --scrape
```

Exa's `search` is the better default for *finding* things (true semantic
ranking). Use `crawl-search` when you specifically want Firecrawl's
index + one-shot scrape of the hits.

## Source clients (Reddit / Academic / Substack free; Supadata paid)

Beyond the open web, four source clients live in `scripts/sources/`. Each is a
self-contained CLI with the same conventions as `webscrape.py` (subcommands,
`--json` before or after the subcommand, human-readable default output). Academic
and Substack are keyless; **Reddit** routes through Composio's managed toolkit
(read-only OAuth, `COMPOSIO_API_KEY` in `~/.claude/.env`) with the keyless direct
public-JSON client as an automatic fallback; **Supadata** is **paid
(credit-metered)** and needs `SUPADATA_API_KEY`. Reach for them when the *kind* of
source matters:

| Source | Script | Reach for it when you want… |
|--------|--------|------------------------------|
| **Reddit** | `scripts/sources/reddit.py` | practitioner sentiment, lived failure modes, "what actually broke / what did people pay" |
| **Academic** | `scripts/sources/academic.py` | primary research, citation-weighted credibility, the research-vs-production gap (OpenAlex + Unpaywall free PDFs) |
| **Substack** | `scripts/sources/substack.py` | named-author long-form analysis, operator essays, thought leadership |
| **Supadata** *(paid, credit-metered)* | `scripts/sources/supadata.py` | **video/transcript** evidence — YouTube search + multi-platform transcripts (YouTube/TikTok/IG/X/FB/file): "what are people saying on YouTube", the actual words of a talk/interview/demo |
| **X-Search** *(paid; dormant until xAI funded)* | `scripts/sources/xsearch.py` | **X/Twitter real-time** — "what is X/Twitter saying about …", real-time X sentiment, recent posts from specific handles (via xAI Grok's X Search tool). **Wired but dormant** until the xAI account has billing/credit (console.x.ai) |

```bash
# Reddit — via Composio managed toolkit (read-only OAuth, runs off Composio infra
# so no IP block); auto-falls back to the direct public-JSON client if unconnected
python3 scripts/sources/reddit.py research "AI coding agents in production" --threads 5
python3 scripts/sources/reddit.py thread "<reddit-url>" --comments 25

# Academic — OpenAlex + Unpaywall, free (set OPENALEX_EMAIL in ~/.claude/.env, optional)
python3 scripts/sources/academic.py search "RAG evaluation" --from-year 2023 --sort cites
python3 scripts/sources/academic.py pdf 10.1038/s41586-023-06291-2   # free PDF via Unpaywall

# Substack — discovery via Exa/Firecrawl, extraction via Substack's public API
python3 scripts/sources/substack.py search "AI agents in production" --limit 10
python3 scripts/sources/substack.py post <publication> <slug>

# Supadata — PAID/metered: YouTube search + transcript; research is conservative by default
python3 scripts/sources/supadata.py search "retrieval augmented generation" --limit 10
python3 scripts/sources/supadata.py transcript "https://www.youtube.com/watch?v=..." --lang en
python3 scripts/sources/supadata.py research "AI coding agents" --videos 3   # metered — use when video evidence is wanted

# X-Search — PAID, DORMANT until xAI funded (console.x.ai): real-time X/Twitter via Grok's X Search tool
python3 scripts/sources/xsearch.py search "what is X saying about Cloudflare Workers" --max-results 5
python3 scripts/sources/xsearch.py research "AI coding agents" --max-results 10   # same bundle shape as the others
```

Notes: **Academic** uses no key for search/citations/PDF; `--full-text` and
**Substack** discovery reuse the Exa/Firecrawl keys already in `~/.claude/.env`.
**Reddit** routes through Composio's managed Reddit toolkit (managed OAuth,
read-only, `COMPOSIO_API_KEY` in `~/.claude/.env`, `user_id from COMPOSIO_USER_ID in ~/.claude/.env`) so it runs
off Composio's infra and isn't hit by Reddit's outbound-IP block; if the Reddit
connection isn't authorised it auto-falls back to the direct public-JSON client
(which can 403 on cloud/CI networks). **Supadata** is the only **paid** source
(`SUPADATA_API_KEY`, credit-metered) — handles both sync and async (job-id
polling) transcripts; keep `research` small and reach for it only when
video/transcript evidence is specifically wanted, not on every pass. Full details
per source: `references/reddit.md`, `references/academic.md`,
`references/substack.md`, `references/supadata.md`.

*Source status / future stubs:* **Supadata** is **live** (paid). **X-Search**
(`XAI_API_KEY`, paid) is now **wired but dormant** — the code is complete and the dry
call reaches xAI correctly; it activates the moment the xAI account has billing/credit
(console.x.ai), with **no code change** (details: `references/xsearch.md`). **Podcast**
has **no dedicated endpoint** and is covered by Supadata's YouTube search + transcript
(or a direct media-file URL). Everything except Supadata and X-Search stays free.

## Running a rigorous multi-source research pass

When the task is "research X properly" rather than one lookup, don't ad-hoc it —
follow `references/research-method.md`. It captures a disciplined flow (scope →
recon with HOT/WARM/COLD per source → human checkpoint → parallel topic agents →
critic pass → confidence-labelled synthesis), a **source-scoring rubric**
(recency / source type / specificity / independence) and ready prompt templates,
all driving **our existing `deep-research` harness and `chief-of-staff` fan-out**
over the sources above. It adds no new orchestrator and no database.

## Choosing a path

```
Need live web data
├─ Have a specific URL to read?
│   ├─ Page is plain/static and small  → a normal fetch is fine
│   └─ Page is JS-heavy / dynamic / SPA → scrape
├─ Need to FIND pages by meaning       → search   (Exa)
├─ Have URLs, just want their content  → contents (Exa)  or scrape (Firecrawl)
└─ Want a direct answer with citations → answer   (Exa)
```

## Common mistakes (and the fix)

These are real API gotchas — avoid them:

- On **Exa `/search`**, `text`/`highlights`/`summary` must be **nested under
  `contents`** (the script does this). On **`/contents`** they're **top-level**.
- `useAutoprompt`, `numSentences`, `highlightsPerUrl`, `tokensNum`,
  `livecrawl: "always"`, `includeUrls`/`excludeUrls` are **deprecated or
  non-existent** — use `--max-age-hours 0` for freshness and
  `--include-domains`/`--exclude-domains` for filtering.
- Uncapped `--text` can blow up context. Prefer `--highlights`, or
  `--text --max-chars N`.
- Slow/empty `scrape` result on a dynamic page → add `--wait 2000`-`5000` to
  let JS render before extraction.
- `401` → the matching key is missing or wrong in `~/.claude/.env`.

## Deeper reference

- `references/exa.md` — search types, content config, `outputSchema`,
  `maxAgeHours`, `/contents` & `/answer`, troubleshooting.
- `references/firecrawl.md` — scrape body fields, `formats`, `actions` for
  interaction, the search endpoint, response shape.
- `references/reddit.md` — Reddit via Composio managed toolkit (read tools, execute contract), CLI, the direct public-JSON fallback and its 403/IP gotcha.
- `references/academic.md` — OpenAlex + Unpaywall CLI, paper fields, citation graph.
- `references/substack.md` — Substack discovery + extraction CLI, response shape.
- `references/supadata.md` — Supadata video/transcript CLI (YouTube search, multi-platform transcripts, sync-vs-async, cost note).
- `references/xsearch.md` — X-Search CLI (xAI Grok X Search tool: Responses API shape, `x_search` fields, model id, cost note, the dormant-until-funded gate).
- `references/research-method.md` — the full multi-source research flow, source-scoring
  rubric, and recon/topic/critic/synthesis prompt templates.

**Canonical sources of truth** (fetch these if behaviour ever contradicts the
above, and report drift back to the user):
- Exa: https://exa.ai/docs/reference/search-api-guide-for-coding-agents
- Firecrawl: https://docs.firecrawl.dev
