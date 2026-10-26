# X-Search (X/Twitter real-time — paid; DORMANT until xAI funded)

The **X/Twitter** modality for the research stack. Asks **xAI Grok** a question with
its server-side **X Search** tool enabled and returns a grounded answer plus the X
posts/handles (and any other pages) it read, as citations. Reach for it for "what is
**X/Twitter** saying about …", **real-time X sentiment**, or pulling recent posts
from specific handles — the live-pulse source the others can't give you.

Like Supadata, X-Search is **paid / credit-metered**, so it is conservative by
default (small `max_search_results`).

## DORMANT UNTIL FUNDED (read this first)

The `XAI_API_KEY` in `~/.claude/.env` is **valid with full ACLs**, but the xAI team
it belongs to is **not funded** (`team_blocked: true`): `/v1/models` is empty and
every call is rejected at the billing gate with:

```
HTTP 403  code: "The caller does not have permission to execute the specified operation"
          error: "Your newly created team doesn't have any credits or licenses yet.
                  You can purchase those on https://console.x.ai/team/<id>."
```

The client detects this (402/403 + billing/credit/team-blocked hints) and exits
cleanly with:

> xAI X-Search is wired but the xAI account needs billing/credit (console.x.ai) —
> no code change needed once funded.

**The wiring is correct** — the dry call reaches `/v1/responses`, the `x_search`
tool body is accepted by the API, and only the team-credits gate stops it (it is a
403 billing error, **not** a 404 / schema error). Add billing/credit at
**https://console.x.ai** and the same commands work with **no code change**.

## Why the Responses API (not legacy `search_parameters`)

The original Live Search shape — `search_parameters` (`mode`/`sources`/
`return_citations`/`max_search_results`/`from_date`/`to_date`) on
`POST /v1/chat/completions` — was **removed by xAI on 12 January 2026**. The current,
documented path is the **Responses API** with a server-side **X Search tool**, so
that is what this client uses. The OpenAI-compatible base is unchanged
(`https://api.x.ai/v1`, `Authorization: Bearer $XAI_API_KEY`).

## Auth & setup

- Base: `https://api.x.ai/v1`  ·  Endpoint: `POST /v1/responses`
- Header: `Authorization: Bearer <XAI_API_KEY>` (read from `~/.claude/.env` by the
  shared loader — nothing to export). A missing key is reported with where to put it.
- Model: **`grok-4.3`** (the docs' current default — "for everything else, use
  Grok 4.3"). Overridable via `--model`, else `XAI_MODEL` in `~/.claude/.env`, else
  the `grok-4.3` default. The live `/v1/models` list is empty pre-funding, so we rely
  on the documented id rather than a runtime lookup.

## Request shape (x_search tool)

```json
POST https://api.x.ai/v1/responses
{
  "model": "grok-4.3",
  "input": [{"role": "user", "content": "<question>"}],
  "tools": [{
    "type": "x_search",
    "allowed_x_handles": ["openai"],     // optional, max 20
    "excluded_x_handles": ["someacct"],  // optional, max 20
    "from_date": "2026-05-01",           // optional, ISO8601 YYYY-MM-DD
    "to_date":   "2026-06-05",           // optional, ISO8601 YYYY-MM-DD
    "max_search_results": 10             // optional; kept small (paid/metered)
  }]
}
```

Other documented x_search fields not wired by default (add if needed):
`enable_image_understanding`, `enable_video_understanding`.

## Response shape

- **Answer text** → `output[].content[].text` where `type` is `"output_text"`
  (the client also tolerates chat-completions `choices[].message.content`).
- **Citations** → top-level **`citations`** array of URL strings (the pages/X posts
  Grok read). The client also tolerates `inline_citations` and per-content
  `citations`/`annotations`.
- Citations give **URLs, not post bodies**, so the normalised post `text`/`date` are
  best-effort (blank); the **handle** is parsed from `x.com|twitter.com/<handle>`
  URLs. X citations are surfaced first; other pages follow.

## CLI

```bash
X=~/.claude/skills/web-scraping/scripts/sources/xsearch.py

# Ask Grok with X Search on; returns answer + X citations
python3 $X search "what is X saying about Cloudflare Workers vs Vercel" --max-results 5

# Constrain to specific handles and a date window
python3 $X search "AI agents" --handles openai,anthropic --from 2026-05-01 --to 2026-06-05

# Structured X-sentiment bundle (same shape as the other sources' research)
python3 $X research "AI coding agents" --max-results 10 --max-chars 12000

# Override the model id (else XAI_MODEL env, else grok-4.3)
python3 $X search "<q>" --model grok-4.3
```

Add `--json` (before or after the subcommand) for the raw structured payload.

## What you get

- **`search`** → `{query, model, answer, x_posts[], other_citations[],
  citation_count}`, where each cited post is
  `{text, author, handle, url, date, is_x}`.
- **`research`** → `{topic, model, search_results_count, search_results,
  extracted_count, extracted_posts, answer, answer_length, answer_truncated,
  other_citations}`. This mirrors the other sources' `research` shape (cf.
  Substack's `extracted_count`/`extracted_posts`, Supadata's `search_results`), so
  `research-method.md` consumes it unchanged.

## Cost note (important)

**Paid / credit-metered** (X Search is billed per source/search by xAI). Defaults are
conservative on purpose: `--max-results 10` and `research` caps the answer at
`--max-chars 12000`. Keep `--max-results` small and reach for X-Search only when
**real-time X sentiment is the point** — otherwise prefer the free sources
(Reddit/Academic/Substack/Exa).

## Gotchas

- **403 "team doesn't have any credits / team_blocked"** → the dormant-until-funded
  gate. Add billing at https://console.x.ai; no code change needed. The client maps
  this (and 402/billing/quota hints) to the funding message.
- **401** → `XAI_API_KEY` missing/wrong in `~/.claude/.env`.
- **404 / 400 schema** → a real wiring bug, **not** the funding gate. The client
  surfaces these verbatim (it does not mask them as "needs funding").
- Citations are **URLs only** — there is no full-post-body field, so `text`/`date`
  on a normalised post are best-effort and the handle is parsed from the URL.
- The client self-throttles ~0.5s between calls.
```
