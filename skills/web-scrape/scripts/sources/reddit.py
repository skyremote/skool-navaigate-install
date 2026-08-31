#!/usr/bin/env python3
"""Reddit search & thread extraction — routed through Composio's managed Reddit
toolkit, with the direct public `.json` endpoints as an automatic fallback.

Reddit blocks many outbound IPs (cloud / datacentre / CI) at the network edge,
which broke the direct `reddit.com/*.json` path. Composio runs the Reddit calls
on its own infrastructure behind a managed OAuth connection, so the IP block no
longer applies. We execute Composio's READ tools (search, subreddit listing,
comments) and map their responses onto this skill's existing output shape, so
the CLI surface and JSON payloads are unchanged — the research method and agents
need no edits.

Composio tools used (read-only):
  - REDDIT_SEARCH_ACROSS_SUBREDDITS   search posts across Reddit
  - REDDIT_RETRIEVE_REDDIT_POST       list posts from one subreddit
  - REDDIT_RETRIEVE_POST_COMMENTS     comments for a post (by base-36 id)

Execution contract (verified against the v3 API):
  POST https://backend.composio.dev/api/v3/tools/execute/{TOOL_SLUG}
  headers: x-api-key: <COMPOSIO_API_KEY>
  body:    {"user_id": "daniel", "arguments": {...}}
  -> {"data": {...}, "successful": bool, "error": str|None, "log_id": ...}

If Composio is unavailable, returns an auth error (no connected account for
user_id=<COMPOSIO_USER_ID>), or COMPOSIO_API_KEY is missing, the client transparently
falls back to the legacy direct public-JSON client below.

CLI (unchanged):
    python3 reddit.py search "<query>" [--subreddit X] [--time year] [--limit 15]
    python3 reddit.py subreddits "<topic>" [--limit 5]
    python3 reddit.py thread "<url>" [--comments 25]
    python3 reddit.py research "<query>" [--time year] [--threads 5] [--comments 25]
Add --json for the raw structured payload.
"""
import argparse
import os
import re
import sys

from _common import RateLimiter, die, emit, load_env, requests

# --------------------------------------------------------------- Composio -----
COMPOSIO_BASE = "https://backend.composio.dev/api/v3"
COMPOSIO_USER_ID = os.environ.get("COMPOSIO_USER_ID", os.environ.get("USER", "default"))
TOOL_SEARCH = "REDDIT_SEARCH_ACROSS_SUBREDDITS"
TOOL_SUBREDDIT_POSTS = "REDDIT_RETRIEVE_REDDIT_POST"
TOOL_POST_COMMENTS = "REDDIT_RETRIEVE_POST_COMMENTS"

# Substrings that mark a Composio "not authenticated / no connected account"
# style failure, as opposed to a real bug. When we see one of these we fall back
# to the direct public-JSON client rather than surfacing it as an error.
_AUTH_ERR_HINTS = (
    "no connected account",
    "not authenticated",
    "no connection",
    "connected account not found",
    "auth config",
    "please connect",
    "active connection",
    "nascent",
)


class ComposioUnavailable(Exception):
    """Raised when Composio can't serve the request (missing key, no connected
    account, auth error, transport failure) so the caller can fall back."""


