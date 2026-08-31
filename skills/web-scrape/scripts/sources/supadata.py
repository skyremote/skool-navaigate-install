#!/usr/bin/env python3
"""Supadata — video/transcript source (YouTube, TikTok, Instagram, X, Facebook, files).

The video/transcript modality for the research stack: search YouTube and pull
clean transcripts from a video URL. Unlike Reddit/Academic/Substack this source
is **credit-metered (paid)** — reach for it when video/transcript evidence is
specifically wanted ("what are people saying on YouTube", a talk/interview/demo
you want the actual words of), not on every research pass.

Auth: `x-api-key: <SUPADATA_API_KEY>` (read from ~/.claude/.env via the shared
loader). Base: https://api.supadata.ai/v1.

Transcripts come back two ways and the client handles BOTH:
  - synchronously ({lang, availableLangs, content}) for short media; or
  - as a job id ({jobId}) for long media, which we poll
    GET /transcript/{jobId} until it completes (with a sane timeout).

CLI:
    python3 supadata.py search "<query>" [--limit 10]
    python3 supadata.py transcript "<url>" [--lang en] [--timeout 120]
    python3 supadata.py metadata "<url>"
    python3 supadata.py research "<topic>" [--videos 3] [--limit 10] [--max-chars 12000] [--timeout 120]
Add --json for the raw structured payload (before or after the subcommand).
"""
import argparse
import os
import sys
import time

from _common import RateLimiter, die, emit, load_env, requests

SUPADATA_BASE = "https://api.supadata.ai/v1"
_RL = RateLimiter(0.5)  # paid + metered; stay gentle


def _api_key():
    load_env()
    return os.environ.get("SUPADATA_API_KEY", "").strip()


def _channel_name(channel):
    """Channel may be a string or a nested {id,name,...} object — return a name."""
    if isinstance(channel, dict):
        return channel.get("name") or channel.get("title") or ""
    return channel or ""


def _fmt_duration(seconds):
    """Format an int-seconds duration as M:SS; pass through anything non-numeric."""
    if isinstance(seconds, bool) or not isinstance(seconds, (int, float)):
        return str(seconds) if seconds else ""
    seconds = int(seconds)
    return f"{seconds // 60}:{seconds % 60:02d}"


