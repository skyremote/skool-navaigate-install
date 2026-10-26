# Supadata (video/transcript — paid, credit-metered)

The **video/transcript** modality for the research stack. Search YouTube and pull
clean transcripts from a video/media URL across **YouTube, TikTok, Instagram, X,
Facebook, and direct file URLs**, plus multi-platform metadata.

Unlike Reddit/Academic/Substack, Supadata is **credit-metered (paid)**. Reach for
it when **video/transcript evidence is specifically wanted** — "what are people
saying on YouTube", a talk/interview/demo/podcast-on-YouTube whose actual words you
need — **not on every research pass**. `research` is deliberately conservative
(small N, capped transcript length) for this reason.

There is **no dedicated podcast endpoint** — podcasts are covered via YouTube search
+ transcript (most are on YouTube), or by passing a direct media file URL to
`transcript`.

## Auth & setup

- Base: `https://api.supadata.ai/v1`
- Header: `x-api-key: <SUPADATA_API_KEY>`
- Key in `~/.claude/.env` (`SUPADATA_API_KEY=...`), loaded by the shared loader —
  nothing to export. A missing key is reported with where to put it.

## CLI

```bash
SD=~/.claude/skills/web-scraping/scripts/sources/supadata.py

# Search YouTube videos for a topic
python3 $SD search "retrieval augmented generation" --limit 10

# Transcript for any supported URL (YouTube/TikTok/IG/X/FB/file)
python3 $SD transcript "https://www.youtube.com/watch?v=T-D1OfcDW1M" --lang en

# Multi-platform metadata for a URL
python3 $SD metadata "https://www.youtube.com/watch?v=T-D1OfcDW1M"

# Pipeline: YouTube-search the topic, transcribe the top N (conservative; metered)
python3 $SD research "AI coding agents" --videos 3 --limit 10 --max-chars 12000
```

Add `--json` (before or after the subcommand) for the raw structured payload.

## Endpoints used

| Endpoint | Used by | Notes |
|----------|---------|-------|
| `GET /transcript?url=…&text=true` | `transcript`, `research` | Multi-platform. `text=true` returns plain text. Optional `lang`. Returns a **sync result** for short media **or** a **`{jobId}`** for long media (see below). |
| `GET /transcript/{jobId}` | `transcript` (polling) | Poll until `status` is completed (or content present). |
| `GET /youtube/transcript?url=…&text=true` | (YouTube-specific equivalent of `/transcript`) | Not wired as a separate command — `/transcript` handles YouTube URLs. |
| `GET /youtube/search?query=…&limit=N` | `search`, `research` | Returns `{query, results:[{type,id,title,description,thumbnail,duration(int s),viewCount,uploadDate,channel:{id,name,thumbnail}}], totalResults}`. The video `url` is built from `id`. |
| `GET /metadata?url=…` | `metadata` | Multi-platform metadata. |

## Sync vs async transcript (handled automatically)

`transcript` and `research` handle **both** return modes:

1. **Sync** (short media) — `GET /transcript` returns
   `{lang, availableLangs[], content}` immediately.
2. **Async** (long media) — `GET /transcript` returns `{jobId}`. The client then
   polls `GET /transcript/{jobId}` every ~3s until `status` reports completion (or
   `content` appears), up to `--timeout` seconds (default **120**; raise it for very
   long media). A failed job exits cleanly with the API's error; a timeout exits
   with a clear message telling you to raise `--timeout`.

Inside `research`, a single failed/timed-out video is skipped so it doesn't sink the
whole bundle.

## What you get

- **`search`** → normalised results: `title, channel, url, video_id, published,
  duration (int seconds), views`.
- **`transcript`** → `{url, lang, availableLangs[], content, content_length}`.
- **`research`** → `{topic, search_results_count, search_results,
  extracted_count, extracted_transcripts}`, where each extracted transcript is
  `{title, channel, url, video_id, published, lang, content, content_length,
  truncated}`. This mirrors the other sources' `research` shape (cf. Substack's
  `extracted_count`/`extracted_posts`) so the research method consumes it unchanged.

## Cost note (important)

Credit-metered. Defaults are conservative on purpose: `research` transcribes only
`--videos 3` of `--limit 10` candidates and caps each transcript at `--max-chars
12000`. Keep N small and use it only when video evidence is the point — otherwise
prefer the free sources (Reddit/Academic/Substack/Exa).

## Gotchas

- `401` → `SUPADATA_API_KEY` missing/wrong in `~/.claude/.env`.
- `429` → metered rate limit; the client backs off ~5s and retries once. The client
  also self-throttles ~0.5s between calls.
- The `channel` field on search results is a nested object in the raw API
  (`{id,name,thumbnail}`); the client flattens it to the channel **name**.
- Some media may have no transcript available (private/no captions/unsupported) —
  the API returns an error and `research` skips that item.
