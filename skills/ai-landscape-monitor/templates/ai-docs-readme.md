# AI Docs — which model to use for what

> Kept current by `/ai-landscape-monitor update`. Last scan: (run your first scan)
> Sources: [LMArena](https://arena.ai) (8 categories), [TTS Arena V2](https://tts-agi-tts-arena-v2.hf.space) (text-to-speech), [Voice Writer](https://voicewriter.io) (speech-to-text), plus OpenRouter pricing if the key is set.
> The daily scan spots ranking changes; the update only rewrites the categories that moved.

## Category leaders

| Category | Leader | Provider | Score | Doc |
|----------|--------|----------|-------|-----|
| **Text LLMs** | (run first scan) | — | — | [text/state-of-the-art.md](text/state-of-the-art.md) |
| **Code** | — | — | — | [code/state-of-the-art.md](code/state-of-the-art.md) |
| **Vision** | — | — | — | [vision/state-of-the-art.md](vision/state-of-the-art.md) |
| **Text-to-Image** | — | — | — | [text-to-image/state-of-the-art.md](text-to-image/state-of-the-art.md) |
| **Image Edit** | — | — | — | [image-edit/state-of-the-art.md](image-edit/state-of-the-art.md) |
| **Search** | — | — | — | [search/state-of-the-art.md](search/state-of-the-art.md) |
| **Text-to-Video** | — | — | — | [text-to-video/state-of-the-art.md](text-to-video/state-of-the-art.md) |
| **Image-to-Video** | — | — | — | [image-to-video/state-of-the-art.md](image-to-video/state-of-the-art.md) |
| **Text-to-Speech** | — | — | — | [text-to-speech/state-of-the-art.md](text-to-speech/state-of-the-art.md) |
| **Speech-to-Text** | — | — | — | [speech-to-text/state-of-the-art.md](speech-to-text/state-of-the-art.md) |

## How this works

Each category doc (`{category}/state-of-the-art.md`) holds:
- a quick-pick table: best model per use case, exact API model ID, price
- the top 10-15 with score, votes and pricing
- integration notes: API access, SDK, the things that catch people out
- what is moving in the category

The daily scan (`scanner.py`, 06:30) pulls every leaderboard, compares with
the previous day in the database and flags categories that changed. Run
`/ai-landscape-monitor update` to research the changes and rewrite those docs.

Metrics: LMArena and TTS Arena use ELO (higher is better). Voice Writer uses
WER % (lower is better).

## Changelog

| Date | Change |
|------|--------|
| — | First setup. Run `/ai-landscape-monitor update` to fill every category |