class SupadataClient:
    """YouTube search + multi-platform transcripts + metadata via Supadata."""

    def __init__(self):
        self.api_key = _api_key()
        if not self.api_key:
            die("SUPADATA_API_KEY missing. Add it to ~/.claude/.env "
                "(one KEY=VALUE per line).")
        self.session = requests.Session()
        self.session.headers.update({
            "x-api-key": self.api_key,
            "Accept": "application/json",
        })

    # ----------------------------------------------------------- transport ----
    def _get(self, path, params=None, timeout=30):
        _RL.wait()
        url = f"{SUPADATA_BASE}{path}"
        try:
            resp = self.session.get(url, params=params or {}, timeout=timeout)
        except Exception as e:
            die(f"Supadata request failed: {e}")
        if resp.status_code == 401:
            die("Supadata 401 — check SUPADATA_API_KEY in ~/.claude/.env.")
        if resp.status_code == 429:
            time.sleep(5)
            resp = self.session.get(url, params=params or {}, timeout=timeout)
        if resp.status_code not in (200, 202):
            # Surface the API's own error text when present, but never the key.
            detail = ""
            try:
                body = resp.json()
                detail = body.get("message") or body.get("error") or ""
            except Exception:
                detail = (resp.text or "")[:200]
            die(f"Supadata {resp.status_code} on {path}: {detail}".strip())
        try:
            return resp.json()
        except Exception:
            die(f"Supadata returned non-JSON on {path}.")

    # ----------------------------------------------------- YouTube search -----
    def search(self, query, limit=10):
        """Search YouTube videos for a topic. Returns normalised result dicts."""
        data = self._get("/youtube/search", {"query": query, "limit": limit})
        return self._normalise_search(data, limit)

    def _normalise_search(self, data, limit):
        # The endpoint returns a list of items; tolerate a wrapped shape too.
        items = data
        if isinstance(data, dict):
            items = (data.get("results") or data.get("videos")
                     or data.get("items") or data.get("data") or [])
        if not isinstance(items, list):
            items = []
        out = []
        for it in items[:limit]:
            if not isinstance(it, dict):
                continue
            vid = (it.get("id") or it.get("videoId") or it.get("video_id") or "")
            url = (it.get("url")
                   or (f"https://www.youtube.com/watch?v={vid}" if vid else ""))
            out.append({
                "title": it.get("title", ""),
                "channel": _channel_name(it.get("channel")
                                         or it.get("channelName")
                                         or it.get("channelTitle")),
                "url": url,
                "video_id": vid,
                "published": (it.get("published") or it.get("publishedDate")
                              or it.get("uploadDate") or it.get("date") or ""),
                "duration": it.get("duration"),
                "views": it.get("viewCount") or it.get("views"),
            })
        return [r for r in out if r["url"] or r["video_id"]]

    # -------------------------------------------------------- transcripts -----
    def transcript(self, url, lang=None, timeout=120, poll_interval=3.0):
        """Multi-platform transcript. Handles sync result AND async job polling.

        Returns {url, lang, availableLangs, content, ...} or raises via die().
        """
        params = {"url": url, "text": "true"}
        if lang:
            params["lang"] = lang
        data = self._get("/transcript", params, timeout=30)

        # Async path: a job id was returned -> poll until complete.
        job_id = data.get("jobId") if isinstance(data, dict) else None
        if job_id:
            data = self._poll_job(job_id, timeout=timeout, poll_interval=poll_interval)

        return self._normalise_transcript(url, data)

    def _poll_job(self, job_id, timeout=120, poll_interval=3.0):
        deadline = time.time() + timeout
        while time.time() < deadline:
            data = self._get(f"/transcript/{job_id}", timeout=30)
            status = (data.get("status") or "").lower() if isinstance(data, dict) else ""
            # Completed: content is present (or status says so).
            if status in ("completed", "complete", "done", "success", "succeeded"):
                return data
            if status in ("failed", "error"):
                detail = data.get("error") or data.get("message") or "job failed"
                die(f"Supadata transcript job {job_id} failed: {detail}")
            # Some responses omit status once done and just include content.
            if not status and (data.get("content") or data.get("transcript")):
                return data
            time.sleep(poll_interval)
        die(f"Supadata transcript job {job_id} timed out after {timeout}s "
            f"(raise --timeout for very long media).")

    def _normalise_transcript(self, url, data):
        if not isinstance(data, dict):
            die("Supadata transcript: unexpected response shape.")
        # Content may be at the top level, or nested under content/result/transcript.
        content = data.get("content")
        if content is None:
            content = data.get("transcript")
        if content is None and isinstance(data.get("result"), dict):
            content = data["result"].get("content") or data["result"].get("transcript")
        if isinstance(content, list):
            # Segmented (non-text) form: join the chunk texts.
            content = " ".join(
                seg.get("text", "") for seg in content if isinstance(seg, dict)
            ).strip()
        content = content or ""
        return {
            "url": url,
            "lang": data.get("lang") or (data.get("result", {}) or {}).get("lang", ""),
            "availableLangs": (data.get("availableLangs")
                               or (data.get("result", {}) or {}).get("availableLangs", [])),
            "content": content,
            "content_length": len(content),
        }

    # ----------------------------------------------------------- metadata -----
    def metadata(self, url):
        """Multi-platform metadata for a media URL."""
        return self._get("/metadata", {"url": url}, timeout=30)

    # ----------------------------------------------------------- research -----
    def research(self, topic, max_videos=3, search_limit=10, max_chars=12000,
                 timeout=120):
        """Pipeline: YouTube-search the topic, transcribe the top N, bundle them.

        Conservative by default (small N, capped transcript length) because this
        source is credit-metered. Shape mirrors the other sources' research()
        output so the research method consumes it unchanged.
        """
        search_results = self.search(topic, limit=search_limit)
        extracted = []
        for r in search_results[:max_videos]:
            url = r.get("url")
            if not url:
                continue
            try:
                t = self.transcript(url, timeout=timeout)
            except SystemExit:
                # A single failed/timed-out video should not sink the bundle.
                continue
            if t and t.get("content"):
                content = t["content"]
                if max_chars and len(content) > max_chars:
                    content = content[:max_chars]
                extracted.append({
                    "title": r.get("title", ""),
                    "channel": r.get("channel", ""),
                    "url": url,
                    "video_id": r.get("video_id", ""),
                    "published": r.get("published", ""),
                    "lang": t.get("lang", ""),
                    "content": content,
                    "content_length": len(content),
                    "truncated": bool(max_chars and t.get("content_length", 0) > max_chars),
                })
        return {
            "topic": topic,
            "search_results_count": len(search_results),
            "search_results": search_results,
            "extracted_count": len(extracted),
            "extracted_transcripts": extracted,
        }


