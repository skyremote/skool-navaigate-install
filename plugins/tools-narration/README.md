# tools-narration (AIOS 2.0, module 12: the shelf, tools)

Narration in your own voice. You use your own **ElevenLabs** account (elevenlabs.io) and your own cloned voice, and
this pack gives your agent our method: the whole script in one take, cut per slide at the timings ElevenLabs returns,
levelled once, so every slide sounds like the same person in the same room.

- **Your account, your voice.** Your key and your voice id live in your own settings.
- **One paid request per deck.** `plan` is free; `narrate` asks for `--yes`; `split` re-cuts without paying again.
- **Consent.** `clone` needs `--consent`: your own voice, or one whose owner agreed in writing.
- **Practise free.** `sample` gives a tone take and timings so you can learn the cut with no account.

## Install

1. Install the start plugin `aios` first (module 1).
2. Create an ElevenLabs account and an API key (profile menu, API Keys). Install ffmpeg (`brew install ffmpeg`).

**Claude Code:** `/aios install tools-narration` (or `/plugin install tools-narration@navaigate-aios`), then
`/reload-plugins`. Open `/plugin`, tools-narration, Configure: paste your key, and later your voice id.

**Codex and Cursor**, from your checkout of this repository:
```
./install.sh tools-narration
./install.sh tools-narration --check
```
Then `export ELEVENLABS_API_KEY=...` and `export ELEVENLABS_VOICE_ID=...` in your shell profile.

Needs Python 3.9 or later and ffmpeg.

## Use

```
tools-narration doctor
tools-narration sample ~/Narration-practice
tools-narration split --slides ~/Narration-practice/slides.json --take ~/Narration-practice/take.mp3 --alignment ~/Narration-practice/alignment.json --out ~/Narration-practice/clips_v1
tools-narration clone "My voice" ~/Recordings/me-1.m4a ~/Recordings/me-2.m4a --consent
tools-narration plan deck/slides.json --out deck/script_v1.txt
tools-narration narrate deck/slides.json --out deck/narration_v1 --yes
```

Three starter prompts: [prompts.md](prompts.md). The method: [skills/tools-narration/SKILL.md](skills/tools-narration/SKILL.md).

## Licence

MIT. ElevenLabs is a third-party service with its own terms, including its rules on voice cloning and consent.
ffmpeg is installed by you (LGPL/GPL).
