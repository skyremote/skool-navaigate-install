# Research sources — what is already on the shelf

Every research source we used to hand out as a separate zip is already wired
into `/web-scrape`. There is no separate research-sources module to install.
Pick the source, run the command, and their key goes in `~/.claude/.env`.

All commands run from the plugin folder (or `~/.claude/skills/web-scrape/`
once `install.sh` has linked it).

| Source | What it is good for | Key | Command |
|---|---|---|---|
| Open web (Exa) | finding pages by meaning, grounded answers | `EXA_API_KEY` | `python3 scripts/webscrape.py search "<query>"` / `answer "<question>"` |
| Open web (Firecrawl) | reading one JS-heavy page as markdown | `FIRECRAWL_API_KEY` | `python3 scripts/webscrape.py scrape "<url>"` |
| Reddit | what practitioners actually say, what broke, what they paid | none (Composio optional: `COMPOSIO_API_KEY`) | `python3 scripts/sources/reddit.py research "<topic>" --threads 5` / `thread "<url>"` / `subreddits "<topic>"` |
| Academic (OpenAlex + Unpaywall) | papers, citation counts, free PDFs | none (`OPENALEX_EMAIL` optional) | `python3 scripts/sources/academic.py search "<topic>" --from-year 2024` / `paper <doi>` / `citations <id>` / `pdf <doi>` |
| Substack | named-author long-form, operator essays | reuses Exa / Firecrawl keys | `python3 scripts/sources/substack.py search "<topic>"` / `archive <publication>` / `post <publication> <slug>` / `publications "<topic>"` |
| X / Twitter (xAI X Search) | real-time X sentiment, posts from named handles | `XAI_API_KEY` (paid, dormant until the xAI account has credit) | `python3 scripts/sources/xsearch.py search "<query>" --max-results 5` |
| Supadata | YouTube search, transcripts from YouTube / TikTok / Instagram / X / Facebook, post metadata | `SUPADATA_API_KEY` (paid, credit-metered) | `python3 scripts/sources/supadata.py search "<query>" --limit 10` / `transcript "<url>" --lang en` / `metadata "<url>"` / `research "<topic>" --videos 3` |

Every source also has a `research` subcommand that returns the same bundle
shape, so `/deep-research` can run them side by side. Add `--json` for the raw
payload.

## Where each one sits on the shelf

- `/web-scrape` — the helper and all the source clients above.
- `/transcripts` — Supadata transcript and search only, for when they paste a video URL.
- `/podcasts` — Exa/Firecrawl for the wide net, Supadata for the words.
- `/deep-research` — the multi-source pass over all of them (`references/research-method.md`).

## Supadata endpoints we have not wired

Supadata's API also does channel stats, channel and playlist video lists,
batch transcripts, translated transcripts, web scrape/map/crawl and AI
extraction from a video. None of those are in `scripts/sources/supadata.py`
today. If they need one, that is a `/new-capability` job: the client is one
file, `x-api-key` header, base `https://api.supadata.ai/v1`, docs at
supadata.ai. Do not build a second Supadata client.

## Rules

- Keys are theirs, in `~/.claude/.env`. Missing key: say which one and stop.
- Supadata and X Search cost credits. Keep `research` small on those two.
- Reddit's direct public JSON can 403 on cloud networks; Composio is the
  route that does not.
