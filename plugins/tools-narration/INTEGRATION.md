# tools-narration: integration notes for the chief of staff

## Where the pack came from

| Source | Owner and licence | What this pack took |
|---|---|---|
| `elevenlabs-toolkit` (our local skill) | Ours | The REST approach on the member's own key (`xi-api-key`, voices, subscription), rewritten narrowly with tests. |
| `daniel-continuous-narration` (private) | Ours | The METHOD only: one take for the whole script, cut halfway between the last word of one slide and the first of the next, two-pass loudness to a PCM master, cut from the master, never pay twice, listen to start, middle and end. Rewritten to use the `with-timestamps` endpoint (one request gives audio and timings). |
| ElevenLabs | Third party | Not bundled. The member's account, key and voice. |

## Left out, and why

| Left out | Why |
|---|---|
| Daniel's trained voice id, its name and its tuned settings | His voice. The pack ships neutral defaults and reads the member's voice id. |
| The approved-case files (a client workshop deck and its measurements) | Client material. |
| `nav-voiceover` and the still-image-to-video step | Private; NavMotion house production. |
| The per-slide HTML player with presenter sync | Deck-specific; the decks pack can embed the clips. |

## Shared-file changes needed (I did not edit these)

1. **`.claude-plugin/marketplace.json`**: add `plugins/tools-narration/MARKETPLACE_ENTRY.json`.
2. **`scripts/build_catalogue.py`**, `CAPABILITIES`: `'tools-narration':['narration','voiceover','elevenlabs','clone my voice','text to speech','tts']`.
3. **`README.md` and `ROADMAP.md`**: list `tools-narration` under module 12, tools.
4. **Tests in CI**: `python3 -m unittest discover -s tests/tools-narration` (the ffmpeg tests skip without ffmpeg).

## Known limits

- One take is capped at 9,500 characters; longer decks are narrated per chapter.
- The response shape of `with-timestamps` was confirmed with one short live call on 26 October 2026
  (`audio_base64`, `alignment.characters`, `character_start_times_seconds`, `character_end_times_seconds`).