class ComposioRedditClient:
    """Reddit search/extraction via Composio's managed Reddit toolkit.

    Maps Composio's READ tools onto the same method signatures and output shape
    as the legacy direct client, so callers (the CLI, the research pipeline,
    agents) don't change. Search and subreddit-listing tools return standard
    Reddit post objects which the shared `_parse_post` handles verbatim.

    Note on Composio's tool surface vs the direct API:
      - search has no per-subreddit restrict and no time filter (the `--time`
        / `--subreddit` flags on `search` degrade to no-ops here; the legacy
        client still honours them when it is in use);
      - the subreddit listing tool returns the subreddit's default (hot) listing
        with no sort/time controls, so `hot()` and `top()` both map to it;
      - comments come back without per-comment scores, so comment sorting/score
        degrade gracefully to 0 — bodies, authors and OP-flagging are intact.
    """

    def __init__(self, api_key):
        self.api_key = api_key
        # Composio runs the request on its own infra (not our IP), so we don't
        # need Reddit's 10 req/min self-throttle. A light limiter is courtesy.
        self._rl = RateLimiter(0.5)

    def _execute(self, tool_slug, arguments):
        """POST /tools/execute/{slug}. Returns the inner `data` dict on success;
        raises ComposioUnavailable on an auth/connection failure or transport
        error so the caller can fall back to the direct client."""
        self._rl.wait()
        url = f"{COMPOSIO_BASE}/tools/execute/{tool_slug}"
        body = {"user_id": COMPOSIO_USER_ID, "arguments": arguments}
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        try:
            resp = requests.post(url, json=body, headers=headers, timeout=60)
        except requests.exceptions.RequestException as e:
            raise ComposioUnavailable(f"Composio transport error: {e}")
        self._rl.mark()
        # 404 here would mean the tool slug is wrong (a real bug) — let it raise.
        if resp.status_code == 404:
            resp.raise_for_status()
        try:
            payload = resp.json()
        except ValueError:
            raise ComposioUnavailable(
                f"Composio returned non-JSON (HTTP {resp.status_code})")
        if resp.status_code >= 400 or not payload.get("successful", False):
            err = str(payload.get("error") or payload.get("message") or
                      f"HTTP {resp.status_code}")
            low = err.lower()
            if any(h in low for h in _AUTH_ERR_HINTS):
                raise ComposioUnavailable(f"Composio not connected: {err}")
            # Any other failure (rate limit, upstream Reddit hiccup, etc.) —
            # fall back rather than break the research run.
            raise ComposioUnavailable(f"Composio execute failed: {err}")
        return payload.get("data", {}) or {}

    # ---- mapped methods (same signatures/output as the legacy client) -------
    def search(self, query, sort="relevance", time_filter="year", limit=15, subreddit="all"):
        # Composio search is cross-subreddit with sorts relevance/new/top/comments.
        # `hot` (legacy default on some calls) maps to relevance; time is ignored.
        composio_sort = sort if sort in ("relevance", "new", "top", "comments") else "relevance"
        args = {
            "search_query": query,
            "sort": composio_sort,
            "limit": min(limit, 100),
            # If a specific subreddit was requested, fold it into the query so we
            # still bias results toward it (Composio search has no restrict_sr-to-X).
            "restrict_sr": False,
        }
        if subreddit and subreddit != "all":
            args["search_query"] = f"subreddit:{subreddit} {query}"
        data = self._execute(TOOL_SEARCH, args)
        children = (data.get("search_results", {}) or {}).get("data", {}).get("children", [])
        return [_parse_post(c.get("data", {})) for c in children if c.get("data")]

    def search_subreddit(self, subreddit, query, sort="relevance", time_filter="year", limit=10):
        return self.search(query, sort=sort, time_filter=time_filter, limit=limit, subreddit=subreddit)

    def find_subreddits(self, query, limit=5):
        """Composio's Reddit toolkit has no subreddit-discovery READ tool. Derive
        candidate subreddits from the subreddits that show up in a cross-Reddit
        search for the topic — good enough to feed the research pipeline."""
        posts = self.search(query, sort="relevance", limit=max(limit * 4, 20))
        seen, subs = set(), []
        for p in posts:
            name = p.get("subreddit")
            if name and name not in seen:
                seen.add(name)
                subs.append({
                    "name": name,
                    "subscribers": 0,        # not available via this tool
                    "description": "",
                    "url": f"/r/{name}",
                    "active_users": 0,
                })
            if len(subs) >= limit:
                break
        return subs

    def hot(self, subreddit="all", limit=10):
        return self._subreddit_listing(subreddit, limit)

    def top(self, subreddit="all", time_filter="week", limit=10):
        # Composio's listing tool has no top/time controls — same default listing.
        return self._subreddit_listing(subreddit, limit)

    def _subreddit_listing(self, subreddit, limit):
        if not subreddit or subreddit == "all":
            subreddit = "all"
        data = self._execute(TOOL_SUBREDDIT_POSTS, {
            "subreddit": subreddit,
            "size": min(limit, 100),
        })
        posts_list = data.get("posts_list", []) or []
        out = []
        for item in posts_list:
            pd = item.get("data") if isinstance(item, dict) and "data" in item else item
            if pd:
                out.append(_parse_post(pd))
        return out

    def extract_thread(self, url, comment_limit=25):
        """Full post body (from search/listing context) + top N comments via
        Composio. We resolve the post's base-36 id from the URL, fetch comments,
        and reconstruct the same thread shape. Post metadata beyond what the URL
        gives is best-effort: title/score etc. are populated by the caller's
        ranked post object in the research pipeline; for a bare `thread <url>`
        call we fill what we can and rely on the comments being the payload."""
        post_id = _extract_post_id(url)
        clean_url = _normalise_reddit_url(url)
        post = {
            "title": None,
            "subreddit": _subreddit_from_url(clean_url),
            "score": 0,
            "num_comments": 0,
            "url": clean_url,
            "created_utc": None,
            "selftext": "",
            "author": None,
            "upvote_ratio": None,
            "link_url": None,
        }
        if not post_id:
            return {"error": "Could not parse a Reddit post id from the URL", "url": url}
        data = self._execute(TOOL_POST_COMMENTS, {"article": post_id})
        raw = data.get("comments", []) or []
        comments = []
        for cd in _flatten_comments(raw):
            comments.append({
                "author": cd.get("author"),
                "body": cd.get("body", ""),
                "score": cd.get("score", cd.get("ups", 0)) or 0,
                "created_utc": cd.get("created_utc"),
                "is_op": bool(cd.get("is_submitter")),
                "controversiality": cd.get("controversiality", 0),
            })
        comments.sort(key=lambda x: x.get("score", 0), reverse=True)
        post["comments"] = comments[:comment_limit]
        post["comments_extracted"] = len(comments[:comment_limit])
        post["num_comments"] = max(post["num_comments"], len(comments))
        return post

    def research(self, query, time_filter="year", max_threads=5, max_comments=25,
                 subreddits=None, auto_detect_subreddits=True, max_subreddits=3):
        return _research(self, query, time_filter, max_threads, max_comments,
                         subreddits, auto_detect_subreddits, max_subreddits)


