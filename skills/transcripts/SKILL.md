---
name: transcripts
description: >
  Pull YouTube, TikTok, Instagram or file transcripts via Supadata. Use
  when they type /transcripts or paste a video URL and want the words.
---

# /transcripts

The words, not a recap. Supadata is paid and metered — use it when they
actually want the transcript.

## Key

`SUPADATA_API_KEY` in `~/.claude/.env`. If it is missing, say so and stop.

```bash
python3 <plugin>/skills/web-scrape/scripts/sources/supadata.py transcript "<url>" --lang en
python3 <plugin>/skills/web-scrape/scripts/sources/supadata.py search "<query>" --limit 10
```

YouTube, TikTok, IG, X, Facebook, or a media file URL.

## Do this

1. Confirm the URL (or search, then they pick).
2. Pull the full transcript.
3. Do the job they asked — extract decisions, objections, quotes. Do not
   replace the transcript with a summary unless they asked for one.

Then `/aios`.
