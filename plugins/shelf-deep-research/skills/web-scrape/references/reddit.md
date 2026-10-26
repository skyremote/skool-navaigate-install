# Reddit (via Composio managed toolkit)

Reddit research now routes through **Composio's managed Reddit toolkit**
(managed OAuth, read-only). Composio runs the Reddit calls on its **own
infrastructure**, so the IP-reputation block that 403s our outbound IP on the
direct path no longer applies. The legacy direct public-`.json` client is kept
as an **automatic fallback** (see below). The CLI surface and JSON output shape
are unchanged — agents and the research method need no edits.

Use Reddit when you want **practitioner sentiment and lived experience**: what
real users say worked, what broke, pricing they actually paid, tools they dropped.
Low upvotes does not mean low value — a 0-score comment with version numbers and a
specific failure mode can be the best signal in a run.

## How it routes

`scripts/sources/reddit.py` tries Composio first and falls back to the direct
public-JSON client only if Composio is unavailable:

1. **Composio (primary).** Reads `COMPOSIO_API_KEY` from `~/.claude/.env`
   (same loader as the other scripts), and executes Composio's read tools with
   `user_id from COMPOSIO_USER_ID`:
   - `REDDIT_SEARCH_ACROSS_SUBREDDITS` — search posts across Reddit
   - `REDDIT_RETRIEVE_REDDIT_POST` — list posts from one subreddit
   - `REDDIT_RETRIEVE_POST_COMMENTS` — comments for a post (by base-36 id)
2. **Direct public JSON (fallback).** Triggers automatically when the key is
   missing, there's no connected account for `user_id from COMPOSIO_USER_ID`, Composio
   returns an auth/connection error, or the transport fails. This is the old
   `reddit.com/*.json` client (browser UA, 6.5s self-throttle, `old.reddit.com`
   retry) — still subject to Reddit's IP block on cloud/datacentre networks.

Execution contract (Composio v3, verified):

```
POST https://backend.composio.dev/api/v3/tools/execute/{TOOL_SLUG}
headers: x-api-key: <COMPOSIO_API_KEY>
body:    {"user_id": "daniel", "arguments": { ... }}
-> {"data": { ... }, "successful": bool, "error": str|None, "log_id": ...}
```

## CLI (unchanged)

```bash
S=~/.claude/skills/web-scraping/scripts/sources/reddit.py

# Search r/all or one subreddit
python3 $S search "RAG evaluation pipeline" --subreddit MachineLearning --time year --limit 15

# Auto-detect relevant subreddits for a topic
python3 $S subreddits "AI automation agency pricing" --limit 5

# Extract a full thread: post body + top comments (scored, OP-flagged)
python3 $S thread "https://reddit.com/r/MachineLearning/comments/.../" --comments 25

# Full pipeline: detect subs -> search -> rank by score+comments -> extract top threads
python3 $S research "AI coding agents in production" --time year --threads 5 --comments 25
```

Add `--json` (works before or after the subcommand) for the raw structured payload.

`--time`: `hour day week month year all`. `--sort` on search:
`relevance hot top new comments`.

## What you get

`research` returns `{query, subreddits_searched, subreddits_detected, posts_found,
threads_extracted, threads:[...]}`. Each thread has `title, subreddit, score,
num_comments, author, selftext, url, upvote_ratio, comments_extracted, comments:[...]`
and each comment has `author, body, score, is_op, controversiality`.

## Composio path — behaviour notes

The managed toolkit's read surface is narrower than Reddit's raw API, so a few
flags degrade gracefully on the Composio path (the direct fallback still honours
them when it is in use):

- **`search`** is cross-Reddit. `--subreddit X` is folded into the query as
  `subreddit:X <query>` to bias results; `--time` is ignored (no time filter on
  the search tool); `--sort hot` maps to `relevance`.
- **`subreddits`** (discovery) has no dedicated Composio tool — relevant
  subreddits are derived from the subreddits that appear in a topic search, so
  `subscribers`/`active_users` come back as `0`.
- **`thread`** comments arrive without per-comment scores, so comment `score`
  is `0` and sorting by score is a no-op (bodies, authors and OP-flagging are
  intact). A bare `thread <url>` call returns comments with minimal post
  metadata; inside `research`, the post's title/score/subreddit are backfilled
  from the ranked search result so nothing is blank.
- `hot` and `top` both map to the subreddit's default listing (the listing tool
  has no top/time controls).

## Gotchas

- **Composio "no connected account / not authenticated"** → the
  `user_id from COMPOSIO_USER_ID` Reddit connection hasn't been authorised. The client falls
  back to the direct path automatically; to use Composio, authorise the Reddit
  connection in Composio for that user.
- **Direct fallback 403 "Blocked"** = the **outbound IP is on Reddit's block
  list** (common on cloud / datacentre / CI networks). This is exactly why
  Composio is now primary. The fallback client is correct; a hard network block
  can't be coded around.
- Reddit is **not** reachable via our Firecrawl path (Firecrawl explicitly
  refuses the site), so Composio is the reliable route.
- The Composio path runs off Composio's infra (no Reddit self-throttle needed);
  a `research` call is fast. The direct fallback is rate-limited (~40-50s per
  `research`) by design.
