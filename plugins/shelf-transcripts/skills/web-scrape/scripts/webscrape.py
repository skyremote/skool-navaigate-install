#!/usr/bin/env python3
"""web-scraping helper — Exa semantic search + Firecrawl scrape over REST.

Two providers, one CLI. No SDK install: everything goes through the REST
APIs with `requests`, which is already present on the system.

  Exa (semantic search):   search | contents | answer
  Firecrawl (JS rendering): scrape | crawl-search

Keys are read from the environment, falling back to ~/.claude/.env:
  EXA_API_KEY=...
  FIRECRAWL_API_KEY=fc-...

Run `python3 webscrape.py <subcommand> --help` for per-command options.
Add `--json` to any command to get the raw API response instead of the
human-readable view.
"""
import argparse
import json
import os
import sys
import warnings
from pathlib import Path

# Quiet the LibreSSL/urllib3 NotOpenSSLWarning that the system Python emits, so
# it doesn't pollute the output the agent reads. Harmless to the requests made.
warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL")

try:
    import requests
except ImportError:
    sys.exit("requests not installed. Run: python3 -m pip install --user requests")

EXA_BASE = "https://api.exa.ai"
FC_BASE = "https://api.firecrawl.dev/v2"

# Allowed Exa search types, verified against the canonical coding-agent guide.
EXA_TYPES = ["auto", "fast", "instant", "deep-lite", "deep", "deep-reasoning"]


def load_env():
    """Populate os.environ from ~/.claude/.env without overriding real env vars."""
    env_path = Path.home() / ".claude" / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def get_key(name):
    load_env()
    key = os.environ.get(name)
    if not key:
        sys.exit(
            f"{name} is not set. Add `{name}=...` to ~/.claude/.env (one KEY=VALUE "
            f"per line) or export it in your shell."
        )
    return key


def post(url, headers, body, timeout):
    """POST JSON and return parsed JSON, exiting cleanly on any error."""
    try:
        r = requests.post(url, headers=headers, json=body, timeout=timeout)
    except requests.exceptions.RequestException as e:
        sys.exit(f"Request to {url} failed: {e}")
    if r.status_code >= 400:
        sys.exit(f"HTTP {r.status_code} from {url}\n{r.text[:800]}")
    try:
        return r.json()
    except ValueError:
        sys.exit(f"Non-JSON response from {url}:\n{r.text[:800]}")


# ---------------------------------------------------------------- Exa --------
def _exa_contents_obj(args):
    """Build the `contents` object from --text/--highlights/--summary flags."""
    contents = {}
    if args.text:
        contents["text"] = {"maxCharacters": args.max_chars} if args.max_chars else True
    if args.highlights:
        contents["highlights"] = True
    if args.summary:
        contents["summary"] = True
    if not contents:  # sensible default for LLM workflows: token-efficient excerpts
        contents["highlights"] = True
    if args.max_age_hours is not None:
        contents["maxAgeHours"] = args.max_age_hours
    return contents


def cmd_search(args):
    key = get_key("EXA_API_KEY")
    body = {
        "query": args.query,
        "type": args.type,
        "numResults": args.num,
        "contents": _exa_contents_obj(args),
    }
    if args.include_domains:
        body["includeDomains"] = args.include_domains
    if args.exclude_domains:
        body["excludeDomains"] = args.exclude_domains
    if args.system_prompt:
        body["systemPrompt"] = args.system_prompt
    if args.output_schema:
        body["outputSchema"] = json.loads(args.output_schema)
    data = post(
        f"{EXA_BASE}/search",
        {"x-api-key": key, "Content-Type": "application/json"},
        body,
        args.timeout,
    )
    if args.json:
        print(json.dumps(data, indent=2))
        return
    if data.get("output"):  # outputSchema synthesis present
        print("=== Synthesised output ===")
        print(json.dumps(data["output"].get("content"), indent=2))
        print()
    results = data.get("results", [])
    if not results:
        print("No results.")
        return
    for i, res in enumerate(results, 1):
        print(f"{i}. {res.get('title') or '(no title)'}")
        print(f"   {res.get('url', '')}")
        if res.get("highlights"):
            print("   " + " … ".join(h.strip() for h in res["highlights"][:2]))
        elif res.get("summary"):
            print("   " + res["summary"][:500].strip())
        elif res.get("text"):
            print("   " + " ".join(res["text"][:500].split()))
        print()