# --------------------------------------------------- direct (fallback) --------
class RedditClient:
    """Reddit search and extraction via public .json endpoints. No API key.

    Kept as the automatic fallback for when Composio is unavailable or not
    connected. NOTE: many outbound IPs are 403-blocked by Reddit at the network
    edge (cloud/datacentre/CI) — that is why Composio is now the primary path.
    """

    BASE = "https://www.reddit.com"
    # Hosts tried in order; some serve public JSON when www is blocked for an IP.
    HOSTS = ["https://www.reddit.com", "https://old.reddit.com"]
    # Browser-like UA: Reddit 403s many bot UAs outright. A real UA + spacing out
    # requests is the most reliable zero-auth path.
    HEADERS = {
        "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0 Safari/537.36"),
        "Accept": "application/json",
    }
    MIN_INTERVAL = 6.5  # 10 req/min unauthenticated cap

    def __init__(self):
        self._rl = RateLimiter(self.MIN_INTERVAL)

    def _get(self, url, params=None):
        """Rate-limited GET. On a 403/429 from www, retry on old.reddit.com.

        Reddit blocks some outbound IPs (datacentre / cloud) at the network
        edge with a 403 regardless of UA or rate. When that happens this raises
        with a clear message — it is an IP-reputation block, not a bug; run from
        a residential network or via a proxy.
        """
        self._rl.wait()
        last_exc = None
        for host in self.HOSTS:
            target = url.replace(self.BASE, host, 1) if url.startswith(self.BASE) else url
            resp = requests.get(target, params=params or {}, headers=self.HEADERS, timeout=30)
            self._rl.mark()
            if resp.status_code == 429:
                import time
                time.sleep(65)
                resp = requests.get(target, params=params or {}, headers=self.HEADERS, timeout=30)
                self._rl.mark()
            if resp.status_code == 403:
                last_exc = requests.exceptions.HTTPError(
                    f"403 Blocked by Reddit for {target} — this outbound IP is "
                    f"likely on Reddit's block list (common on cloud/datacentre "
                    f"networks). The client is correct; run from a residential "
                    f"network or proxy.", response=resp)
                continue  # try next host
            resp.raise_for_status()
            return resp.json()
        raise last_exc

    def search(self, query, sort="relevance", time_filter="year", limit=15, subreddit="all"):
        """Search r/all or a specific subreddit."""
        params = {
            "q": query,
            "sort": sort,
            "t": time_filter,
            "limit": min(limit, 100),
            "restrict_sr": "on" if subreddit != "all" else "off",
        }
        data = self._get(f"{self.BASE}/r/{subreddit}/search.json", params)
        return [_parse_post(p["data"]) for p in data.get("data", {}).get("children", [])]

    def search_subreddit(self, subreddit, query, sort="relevance", time_filter="year", limit=10):
        return self.search(query, sort=sort, time_filter=time_filter, limit=limit, subreddit=subreddit)

    def find_subreddits(self, query, limit=5):
        """Auto-detect relevant subreddits for a topic."""
        data = self._get(f"{self.BASE}/subreddits/search.json", params={"q": query, "limit": limit})
        return [
            {
                "name": s["data"].get("display_name"),
                "subscribers": s["data"].get("subscribers", 0),
                "description": (s["data"].get("public_description") or "")[:200],
                "url": f"/r/{s['data'].get('display_name')}",
                "active_users": s["data"].get("accounts_active", 0),
            }
            for s in data.get("data", {}).get("children", [])
        ]

    def hot(self, subreddit="all", limit=10):
        data = self._get(f"{self.BASE}/r/{subreddit}/hot.json", params={"limit": limit})
        return [_parse_post(p["data"]) for p in data.get("data", {}).get("children", [])]

    def top(self, subreddit="all", time_filter="week", limit=10):
        data = self._get(f"{self.BASE}/r/{subreddit}/top.json", params={"t": time_filter, "limit": limit})
        return [_parse_post(p["data"]) for p in data.get("data", {}).get("children", [])]

    def extract_thread(self, url, comment_limit=25):
        """Full post body + top N comments with scores."""
        clean_url = url.rstrip("/")
        if not clean_url.startswith("http"):
            clean_url = f"{self.BASE}{clean_url}"
        clean_url = re.sub(r"https?://(?:old\.|new\.)?reddit\.com", self.BASE, clean_url)
        json_url = clean_url + ".json"
        data = self._get(json_url, params={"limit": comment_limit, "sort": "best"})
        if not isinstance(data, list) or len(data) < 2:
            return {"error": "Unexpected response format", "url": url}
        post_data = data[0]["data"]["children"][0]["data"]
        post = _parse_post(post_data, full_text=True)
        comments = []
        for c in data[1]["data"]["children"]:
            if c.get("kind") == "t1":
                cd = c["data"]
                comments.append({
                    "author": cd.get("author"),
                    "body": cd.get("body", ""),
                    "score": cd.get("score", 0),
                    "created_utc": cd.get("created_utc"),
                    "is_op": cd.get("author") == post.get("author"),
                    "controversiality": cd.get("controversiality", 0),
                })
        comments.sort(key=lambda x: x.get("score", 0), reverse=True)
        post["comments"] = comments[:comment_limit]
        post["comments_extracted"] = len(comments[:comment_limit])
        return post

    def research(self, query, time_filter="year", max_threads=5, max_comments=25,
                 subreddits=None, auto_detect_subreddits=True, max_subreddits=3):
        return _research(self, query, time_filter, max_threads, max_comments,
                         subreddits, auto_detect_subreddits, max_subreddits)


