# Exa reference

Canonical source of truth (fetch if anything here contradicts live behaviour,
and report drift to the user):
https://exa.ai/docs/reference/search-api-guide-for-coding-agents

REST basics (what the helper uses):
- `POST https://api.exa.ai/search`
- Auth header: `x-api-key: <EXA_API_KEY>`
- Sibling endpoints: `POST /contents`, `POST /answer`

## Contents

- [Search types](#search-types)
- [Content configuration](#content-configuration)
- [Structured output (outputSchema)](#structured-output-outputschema)
- [Domain & date filtering](#domain--date-filtering)
- [Content freshness (maxAgeHours)](#content-freshness-maxagehours)
- [/contents and /answer](#contents-and-answer)
- [Troubleshooting](#troubleshooting)

## Search types

`type` ∈ `auto | fast | instant | deep-lite | deep | deep-reasoning`.

| Type | Best for | Approx latency | Depth |
|------|----------|----------------|-------|
| `auto` | Most queries — balanced relevance and speed | ~1 s | Smart (default) |
| `fast` | Latency-sensitive, still good relevance | ~450 ms | Basic |
| `instant` | Chat, voice, autocomplete, quick lookups | ~250 ms | Basic |
| `deep-lite` | Cheaper synthesis when full deep is overkill | ~4 s | Deep |
| `deep` | Research, enrichment, thorough results | 4–15 s | Deep |
| `deep-reasoning` | Complex, multi-step, hard synthesis | 12–40 s | Deepest |

Synthesis (`outputSchema`) and forced livecrawls (`maxAgeHours: 0`) stack on
top of the base latency. Raise the helper's `--timeout` for deep types.

`additionalQueries` is only valid on `deep-lite`/`deep`/`deep-reasoning`, to
force explicit query angles instead of relying on automatic expansion.

## Content configuration

Pick **one** of `text`, `highlights`, `summary` by default; combining all
three at the start of a project is usually an antipattern. On `/search` these
nest under `contents`; on `/contents` they are top-level.

| Mode | Config | Best for |
|------|--------|----------|
| Highlights | `highlights: true` | Token-efficient excerpts (default for agents) |
| Text | `text: {maxCharacters: 20000}` | Full extraction, RAG |
| Summary | `summary: true` or `{query: "..."}` | LLM-written per-result summary |

Tuning knobs:
- `text.verbosity` — `"compact"` (default, main content only) or `"full"`.
- `text.includeHtmlTags` — keep HTML structure (code blocks, tables).
- `text.maxCharacters` — always set this to control token cost.
- `summary.query` — bias the summary toward a specific question; `summary.schema`
  gives per-result structured output.

Case: raw JSON / JS SDK use camelCase (`maxCharacters`); the Python SDK uses
snake_case (`max_characters`). The helper sends camelCase JSON directly.

## Structured output (outputSchema)

Works on **every** search type (`auto` is fine; deep variants synthesise
better). Pass a JSON schema; Exa returns the synthesised answer in
`output.content` plus field-level citations in `output.grounding`. Pair with
`systemPrompt` for source preferences and dedupe behaviour.

Schema limits: keys `type`, `description`, `required`, `properties`, `items`;
max nesting depth 2; max 10 total properties. Do **not** add citation or
confidence fields — grounding is returned automatically.

The helper exposes this via `--output-schema '<json>'` and `--system-prompt`.
Use `--json` to see `output.content` and `output.grounding`.

Response shape with `outputSchema`:
```json
{
  "output": {
    "content": { "...": "matches your schema" },
    "grounding": [
      {"field": "companies[0].name",
       "citations": [{"url": "https://…", "title": "Source"}],
       "confidence": "high"}
    ]
  }
}
```

When to use: enrichment workflows, data pipelines, grounded answers where you
want both retrieval control and synthesis. For question-first UIs where you
don't need raw results, `/answer` is simpler.

## Domain & date filtering

Usually unnecessary — neural search finds relevant results without it. Use to
target authoritative sources or exclude low-quality domains.

- `includeDomains` / `excludeDomains` (string arrays, max 1200 each). Can be
  combined to include a broad domain but exclude a subdomain, e.g. include
  `vercel.com`, exclude `community.vercel.com`.
- `startPublishedDate` / `endPublishedDate` (ISO 8601).
- Note: `category: "company" | "people"` does not support `excludeDomains` or
  date filters (→ 400).

## Content freshness (maxAgeHours)

Max acceptable age (hours) for cached content; older → Exa livecrawls.

| Value | Behaviour |
|-------|-----------|
| `24` | Use cache if <24 h old, else livecrawl |
| `1` | Near real-time |
| `0` | Always livecrawl (ignore cache) |
| `-1` | Never livecrawl (cache only — fastest) |
| omit | Default: livecrawl as fallback if no cache (**recommended**) |

Cached data is fine for historical/educational topics. Helper flag:
`--max-age-hours N` (sent inside `contents` on search, top-level on contents).

## /contents and /answer

- `POST /contents` — clean content for URLs you already have (DB, user input,
  RSS). Content options are **top-level** here (`text`, `highlights`,
  `maxAgeHours`), not nested. Helper: `contents <url...>`.
- `POST /answer` — grounded answer with citations for a question-first flow.
  Helper: `answer "<question>"`.

## Troubleshooting

- **Irrelevant results** → try `type auto`, then `deep`; use singular,
  specific queries.
- **Need structured data** → `--output-schema` (+ `--system-prompt`).
- **Too slow** → `type fast`/`instant`, fewer `--num`, skip contents if you
  only need URLs.
- **No results** → drop filters (date/domain), simplify the query, use `auto`.

Deprecated / non-existent (never send these):
`useAutoprompt`, `numSentences`, `highlightsPerUrl`, `tokensNum`,
`livecrawl: "always"` (use `maxAgeHours: 0`), `includeUrls`/`excludeUrls`
(use `includeDomains`/`excludeDomains`).
