# shelf-video (AIOS 2.0, module 12: the shelf)

Edit a talking-head recording on your own machine. Transcribe it with Whisper, remove the filler words,
tighten the long pauses, burn in captions and export an MP4. You approve every cut before anything renders.

- **Runs locally.** No account, no API key, no upload. This pack has no `userConfig` because it needs no secrets.
- **Open tools.** FFmpeg, openai-whisper or whisper.cpp, and Pillow.
- **Safe by design.** The original is never changed. Every plan, approval and export is a new `_vN` version.

## Install

Install the start plugin `aios` first.

Claude Code: type `/aios install shelf-video` (it runs `aios-guide --harness claude install shelf-video`), then `/reload-plugins`.
Or install it directly:
```
/plugin install shelf-video@navaigate-aios
```

Codex and Cursor, from your checkout of this repository:
```
./install.sh shelf-video
./install.sh shelf-video --check
```

Then install the tools once (macOS shown; Linux lines are in the command guide):
```
brew install ffmpeg
python3 -m pip install --user Pillow openai-whisper
```

## Use

Ask your agent: "Use shelf-video on `~/Videos/intro.mp4`. Show me the plan before you cut anything."
Or run the steps yourself:

```
shelf-video init ~/Videos/intro.mp4
shelf-video transcribe --project ~/Videos/intro_EDIT_v1
shelf-video plan --project ~/Videos/intro_EDIT_v1 --show
shelf-video approve --project ~/Videos/intro_EDIT_v1 --yes
shelf-video render --project ~/Videos/intro_EDIT_v1
shelf-video verify --project ~/Videos/intro_EDIT_v1
```

No recording yet? `shelf-video sample` makes a 30-second practice clip with a drawn, fictional presenter.

Full commands, settings and fixes: [skills/shelf-video/references/commands.md](skills/shelf-video/references/commands.md).

## What it does not do

It does not publish, add B-roll or motion graphics, cut vertical shorts, or clone a voice. It edits what you recorded.

## Licence

MIT. Parts of the approach (source fingerprinting, frame-snapped cuts, the approval gate) come from
cutroom-starter, MIT, Copyright (c) 2026 NavAIgate.