# ------------------------------------------------- shared helpers -------------
def _parse_post(data, full_text=False):
    text_limit = 10000 if full_text else 300
    return {
        "title": data.get("title"),
        "subreddit": data.get("subreddit"),
        "score": data.get("score", 0),
        "num_comments": data.get("num_comments", 0),
        "url": f"https://reddit.com{data.get('permalink', '')}",
        "created_utc": data.get("created_utc"),
        "selftext": (data.get("selftext") or "")[:text_limit],
        "author": data.get("author"),
        "upvote_ratio": data.get("upvote_ratio"),
        "link_url": data.get("url") if not data.get("is_self") else None,
    }


def _normalise_reddit_url(url):
    clean = (url or "").rstrip("/")
    if not clean.startswith("http"):
        clean = f"https://www.reddit.com{clean}"
    return re.sub(r"https?://(?:www\.|old\.|new\.)?reddit\.com", "https://reddit.com", clean)


def _extract_post_id(url):
    """Pull the base-36 post id from a Reddit permalink/URL.

    e.g. https://reddit.com/r/X/comments/1taei9m/title/ -> 1taei9m
    Also accepts a bare id, or a `t3_<id>` fullname.
    """
    if not url:
        return None
    m = re.search(r"/comments/([a-z0-9]+)", url, re.IGNORECASE)
    if m:
        return m.group(1)
    m = re.match(r"^(?:t3_)?([a-z0-9]{4,})$", url.strip(), re.IGNORECASE)
    if m:
        return m.group(1)
    return None


def _subreddit_from_url(url):
    m = re.search(r"/r/([^/]+)", url or "")
    return m.group(1) if m else None


