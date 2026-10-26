# shelf-video command guide

Replace `shelf-video` with the full path to the pack's `bin/shelf-video` if it is not on PATH.

## Install the tools once

| Tool | Why | macOS | Linux (Ubuntu) |
|---|---|---|---|
| FFmpeg | cuts, encodes, checks | `brew install ffmpeg` | `sudo apt install ffmpeg` |
| Pillow | draws the captions | `python3 -m pip install --user Pillow` | same |
| openai-whisper | transcribes, on your machine | `python3 -m pip install --user -U openai-whisper` | same |
| whisper.cpp (optional, faster on Apple silicon) | transcribes | `brew install whisper-cpp` | build from github.com/ggerganov/whisper.cpp |

openai-whisper and whisper.cpp are MIT-licensed open-source projects. FFmpeg is LGPL/GPL. Pillow is MIT-CMU.
None of them needs an account.

## Commands

```sh
shelf-video sample --out ~/Videos/practice/sam_acme_v1.mp4      # optional practice clip
shelf-video init "<recording>"                                   # makes <name>_EDIT_v1/ beside it
shelf-video transcribe --project "<folder>"                       # Whisper, small.en by default
shelf-video plan --project "<folder>" --show                      # proposals + review page
shelf-video approve --project "<folder>" --yes                    # the member's decision
shelf-video render --project "<folder>"                           # MP4 + SRT
shelf-video verify --project "<folder>"                           # PASS or FAIL, plus stills
```

Useful options:
- `transcribe --model medium.en` for a harder accent or a noisy room (slower, more accurate).
- `transcribe --engine whisper-cpp --model-path ~/models/ggml-small.en.bin` for whisper.cpp.
- `transcribe --import-json <file>` to use a Whisper JSON you already have (openai-whisper, faster-whisper,
  whisper.cpp `-ojf`). It must have word timings.
- `plan --max-pause 0.9` keeps more of your natural pauses.
- `approve --drop 3,7` keeps proposals 3 and 7 in the film. `--add 12` cuts an unselected proposal.
  `--remove 41.2:43.0` cuts any range you choose (seconds in the original).
- `render --no-burn` gives a clean MP4 and a separate SRT, for YouTube or LinkedIn captions.

## The project folder

```
<name>_EDIT_v1/
  project.json                 the original's path and SHA-256 fingerprint
  transcript/words_v1.json     every word with its start and end time
  transcript/words_v1.txt      the plain transcript
  plans/plan_v1.json|.md       the proposals
  plans/review_v1.html         open in a browser to hear each proposal
  approvals/approval_v1.json   the member's decision, signed against the plan
  exports/edit_v1/edited.mp4   the finished film
  exports/edit_v1/captions.srt captions timed to the finished film
  exports/edit_v1/verify.json  the check result; checks/*.png are stills to look at
```

## Settings

`~/.config/aios/shelf-video.json` (set `AIOS_CONFIG_DIR` to move it). Show them with `shelf-video settings`.

| Setting | Default | What it does |
|---|---|---|
| `whisper_model` | `small.en` | Whisper model. `medium.en` is more accurate, `base.en` is faster. |
| `fillers` | um, uh, er, erm, ah, hmm... | Words cut by default. |
| `soft_fillers` | you know, like, sort of... | Proposed only, never cut by default. |
| `max_pause` / `keep_pause` | 0.6 / 0.3 s | Pauses longer than max_pause shrink to keep_pause. |
| `caption.font` | system bold sans | Path to a TTF or OTF, such as your brand font. |
| `caption.colour` / `caption.box` | `#FFFFFF` / `#000000B8` | Text colour and box colour (last two hex digits are opacity). |
| `caption.size_ratio` | 0.055 | Text height as a share of the frame height. |
| `caption.margin_ratio` | 0.11 | Gap below the caption box; never less than 90 px. |
| `caption.max_chars` | 36 | Characters per caption line. |
| `export.crf` | 18 | Quality. Lower is larger and sharper. |
| `export.loudnorm` | false | Level the voice to -16 LUFS for social platforms. |

## Common problems

- **Filler words are missing from the transcript.** Whisper tidies speech. The pack prompts it to keep fillers,
  but a quiet "um" can still vanish. Try `--model medium.en --force`, or cut it by hand with `--remove`.
- **A word is clipped at a join.** Whisper's word times are close, not exact. Set `pad` higher
  (`shelf-video settings set pad=0.1`), plan again, approve again, render again.
- **"This file carries rotation metadata".** Phone videos often do. Export an upright copy first:
  `ffmpeg -i in.mov -c:v libx264 -crf 18 -c:a aac upright.mp4`, then init the copy.
- **"Unsupported frame rate".** Variable frame rate (screen recorders, phones). Export a constant-rate copy:
  `ffmpeg -i in.mp4 -r 30 -c:v libx264 -crf 18 -c:a aac cfr.mp4`.
- **Whisper is slow.** The first run downloads the model. After that, `small.en` runs at a few times real time on
  a laptop CPU. whisper.cpp is faster on Apple silicon.
- **"Another shelf-video step is running".** A step crashed. Check no ffmpeg or whisper process is running, then
  delete `.busy` in the project folder.
- **Verify says FAIL on duration.** Render again. If it fails twice, send the verify.json to the community.
