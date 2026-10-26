#!/usr/bin/env python3
"""X-Search — real-time X/Twitter source via xAI Grok's server-side X Search tool.

The X/Twitter modality for the research stack: ask Grok a question with its
server-side **X Search** tool enabled and get back a grounded answer plus the X
posts/handles it read, as citations. Use this for "what is X/Twitter saying about
…", real-time X sentiment, or pulling recent posts from specific handles.

Like Supadata this source is **paid / credit-metered**, so it is conservative by
default (small `max_search_results`). Unlike the free sources, it costs per search.

DORMANT UNTIL FUNDED
--------------------
The xAI account this key belongs to is **not funded yet** (`team_blocked: true`):
`/v1/models` is empty and any call is rejected at the billing gate. The wiring is
correct — once billing/credit is added at https://console.x.ai the same commands
work with **no code change**. On a billing/team-block/402/403 error the client
exits cleanly with that message rather than looking like a code bug.

API shape (from the xAI docs — Responses API; the legacy `search_parameters` Live
Search on /v1/chat/completions was removed 12 Jan 2026 and is NOT used here):

  POST https://api.x.ai/v1/responses
  Authorization: Bearer $XAI_API_KEY
  {
    "model": "grok-4.3",
    "input": [{"role": "user", "content": "<question>"}],
    "tools": [{
      "type": "x_search",
      "allowed_x_handles": ["openai"],      # optional, max 20
      "excluded_x_handles": [...],          # optional, max 20
      "from_date": "2026-05-01",            # optional, ISO8601 YYYY-MM-DD
      "to_date":   "2026-06-05",            # optional
      "max_search_results": 10              # optional; we keep this small
    }]
  }

Response: text lives at output[].content[].text (type "output_text"); the X posts
and pages Grok read come back as a top-level `citations` array of URL strings (we
also tolerate `inline_citations`). We normalise each citation to
{text, author/handle, url, date} best-effort — for x.com/<handle>/status/<id> URLs
the handle is parsed from the path.

Model id is overridable: `--model`, else `XAI_MODEL` in ~/.claude/.env, else the
docs' current default `grok-4.3`.

CLI:
    python3 xsearch.py search "<query>" [--handles a,b] [--exclude c,d]
            [--from 2026-05-01] [--to 2026-06-05] [--max-results 10] [--model grok-4.3]
    python3 xsearch.py research "<topic>" [--handles a,b] [--from ...] [--to ...]
            [--max-results 10] [--max-chars 12000] [--model grok-4.3]
Add --json (before or after the subcommand) for the raw structured payload.
"""
import argparse
import os
import re
import sys

from _common import RateLimiter, die, emit, load_env, requests

XAI_BASE = "https://api.x.ai/v1"
XAI_RESPONSES = f"{XAI_BASE}/responses"
# Current default per the xAI docs ("for everything else, use Grok 4.3").
# Overridable via --model or XAI_MODEL. The live /v1/models list is empty until
# the account is funded, so we rely on the documented id, not a runtime lookup.
DEFAULT_MODEL = "grok-4.3"
# Paid + credit-metered: keep the search footprint small by default.
DEFAULT_MAX_RESULTS = 10
_RL = RateLimiter(0.5)

# Substrings that mark a "needs billing / team blocked" failure rather than a code
# bug. When we see one of these (or a 402/403) we exit with the funding message so
# it is obvious the wiring is correct and only credit is missing.
_FUNDING_ERR_HINTS = (
    "team_blocked",
    "team is blocked",
    "blocked",
    "no credits",
    "insufficient",
    "billing",
    "payment",
    "quota",
    "spend",
    "credit",
    "not funded",
    "fund",
    "subscription",
)

_FUNDING_MSG = (
    "xAI X-Search is wired but the xAI account needs billing/credit "
    "(console.x.ai) — no code change needed once funded."
)


def _api_key():
    load_env()
    return os.environ.get("XAI_API_KEY", "").strip()


def _default_model():
    load_env()
    return os.environ.get("XAI_MODEL", "").strip() or DEFAULT_MODEL


def _is_funding_error(status, detail):
    """True if this looks like the dormant-until-funded gate (vs a real bug)."""
    if status in (402, 403):
        return True
    low = (detail or "").lower()
    return any(h in low for h in _FUNDING_ERR_HINTS)