def _flatten_comments(raw):
    """Composio returns a nested comment tree (each has `replies`). Flatten it so
    the top-by-score selection sees every comment, matching the legacy client
    which sorted a flat list. Skips non-comment / 'more' placeholders."""
    out = []
    stack = list(raw or [])
    while stack:
        c = stack.pop()
        if not isinstance(c, dict):
            continue
        if c.get("body") is not None or c.get("author") is not None:
            out.append(c)
        replies = c.get("replies")
        if isinstance(replies, list):
            stack.extend(replies)
        elif isinstance(replies, dict):
            kids = replies.get("data", {}).get("children")
            if isinstance(kids, list):
                stack.extend([k.get("data", k) for k in kids if isinstance(k, dict)])
    return out


def _research(client, query, time_filter, max_threads, max_comments,
              subreddits, auto_detect_subreddits, max_subreddits):
    """Full pipeline shared by both clients: detect subs, search, rank, extract.

    Identical logic and output to the original `RedditClient.research`, lifted to
    a free function so the Composio and direct clients share it verbatim.
    """
    detected_subs = []
    all_posts = []
    if subreddits:
        detected_subs = [{"name": s} for s in subreddits]
    elif auto_detect_subreddits:
        detected_subs = client.find_subreddits(query, limit=max_subreddits + 2)
        detected_subs = [s for s in detected_subs if s.get("subscribers", 0) >= 0][:max_subreddits]
    sub_names = [s["name"] for s in detected_subs]
    all_posts.extend(client.search(query, sort="relevance", time_filter=time_filter, limit=15))
    for sub_name in sub_names:
        try:
            all_posts.extend(client.search_subreddit(sub_name, query, time_filter=time_filter, limit=10))
        except Exception:
            pass
    seen = set()
    unique = []
    for p in all_posts:
        if p["url"] not in seen:
            seen.add(p["url"])
            unique.append(p)
    unique.sort(key=lambda p: p.get("score", 0) * 0.6 + p.get("num_comments", 0) * 0.4, reverse=True)
    threads = []
    for post in unique[:max_threads]:
        try:
            thread = client.extract_thread(post["url"], comment_limit=max_comments)
            # Composio's thread tool returns comments only; backfill post metadata
            # from the ranked search result so titles/scores are never blank.
            if isinstance(thread, dict) and not thread.get("error"):
                for k in ("title", "score", "num_comments", "author", "selftext",
                          "upvote_ratio", "created_utc", "subreddit"):
                    if not thread.get(k) and post.get(k):
                        thread[k] = post[k]
            threads.append(thread)
        except Exception as e:
            post["comments"] = []
            post["comments_extracted"] = 0
            post["extraction_error"] = str(e)
            threads.append(post)
    return {
        "query": query,
        "time_filter": time_filter,
        "subreddits_searched": ["all"] + sub_names,
        "subreddits_detected": detected_subs,
        "posts_found": len(unique),
        "threads_extracted": len(threads),
        "threads": threads,
    }


# ------------------------------------------------- client selection -----------
def _composio_api_key():
    load_env()
    return os.environ.get("COMPOSIO_API_KEY", "").strip()


class RedditSource:
    """Front door: try Composio first, fall back to the direct client on any
    Composio-unavailable condition (missing key, no connected account, auth
    error, transport failure). Each method delegates and degrades the same way,
    so the CLI never has to care which path served the request."""

    def __init__(self):
        key = _composio_api_key()
        self._composio = ComposioRedditClient(key) if key else None
        self._direct = None  # lazily constructed only if we actually fall back

    def _fallback(self):
        if self._direct is None:
            self._direct = RedditClient()
        return self._direct

    def _via(self, method, *args, **kwargs):
        if self._composio is not None:
            try:
                return getattr(self._composio, method)(*args, **kwargs)
            except ComposioUnavailable:
                # Drop to direct for this and subsequent calls in the process.
                self._composio = None
        return getattr(self._fallback(), method)(*args, **kwargs)

    def search(self, *a, **k):
        return self._via("search", *a, **k)

    def search_subreddit(self, *a, **k):
        return self._via("search_subreddit", *a, **k)

    def find_subreddits(self, *a, **k):
        return self._via("find_subreddits", *a, **k)

    def hot(self, *a, **k):
        return self._via("hot", *a, **k)

    def top(self, *a, **k):
        return self._via("top", *a, **k)

    def extract_thread(self, *a, **k):
        return self._via("extract_thread", *a, **k)

    def research(self, *a, **k):
        # research() orchestrates many sub-calls; run the whole pipeline on the
        # chosen client so a mid-pipeline fallback doesn't mix shapes.
        if self._composio is not None:
            try:
                return self._composio.research(*a, **k)
            except ComposioUnavailable:
                self._composio = None
        return self._fallback().research(*a, **k)


