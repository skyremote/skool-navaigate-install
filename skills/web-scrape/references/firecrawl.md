# Firecrawl reference (REST v2)

Canonical source of truth (fetch if anything here contradicts live behaviour,
and report drift to the user): https://docs.firecrawl.dev

REST basics (what the helper uses):
- Base URL: `https://api.firecrawl.dev/v2`
- Auth header: `Authorization: Bearer <FIRECRAWL_API_KEY>` (keys start `fc-`)
- Endpoints used here: `POST /scrape`, `POST /search`

Firecrawl runs a real headless browser, so it executes JavaScript and returns
content a plain HTTP fetch would miss. That is the whole reason to reach for
it over a normal fetch: SPAs, client-rendered dashboards, infinite scroll,
content injected after load.

## Contents

- [Scrape](#scrape)
- [Interaction with actions](#interaction-with-actions)
- [Search](#search)
- [Response shape](#response-shape)
- [Troubleshooting](#troubleshooting)
- [Optional: the Firecrawl CLI](#optional-the-firecrawl-cli)

## Scrape

`POST /scrape` — render one URL and return clean content.

Request body fields:
- `url` (string, required).
- `formats` (array) — any of `markdown`, `html`, `rawHtml`, `links`,
  `screenshot`, `json`, `summary`, `highlights`. Default the helper sends
  `["markdown"]`.
- `onlyMainContent` (bool, default `true`) — strips nav/header/footer/banners.
  The helper's `--full` flag sets this to `false`.
- `waitFor` (int ms, default `0`) — delay before capture; raise for slow JS
  hydration. Helper: `--wait`.
- `timeout` (int ms, default `60000`, range `1000`–`300000`) — Firecrawl-side
  timeout. Helper: `--fc-timeout`.

Helper examples:
```bash
python3 .../webscrape.py scrape "https://example.com/app"
python3 .../webscrape.py scrape "https://example.com/app" --wait 3000 --full
python3 .../webscrape.py scrape "https://example.com" --formats markdown links
```

## Interaction with actions

When the content only appears after clicks, typing, scrolling, or login,
add an `actions` array to the `/scrape` body. This is **not** wired into the
helper's flags — call the API directly (e.g. with a short `requests` snippet)
or extend `cmd_scrape`. Supported action types: `click`, `write`, `scroll`,
`screenshot`, `wait`, `press`, `executeJavascript`.

```json
{
  "url": "https://example.com/login",
  "formats": ["markdown"],
  "actions": [
    {"type": "write", "selector": "#email", "text": "user@example.com"},
    {"type": "click", "selector": "button[type=submit]"},
    {"type": "wait", "milliseconds": 2000}
  ]
}
```

For heavy interactive flows, the project's dedicated browser-automation
tooling may be a better fit than scripting actions by hand.

## Search

`POST /search` — Firecrawl's own web search; optionally scrape each hit in
the same call by sending `scrapeOptions`.

```bash
python3 .../webscrape.py crawl-search "structured logging best practices" --num 5
python3 .../webscrape.py crawl-search "structured logging best practices" --scrape
```

Prefer Exa `search` for true semantic discovery; use this when you want
Firecrawl's index plus inline scraping of the results.

## Response shape

`/scrape` returns `{ "success": true, "data": { ... } }`. Content lives under
`data` by requested format:
- `data.markdown` — clean markdown (what the helper prints by default)
- `data.html`, `data.rawHtml`, `data.links`, `data.screenshot`
- `data.metadata` — `title`, `description`, `sourceURL`, `statusCode`, etc.

Use the helper's `--json` to see the full envelope.

## Troubleshooting

- **Empty / partial markdown on a dynamic page** → add `--wait 2000`–`5000`
  so JS finishes rendering before capture.
- **Missing nav/sidebar you actually wanted** → `--full` (turns off
  `onlyMainContent`).
- **Timeouts on heavy pages** → raise `--fc-timeout` (ms, up to 300000) and
  the helper's `--timeout` (seconds) accordingly.
- **`401 Unauthorized`** → `FIRECRAWL_API_KEY` missing/invalid in
  `~/.claude/.env`; keys begin with `fc-`.
- **Need clicks/forms/login** → use `actions` (above) or browser tooling.

## Optional: the Firecrawl CLI

This skill deliberately uses REST only — zero install, deterministic. If you
later want the richer CLI (`firecrawl search|scrape|interact|crawl|map|ask`),
install it once with `npx -y firecrawl-cli@latest init --all --browser`
(opens a browser sign-in). It is not required for anything in this skill.