# ---------------------------------------------------------------- CLI --------
def cmd_search(args, c):
    results = c.search(args.query, limit=args.limit)
    if emit({"query": args.query, "results": results}, args.json):
        return
    if not results:
        print("No YouTube videos found.")
        return
    for r in results:
        print(f"{r['title']}  ({r['channel']})")
        meta = "  ".join(x for x in [r.get("published") or "",
                                     _fmt_duration(r.get("duration"))] if x)
        if meta:
            print(f"   {meta}")
        print(f"   {r['url']}")
        print()


def cmd_transcript(args, c):
    t = c.transcript(args.url, lang=args.lang, timeout=args.timeout)
    if emit(t, args.json):
        return
    langs = ", ".join(t.get("availableLangs", []) or [])
    print(f"lang: {t.get('lang', '')}  ({t.get('content_length', 0)} chars)"
          + (f"  available: {langs}" if langs else ""))
    print(f"{t['url']}\n")
    print(t["content"][:5000])


def cmd_metadata(args, c):
    data = c.metadata(args.url)
    if emit(data, args.json):
        return
    if isinstance(data, dict):
        for k in ("title", "channel", "duration", "uploadDate", "viewCount", "description"):
            if data.get(k):
                val = str(data[k])
                print(f"{k}: {val[:300]}")
    else:
        print(data)


def cmd_research(args, c):
    result = c.research(args.query, max_videos=args.videos, search_limit=args.limit,
                        max_chars=args.max_chars, timeout=args.timeout)
    if emit(result, args.json):
        return
    print(f"Discovered {result['search_results_count']}, "
          f"transcribed {result['extracted_count']}\n")
    for t in result["extracted_transcripts"]:
        tag = " [truncated]" if t.get("truncated") else ""
        print(f"# {t['title']} ({t['channel']}, {t['content_length']} chars{tag})")
        print(f"   {t['url']}")
        print("   " + " ".join(t["content"][:240].split()))
        print()


def build_parser():
    # Shared --json flag works before OR after the subcommand (matches webscrape.py).
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", default=argparse.SUPPRESS,
                        help="Print the raw structured payload.")
    p = argparse.ArgumentParser(prog="supadata.py",
                                description="Supadata video/transcript source (paid, metered).")
    p.add_argument("--json", action="store_true", help="Print the raw structured payload.")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("search", parents=[common], help="Search YouTube videos for a topic.")
    s.add_argument("query")
    s.add_argument("--limit", type=int, default=10)
    s.set_defaults(func=cmd_search)

    t = sub.add_parser("transcript", parents=[common],
                       help="Transcript for a video/media URL (YouTube/TikTok/IG/X/FB/file).")
    t.add_argument("url")
    t.add_argument("--lang", help="Preferred transcript language (e.g. en).")
    t.add_argument("--timeout", type=int, default=120,
                   help="Max seconds to wait for an async (long-media) job.")
    t.set_defaults(func=cmd_transcript)

    m = sub.add_parser("metadata", parents=[common], help="Multi-platform metadata for a URL.")
    m.add_argument("url")
    m.set_defaults(func=cmd_metadata)

    r = sub.add_parser("research", parents=[common],
                       help="Pipeline: YouTube-search + transcribe top N (conservative; metered).")
    r.add_argument("query")
    r.add_argument("--videos", type=int, default=3, help="How many top videos to transcribe.")
    r.add_argument("--limit", type=int, default=10, help="How many search results to consider.")
    r.add_argument("--max-chars", type=int, default=12000,
                   help="Cap per-transcript length to control tokens/cost.")
    r.add_argument("--timeout", type=int, default=120,
                   help="Max seconds to wait per async transcript job.")
    r.set_defaults(func=cmd_research)
    return p


def main():
    args = build_parser().parse_args()
    if not hasattr(args, "json"):
        args.json = False
    c = SupadataClient()
    args.func(args, c)


if __name__ == "__main__":
    main()