def _split_handles(value):
    """Comma/space separated handles -> clean list (strip @, max 20 per the docs)."""
    if not value:
        return []
    parts = re.split(r"[,\s]+", value.strip())
    out = []
    for p in parts:
        h = p.strip().lstrip("@")
        if h:
            out.append(h)
    return out[:20]


def _handle_from_url(url):
    """Pull an X handle from a status/profile URL, else None.

    https://x.com/elonmusk/status/123 -> elonmusk
    https://twitter.com/openai        -> openai
    """
    if not url:
        return None
    m = re.search(r"https?://(?:www\.|mobile\.)?(?:x|twitter)\.com/([^/?#]+)", url)
    if not m:
        return None
    handle = m.group(1)
    # Skip non-profile path segments x.com sometimes uses.
    if handle.lower() in ("i", "home", "search", "explore", "hashtag", "intent"):
        return None
    return handle


def _is_x_url(url):
    return bool(re.search(r"https?://(?:www\.|mobile\.)?(?:x|twitter)\.com/", url or ""))


class XSearchClient:
    """xAI Grok X-Search via the Responses API + server-side x_search tool."""

    def __init__(self, model=None):
        self.api_key = _api_key()
        if not self.api_key:
            die("XAI_API_KEY missing. Add it to ~/.claude/.env "
                "(one KEY=VALUE per line).")
        self.model = model or _default_model()
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    # ----------------------------------------------------------- transport ----
    def _post_responses(self, body):
        """POST /v1/responses. Returns parsed JSON, or exits cleanly via die().

        Distinguishes the dormant-until-funded gate (402/403/team_blocked/billing
        -> the funding message) from genuine errors (schema/404 -> surfaced as-is,
        so a real bug is never masked as 'just needs funding')."""
        _RL.wait()
        try:
            resp = self.session.post(XAI_RESPONSES, json=body, timeout=120)
        except requests.exceptions.RequestException as e:
            die(f"xAI request failed (transport): {e}")
        _RL.mark()

        if resp.status_code == 200:
            try:
                return resp.json()
            except ValueError:
                die("xAI returned non-JSON on /v1/responses.")

        # Extract the API's own error text (never the key) for the message.
        detail = ""
        code = ""
        try:
            body_json = resp.json()
            err = body_json.get("error")
            if isinstance(err, dict):
                detail = err.get("message") or err.get("code") or ""
                code = str(err.get("code") or "")
            elif isinstance(err, str):
                detail = err
            detail = detail or body_json.get("message") or ""
        except ValueError:
            detail = (resp.text or "")[:300]

        if resp.status_code == 401:
            die("xAI 401 — check XAI_API_KEY in ~/.claude/.env.")

        if _is_funding_error(resp.status_code, f"{detail} {code}"):
            # Dormant-until-funded: clear, actionable, not a code bug.
            die(f"{_FUNDING_MSG}\n  (xAI HTTP {resp.status_code}: "
                f"{detail or 'team blocked / billing required'})")

        # Anything else (404, 400 schema error, 5xx) is a real problem — surface it
        # verbatim so we never hide a wiring bug behind the funding message.
        die(f"xAI {resp.status_code} on /v1/responses: "
            f"{detail or 'unexpected error'}".strip())

    # ------------------------------------------------------- request shaping ---
    def _build_tool(self, handles=None, exclude=None, from_date=None,
                    to_date=None, max_results=DEFAULT_MAX_RESULTS):
        tool = {"type": "x_search"}
        if handles:
            tool["allowed_x_handles"] = handles[:20]
        if exclude:
            tool["excluded_x_handles"] = exclude[:20]
        if from_date:
            tool["from_date"] = from_date
        if to_date:
            tool["to_date"] = to_date
        if max_results:
            tool["max_search_results"] = int(max_results)
        return tool

    def _build_body(self, prompt, tool):
        return {
            "model": self.model,
            "input": [{"role": "user", "content": prompt}],
            "tools": [tool],
        }

    # ----------------------------------------------------- response parsing ----
    @staticmethod
    def _extract_text(data):
        """Pull the assistant text from output[].content[].text (type output_text).

        Tolerates the chat-completions-style choices[].message.content too, in case
        a future/funded response comes back in that shape."""
        if not isinstance(data, dict):
            return ""
        parts = []
        for item in data.get("output", []) or []:
            if not isinstance(item, dict):
                continue
            for c in item.get("content", []) or []:
                if isinstance(c, dict) and c.get("type") in ("output_text", "text"):
                    if c.get("text"):
                        parts.append(c["text"])
        if parts:
            return "\n".join(parts).strip()
        # Fallbacks for alternate shapes.
        if data.get("output_text"):
            return str(data["output_text"]).strip()
        choices = data.get("choices")
        if isinstance(choices, list) and choices:
            msg = choices[0].get("message", {}) if isinstance(choices[0], dict) else {}
            if isinstance(msg, dict) and msg.get("content"):
                return str(msg["content"]).strip()
        return ""

    @staticmethod
    def _extract_citations(data):
        """Return the list of citation URLs from the response.

        Primary: top-level `citations` (array of URL strings). Also tolerates
        `inline_citations` and per-item citations under output[].content[]."""
        if not isinstance(data, dict):
            return []
        urls = []

        def _add(val):
            if isinstance(val, str) and val.strip():
                urls.append(val.strip())
            elif isinstance(val, dict):
                u = val.get("url") or val.get("uri") or val.get("link")
                if u:
                    urls.append(str(u).strip())

        for key in ("citations", "inline_citations"):
            val = data.get(key)
            if isinstance(val, list):
                for v in val:
                    _add(v)

        # Some shapes nest citations on each output content block.
        for item in data.get("output", []) or []:
            if not isinstance(item, dict):
                continue
            for c in item.get("content", []) or []:
                if isinstance(c, dict):
                    inner = c.get("citations") or c.get("annotations")
                    if isinstance(inner, list):
                        for v in inner:
                            _add(v)

        # De-dup, preserve order.
        seen, out = set(), []
        for u in urls:
            if u not in seen:
                seen.add(u)
                out.append(u)
        return out

    def _normalise_citations(self, urls):
        """Map citation URLs onto the shared post shape: text/author/url/date.

        We don't get full post bodies back via citations, so text/date are
        best-effort (left blank) and the handle is parsed from x.com URLs. X
        citations are surfaced first; non-X pages Grok also read follow."""
        x_posts, other = [], []
        for u in urls:
            handle = _handle_from_url(u)
            row = {
                "text": "",            # citation gives the URL, not the body
                "author": handle,      # handle parsed from the URL when present
                "handle": handle,
                "url": u,
                "date": "",            # not provided by the citation list
                "is_x": _is_x_url(u),
            }
            (x_posts if row["is_x"] else other).append(row)
        return x_posts, other

    # ----------------------------------------------------------- public API ---
    def search(self, query, handles=None, exclude=None, from_date=None,
               to_date=None, max_results=DEFAULT_MAX_RESULTS):
        """Ask Grok with X Search enabled. Returns the grounded answer plus the X
        posts/handles (and other pages) it cited, normalised."""
        tool = self._build_tool(handles, exclude, from_date, to_date, max_results)
        data = self._post_responses(self._build_body(query, tool))
        answer = self._extract_text(data)
        urls = self._extract_citations(data)
        x_posts, other = self._normalise_citations(urls)
        return {
            "query": query,
            "model": self.model,
            "answer": answer,
            "x_posts": x_posts,
            "other_citations": other,
            "citation_count": len(urls),
        }

    def research(self, topic, handles=None, exclude=None, from_date=None,
                 to_date=None, max_results=DEFAULT_MAX_RESULTS, max_chars=12000):
        """Structured bundle in the SAME shape the other sources' research()
        produces, so the research method consumes it unchanged. Conservative by
        default (small max_results) because the source is credit-metered."""
        # Ask for a sentiment-aware read of recent X discussion on the topic.
        prompt = (
            f"What are people saying on X about: {topic}? "
            "Summarise the recent discussion, the main viewpoints and overall "
            "sentiment, and name the most relevant accounts. Cite the X posts."
        )
        res = self.search(prompt, handles=handles, exclude=exclude,
                          from_date=from_date, to_date=to_date,
                          max_results=max_results)
        answer = res.get("answer", "")
        truncated = bool(max_chars and len(answer) > max_chars)
        if truncated:
            answer = answer[:max_chars]
        x_posts = res.get("x_posts", [])
        other = res.get("other_citations", [])
        return {
            "topic": topic,
            "model": self.model,
            "search_results_count": len(x_posts) + len(other),
            "search_results": x_posts + other,   # parallels other sources' list
            "extracted_count": len(x_posts),
            "extracted_posts": x_posts,           # mirrors Substack's extracted_posts
            "answer": answer,
            "answer_length": len(answer),
            "answer_truncated": truncated,
            "other_citations": other,
        }