def cmd_contents(args):
    key = get_key("EXA_API_KEY")
    # On /contents the content options are TOP-LEVEL (unlike /search where they nest).
    body = {"urls": args.urls}
    if args.text:
        body["text"] = {"maxCharacters": args.max_chars} if args.max_chars else True
    else:
        body["highlights"] = True
    if args.max_age_hours is not None:
        body["maxAgeHours"] = args.max_age_hours
    data = post(
        f"{EXA_BASE}/contents",
        {"x-api-key": key, "Content-Type": "application/json"},
        body,
        args.timeout,
    )
    if args.json:
        print(json.dumps(data, indent=2))
        return
    for res in data.get("results", []):
        print(f"# {res.get('title') or '(no title)'}")
        print(res.get("url", ""))
        if res.get("text"):
            print(res["text"])
        elif res.get("highlights"):
            print("\n".join(res["highlights"]))
        print("\n---\n")


def cmd_answer(args):
    key = get_key("EXA_API_KEY")
    body = {"query": args.query}
    data = post(
        f"{EXA_BASE}/answer",
        {"x-api-key": key, "Content-Type": "application/json"},
        body,
        args.timeout,
    )
    if args.json:
        print(json.dumps(data, indent=2))
        return
    print(data.get("answer", "(no answer)"))
    cites = data.get("citations", [])
    if cites:
        print("\nSources:")
        for c in cites:
            print(f"- {c.get('title') or c.get('url')}: {c.get('url')}")