# ---------------------------------------------------------------- CLI --------
def _print_posts(posts):
    if not posts:
        print("No posts.")
        return
    for p in posts:
        print(f"[{p['score']} pts | {p['num_comments']} comments] r/{p['subreddit']} — {p['title']}")
        print(f"   {p['url']}")
        if p.get("selftext"):
            print("   " + " ".join(p["selftext"][:200].split()))
        print()


def cmd_search(args, c):
    posts = c.search(args.query, sort=args.sort, time_filter=args.time,
                     limit=args.limit, subreddit=args.subreddit)
    if emit({"query": args.query, "posts": posts}, args.json):
        return
    _print_posts(posts)


def cmd_subreddits(args, c):
    subs = c.find_subreddits(args.topic, limit=args.limit)
    if emit({"topic": args.topic, "subreddits": subs}, args.json):
        return
    for s in subs:
        print(f"r/{s['name']} — {s['subscribers']:,} subs — {s['description']}")


def cmd_thread(args, c):
    thread = c.extract_thread(args.url, comment_limit=args.comments)
    if emit(thread, args.json):
        return
    if thread.get("error"):
        die(thread["error"])
    print(f"# {thread['title']}  [{thread['score']} pts] r/{thread['subreddit']}")
    print(f"{thread['url']}\n")
    if thread.get("selftext"):
        print(thread["selftext"][:2000] + "\n")
    print(f"--- Top {thread.get('comments_extracted', 0)} comments ---")
    for cm in thread.get("comments", []):
        flag = " (OP)" if cm.get("is_op") else ""
        print(f"[{cm['score']} pts] u/{cm['author']}{flag}: {cm['body'][:300]}")


def cmd_research(args, c):
    result = c.research(args.query, time_filter=args.time, max_threads=args.threads,
                        max_comments=args.comments)
    if emit(result, args.json):
        return
    print(f"Searched: {result['subreddits_searched']}")
    print(f"Found {result['posts_found']} posts, extracted {result['threads_extracted']} threads\n")
    for t in result["threads"]:
        print(f"[{t.get('score', 0)} pts | {t.get('comments_extracted', 0)} comments] "
              f"r/{t.get('subreddit')} — {t.get('title')}")
        print(f"   {t.get('url')}")
        for cm in t.get("comments", [])[:3]:
            print(f"     [{cm['score']}] u/{cm['author']}: {cm['body'][:120]}")
        print()


def build_parser():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", default=argparse.SUPPRESS,
                        help="Print the raw structured payload.")
    p = argparse.ArgumentParser(prog="reddit.py",
                                description="Reddit research via Composio's managed toolkit "
                                            "(direct public JSON as fallback).")
    p.add_argument("--json", action="store_true", help="Print the raw structured payload.")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("search", parents=[common], help="Search posts across Reddit or one subreddit.")
    s.add_argument("query")
    s.add_argument("--subreddit", default="all")
    s.add_argument("--sort", default="relevance", choices=["relevance", "hot", "top", "new", "comments"])
    s.add_argument("--time", default="year", choices=["hour", "day", "week", "month", "year", "all"])
    s.add_argument("--limit", type=int, default=15)
    s.set_defaults(func=cmd_search)

    sr = sub.add_parser("subreddits", parents=[common], help="Auto-detect relevant subreddits for a topic.")
    sr.add_argument("topic")
    sr.add_argument("--limit", type=int, default=5)
    sr.set_defaults(func=cmd_subreddits)

    t = sub.add_parser("thread", parents=[common], help="Extract a thread: post body + top comments.")
    t.add_argument("url")
    t.add_argument("--comments", type=int, default=25)
    t.set_defaults(func=cmd_thread)

    r = sub.add_parser("research", parents=[common],
                       help="Full pipeline: detect subs, search, rank, extract threads.")
    r.add_argument("query")
    r.add_argument("--time", default="year", choices=["hour", "day", "week", "month", "year", "all"])
    r.add_argument("--threads", type=int, default=5)
    r.add_argument("--comments", type=int, default=25)
    r.set_defaults(func=cmd_research)
    return p


def main():
    args = build_parser().parse_args()
    if not hasattr(args, "json"):
        args.json = False
    c = RedditSource()
    try:
        args.func(args, c)
    except requests.exceptions.RequestException as e:
        die(f"Reddit request failed: {e}")


if __name__ == "__main__":
    main()