# ---------------------------------------------------------------- CLI --------
def cmd_search(args, c):
    res = c.search(
        args.query,
        handles=_split_handles(getattr(args, "handles", None)),
        exclude=_split_handles(getattr(args, "exclude", None)),
        from_date=getattr(args, "from_date", None),
        to_date=getattr(args, "to_date", None),
        max_results=args.max_results,
    )
    if emit(res, args.json):
        return
    print(f"[model {res['model']}]  {res['citation_count']} citations "
          f"({len(res['x_posts'])} from X)\n")
    if res.get("answer"):
        print(res["answer"][:4000] + "\n")
    if res["x_posts"]:
        print("--- X posts cited ---")
        for p in res["x_posts"]:
            who = f"@{p['handle']}" if p.get("handle") else "(unknown)"
            print(f"  {who}  {p['url']}")
    if res["other_citations"]:
        print("\n--- Other pages cited ---")
        for p in res["other_citations"]:
            print(f"  {p['url']}")


def cmd_research(args, c):
    res = c.research(
        args.query,
        handles=_split_handles(getattr(args, "handles", None)),
        exclude=_split_handles(getattr(args, "exclude", None)),
        from_date=getattr(args, "from_date", None),
        to_date=getattr(args, "to_date", None),
        max_results=args.max_results,
        max_chars=args.max_chars,
    )
    if emit(res, args.json):
        return
    tag = " [truncated]" if res.get("answer_truncated") else ""
    print(f"[model {res['model']}]  {res['extracted_count']} X posts of "
          f"{res['search_results_count']} citations\n")
    if res.get("answer"):
        print(f"# X sentiment ({res['answer_length']} chars{tag})")
        print(res["answer"][:4000] + "\n")
    for p in res["extracted_posts"]:
        who = f"@{p['handle']}" if p.get("handle") else "(unknown)"
        print(f"  {who}  {p['url']}")