# ----------------------------------------------------------- Firecrawl -------
def cmd_scrape(args):
    key = get_key("FIRECRAWL_API_KEY")
    body = {
        "url": args.url,
        "formats": args.formats,
        "onlyMainContent": not args.full,
        "timeout": args.fc_timeout,
    }
    if args.wait:
        body["waitFor"] = args.wait
    resp = post(
        f"{FC_BASE}/scrape",
        {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        body,
        args.timeout,
    )
    if args.json:
        print(json.dumps(resp, indent=2))
        return
    data = resp.get("data", {})
    out = data.get("markdown") or data.get("html") or data.get("rawHtml") or ""
    if not out:
        print(f"(no content extracted; full response keys: {list(data.keys())})")
        return
    print(out)


def cmd_crawl_search(args):
    """Firecrawl's own web search (discovery + optional scrape of each hit)."""
    key = get_key("FIRECRAWL_API_KEY")
    body = {"query": args.query, "limit": args.num}
    if args.scrape:
        body["scrapeOptions"] = {"formats": ["markdown"]}
    resp = post(
        f"{FC_BASE}/search",
        {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        body,
        args.timeout,
    )
    if args.json:
        print(json.dumps(resp, indent=2))
        return
    web = (resp.get("data") or {}).get("web") or resp.get("data") or []
    if isinstance(web, dict):
        web = web.get("web", [])
    for i, res in enumerate(web, 1):
        print(f"{i}. {res.get('title') or '(no title)'}")
        print(f"   {res.get('url', '')}")
        if res.get("description"):
            print("   " + res["description"][:300])
        print()


# ------------------------------------------------------------- parser --------
def build_parser():
    # Shared flags. Defined on both the top-level parser and (via this parent,
    # with SUPPRESS defaults so they don't clobber) every subparser, so
    # `--timeout`/`--json` work whether placed before OR after the subcommand.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--timeout", type=int, default=argparse.SUPPRESS,
                        help="HTTP timeout in seconds (default 120; raise for deep Exa types).")
    common.add_argument("--json", action="store_true", default=argparse.SUPPRESS,
                        help="Print the raw API JSON response.")

    p = argparse.ArgumentParser(
        prog="webscrape.py",
        description="Exa semantic search + Firecrawl scraping over REST.",
    )
    p.add_argument("--timeout", type=int, default=120,
                   help="HTTP timeout in seconds (default 120; raise for deep Exa types).")
    p.add_argument("--json", action="store_true", help="Print the raw API JSON response.")
    sub = p.add_subparsers(dest="command", required=True)

    # Exa search
    s = sub.add_parser("search", parents=[common], help="Exa semantic web search.")
    s.add_argument("query")
    s.add_argument("--type", choices=EXA_TYPES, default="auto",
                   help="Search depth. auto=balanced (default); fast/instant=quick; "
                        "deep/deep-reasoning=research-grade synthesis.")
    s.add_argument("--num", type=int, default=10, help="Number of results (1-100).")
    s.add_argument("--text", action="store_true", help="Return full page text.")
    s.add_argument("--highlights", action="store_true",
                   help="Return query-relevant excerpts (default if no content flag).")
    s.add_argument("--summary", action="store_true", help="Return an LLM summary per result.")
    s.add_argument("--max-chars", type=int, help="Cap on --text length (controls token cost).")
    s.add_argument("--max-age-hours", type=int,
                   help="Cache freshness: 0=always livecrawl, -1=cache only, omit=default.")
    s.add_argument("--include-domains", nargs="+", help="Restrict to these domains.")
    s.add_argument("--exclude-domains", nargs="+", help="Drop these domains.")
    s.add_argument("--system-prompt", help="Synthesis instructions (use with --output-schema).")
    s.add_argument("--output-schema", help="JSON schema string for grounded structured output.")
    s.set_defaults(func=cmd_search)

    # Exa contents
    c = sub.add_parser("contents", parents=[common],
                       help="Exa: get clean content for URLs you already have.")
    c.add_argument("urls", nargs="+")
    c.add_argument("--text", action="store_true", help="Full text (default: highlights).")
    c.add_argument("--max-chars", type=int, help="Cap on --text length.")
    c.add_argument("--max-age-hours", type=int, help="0=always livecrawl, -1=cache only.")
    c.set_defaults(func=cmd_contents)

    # Exa answer
    a = sub.add_parser("answer", parents=[common],
                       help="Exa: grounded answer with citations for a question.")
    a.add_argument("query")
    a.set_defaults(func=cmd_answer)

    # Firecrawl scrape
    sc = sub.add_parser("scrape", parents=[common],
                        help="Firecrawl: render a (JS-heavy) page to clean markdown.")
    sc.add_argument("url")
    sc.add_argument("--formats", nargs="+", default=["markdown"],
                    help="Output formats: markdown html rawHtml links screenshot (default markdown).")
    sc.add_argument("--full", action="store_true",
                    help="Keep nav/footer/banners (default strips them via onlyMainContent).")
    sc.add_argument("--wait", type=int,
                    help="Milliseconds to wait for JS to render before scraping.")
    sc.add_argument("--fc-timeout", type=int, default=60000,
                    help="Firecrawl-side timeout in ms (1000-300000, default 60000).")
    sc.set_defaults(func=cmd_scrape)

    # Firecrawl search
    fs = sub.add_parser("crawl-search", parents=[common],
                        help="Firecrawl: web search; add --scrape to also pull each page.")
    fs.add_argument("query")
    fs.add_argument("--num", type=int, default=5, help="Number of results.")
    fs.add_argument("--scrape", action="store_true", help="Also scrape each result to markdown.")
    fs.set_defaults(func=cmd_crawl_search)

    return p


def main():
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
