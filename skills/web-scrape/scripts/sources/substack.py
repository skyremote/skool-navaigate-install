#!/usr/bin/env python3
"""Substack search & full-article extraction.

Two layers:
  Discovery — find Substack posts on a topic. Uses THIS skill's webscrape.py:
    Exa first (semantic, domain-filtered to substack.com), Firecrawl as fallback.
  Extraction — pull full post body + metadata via Substack's public /api/v1
    endpoints (undocumented but unauthenticated; archive + post content).

Client adapted from the AAA Deep Research module's Substack client. The only
change: discovery routes through our webscrape.py rather than a `firecrawl` CLI.

CLI:
    python3 substack.py search "<query>" [--limit 10]
    python3 substack.py archive "<publication>" [--limit 12] [--sort new|top]
    python3 substack.py post "<publication>" "<slug>" [--html]
    python3 substack.py publications "<topic>" [--limit 10]
    python3 substack.py research "<query>" [--posts 5] [--limit 10]
Add --json for the raw structured payload.
"""
import argparse
import json
import re
import subprocess
import sys
import time
from html import unescape

from _common import WEBSCRAPE, RateLimiter, die, emit, requests

_RL = RateLimiter(2.0)  # be gentle on Substack's API


def _strip_html(html):
    if not html:
        return ""
    text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r"</p>", "\n\n", text)
    text = re.sub(r"</h[1-6]>", "\n\n", text)
    text = re.sub(r"</li>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = unescape(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


class SubstackClient:
    """Discovery via webscrape.py (Exa/Firecrawl) + extraction via Substack API."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"),
            "Accept": "application/json",
        })

    # --- Layer 1: Discovery (via webscrape.py) ---
    def search(self, query, limit=10):
        """Find Substack posts on a topic. Exa semantic search, Firecrawl fallback."""
        results = self._search_via_exa(query, limit)
        if not results:
            results = self._search_via_firecrawl(query, limit)
        return results

    def _run_webscrape(self, args):
        try:
            res = subprocess.run([sys.executable, str(WEBSCRAPE)] + args + ["--json"],
                                 capture_output=True, text=True, timeout=120)
            if res.returncode != 0:
                return None
            return json.loads(res.stdout)
        except Exception:
            return None

    def _search_via_exa(self, query, limit):
        data = self._run_webscrape(["search", query, "--num", str(limit),
                                    "--include-domains", "substack.com"])
        if not data:
            return []
        out = []
        for r in data.get("results", [])[:limit]:
            url = r.get("url", "")
            pub, slug = self._parse_substack_url(url)
            out.append({
                "title": r.get("title", ""),
                "url": url,
                "description": (r.get("summary") or
                                (" ".join(r.get("highlights", [])[:1]) if r.get("highlights") else "")),
                "publication": pub,
                "slug": slug,
            })
        return [r for r in out if r["url"]]

    def _search_via_firecrawl(self, query, limit):
        data = self._run_webscrape(["crawl-search", f"{query} site:substack.com",
                                    "--num", str(limit)])
        if not data:
            return []
        web = (data.get("data") or {})
        if isinstance(web, dict):
            web = web.get("web", []) or data.get("data", [])
        if not isinstance(web, list):
            web = []
        out = []
        for item in web[:limit]:
            url = item.get("url", "")
            pub, slug = self._parse_substack_url(url)
            out.append({
                "title": item.get("title", ""),
                "url": url,
                "description": item.get("description", ""),
                "publication": pub,
                "slug": slug,
            })
        return [r for r in out if r["url"]]

    def _parse_substack_url(self, url):
        m = re.search(r"(?:https?://)?([^./]+)\.substack\.com/p/([^/?#]+)", url)
        if m:
            return m.group(1), m.group(2)
        m = re.search(r"open\.substack\.com/pub/([^/]+)/p/([^/?#]+)", url)
        if m:
            return m.group(1), m.group(2)
        slug, pub = "", ""
        m = re.search(r"/p/([^/?#]+)", url)
        if m:
            slug = m.group(1)
            dm = re.search(r"https?://(?:www\.)?([^./]+)", url)
            if dm:
                pub = dm.group(1)
        return pub, slug

    # --- Layer 2: Substack API (extraction) ---
    def _api_get(self, base_url, path, params=None):
        _RL.wait()
        url = f"https://{base_url}/api/v1{path}"
        try:
            resp = self.session.get(url, params=params or {}, timeout=15)
            if resp.status_code == 429:
                time.sleep(10)
                resp = self.session.get(url, params=params or {}, timeout=15)
            if resp.status_code != 200:
                return None
            return resp.json()
        except Exception:
            return None

    def list_posts(self, publication, limit=12, offset=0, sort="new"):
        for base in [f"{publication}.substack.com", f"www.{publication}.com", publication]:
            data = self._api_get(base, "/archive", {"sort": sort, "limit": limit, "offset": offset})
            if data and isinstance(data, list):
                return [
                    {
                        "title": p.get("title", ""),
                        "slug": p.get("slug", ""),
                        "date": p.get("post_date", ""),
                        "wordcount": p.get("wordcount", 0),
                        "reactions": p.get("reactions", {}),
                        "subtitle": p.get("subtitle", ""),
                        "audience": p.get("audience", ""),
                        "comment_count": p.get("comment_count", 0),
                        "publication": publication,
                        "url": f"https://{base}/p/{p.get('slug', '')}",
                    }
                    for p in data
                ]
        return []

    def get_post(self, publication, slug, as_text=True):
        for base in [f"{publication}.substack.com", f"www.{publication}.com", publication]:
            data = self._api_get(base, f"/posts/{slug}")
            if data and isinstance(data, dict) and data.get("title"):
                body_html = data.get("body_html", "") or ""
                body = _strip_html(body_html) if as_text else body_html
                return {
                    "title": data.get("title", ""),
                    "slug": slug,
                    "date": data.get("post_date", ""),
                    "body": body,
                    "body_length": len(body),
                    "wordcount": data.get("wordcount", 0),
                    "reactions": data.get("reactions", {}),
                    "comment_count": data.get("comment_count", 0),
                    "subtitle": data.get("subtitle", ""),
                    "audience": data.get("audience", ""),
                    "publication": publication,
                    "url": f"https://{base}/p/{slug}",
                    "canonical_url": data.get("canonical_url", ""),
                }
        return None

    def discover_publications(self, query, limit=10):
        results = self.search(query, limit=limit)
        pubs = {}
        for r in results:
            pub = r.get("publication", "")
            if pub and pub not in pubs and pub != "open":
                pubs[pub] = {"publication": pub, "url": f"https://{pub}.substack.com",
                             "found_via": r.get("title", "")}
        return list(pubs.values())

    def research(self, query, max_posts=5, search_limit=10):
        search_results = self.search(query, limit=search_limit)
        extracted = []
        for result in search_results[:max_posts]:
            pub, slug = result.get("publication", ""), result.get("slug", "")
            if not pub or not slug:
                continue
            post = self.get_post(pub, slug)
            if post and post.get("body"):
                extracted.append(post)
        return {
            "query": query,
            "search_results_count": len(search_results),
            "search_results": search_results,
            "extracted_count": len(extracted),
            "extracted_posts": extracted,
        }


# ---------------------------------------------------------------- CLI --------
def cmd_search(args, c):
    results = c.search(args.query, limit=args.limit)
    if emit({"query": args.query, "results": results}, args.json):
        return
    if not results:
        print("No Substack posts found.")
        return
    for r in results:
        print(f"{r['title']}  ({r['publication']}/{r['slug']})")
        print(f"   {r['url']}")
        if r.get("description"):
            print("   " + " ".join(r["description"][:200].split()))
        print()


def cmd_archive(args, c):
    posts = c.list_posts(args.publication, limit=args.limit, sort=args.sort)
    if emit({"publication": args.publication, "posts": posts}, args.json):
        return
    if not posts:
        print("No posts (publication not found or API blocked).")
        return
    for p in posts:
        print(f"[{p['date'][:10]}] {p['title']} ({p['wordcount']} words) — {p['url']}")


def cmd_post(args, c):
    post = c.get_post(args.publication, args.slug, as_text=not args.html)
    if not post:
        die("Post not found.")
    if emit(post, args.json):
        return
    print(f"# {post['title']}")
    if post.get("subtitle"):
        print(post["subtitle"])
    print(f"{post['publication']} — {post['date'][:10]} — {post['wordcount']} words")
    print(f"{post['url']}\n")
    print(post["body"][:5000])


def cmd_publications(args, c):
    pubs = c.discover_publications(args.topic, limit=args.limit)
    if emit({"topic": args.topic, "publications": pubs}, args.json):
        return
    for p in pubs:
        print(f"{p['publication']} — {p['url']}  (via: {p['found_via']})")


def cmd_research(args, c):
    result = c.research(args.query, max_posts=args.posts, search_limit=args.limit)
    if emit(result, args.json):
        return
    print(f"Discovered {result['search_results_count']}, extracted {result['extracted_count']}\n")
    for p in result["extracted_posts"]:
        print(f"# {p['title']} ({p['publication']}, {p['wordcount']} words)")
        print(f"   {p['url']}")
        print("   " + " ".join(p["body"][:240].split()))
        print()


def build_parser():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", default=argparse.SUPPRESS,
                        help="Print the raw structured payload.")
    p = argparse.ArgumentParser(prog="substack.py", description="Substack search + extraction (no key).")
    p.add_argument("--json", action="store_true", help="Print the raw structured payload.")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("search", parents=[common], help="Find Substack posts on a topic.")
    s.add_argument("query")
    s.add_argument("--limit", type=int, default=10)
    s.set_defaults(func=cmd_search)

    a = sub.add_parser("archive", parents=[common], help="List posts from a known publication.")
    a.add_argument("publication")
    a.add_argument("--limit", type=int, default=12)
    a.add_argument("--sort", default="new", choices=["new", "top"])
    a.set_defaults(func=cmd_archive)

    po = sub.add_parser("post", parents=[common], help="Get one post's full content + metadata.")
    po.add_argument("publication")
    po.add_argument("slug")
    po.add_argument("--html", action="store_true", help="Return raw HTML body, not plain text.")
    po.set_defaults(func=cmd_post)

    pu = sub.add_parser("publications", parents=[common], help="Discover publications on a topic.")
    pu.add_argument("topic")
    pu.add_argument("--limit", type=int, default=10)
    pu.set_defaults(func=cmd_publications)

    r = sub.add_parser("research", parents=[common], help="Full pipeline: discover + extract full posts.")
    r.add_argument("query")
    r.add_argument("--posts", type=int, default=5)
    r.add_argument("--limit", type=int, default=10)
    r.set_defaults(func=cmd_research)
    return p


def main():
    args = build_parser().parse_args()
    if not hasattr(args, "json"):
        args.json = False
    c = SubstackClient()
    args.func(args, c)


if __name__ == "__main__":
    main()