def build_parser():
    # Shared --json flag works before OR after the subcommand (matches supadata.py).
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", default=argparse.SUPPRESS,
                        help="Print the raw structured payload.")
    common.add_argument("--handles", default=None,
                        help="Comma/space list of X handles to include (max 20).")
    common.add_argument("--exclude", default=None,
                        help="Comma/space list of X handles to exclude (max 20).")
    common.add_argument("--from", dest="from_date", default=None,
                        help="Earliest date, ISO8601 YYYY-MM-DD.")
    common.add_argument("--to", dest="to_date", default=None,
                        help="Latest date, ISO8601 YYYY-MM-DD.")
    common.add_argument("--max-results", type=int, default=DEFAULT_MAX_RESULTS,
                        help=f"Max X search results (paid/metered; default "
                             f"{DEFAULT_MAX_RESULTS}).")
    common.add_argument("--model", default=None,
                        help=f"Override the model id (else XAI_MODEL env, else "
                             f"{DEFAULT_MODEL}).")

    p = argparse.ArgumentParser(
        prog="xsearch.py",
        description="X-Search via xAI Grok X Search tool (paid; dormant until "
                    "the xAI account is funded at console.x.ai).")
    p.add_argument("--json", action="store_true", help="Print the raw structured payload.")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("search", parents=[common],
                       help="Ask Grok with X Search on; return answer + X citations.")
    s.add_argument("query")
    s.set_defaults(func=cmd_search)

    r = sub.add_parser("research", parents=[common],
                       help="Structured X-sentiment bundle (same shape as other sources).")
    r.add_argument("query")
    r.add_argument("--max-chars", type=int, default=12000,
                   help="Cap the answer length to control tokens/cost.")
    r.set_defaults(func=cmd_research)
    return p


def main():
    args = build_parser().parse_args()
    if not hasattr(args, "json"):
        args.json = False
    c = XSearchClient(model=getattr(args, "model", None))
    args.func(args, c)


if __name__ == "__main__":
    main()
