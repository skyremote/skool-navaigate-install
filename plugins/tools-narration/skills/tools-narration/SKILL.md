---
name: tools-narration
description: Narrate slides, lessons and videos in the member's own voice (their ElevenLabs clone or a voice they chose) on their own ElevenLabs account, as one continuous take cut at aligned slide boundaries. Use for "narrate this deck", "voiceover", "read this in my voice", "clone my voice", or uneven per-slide audio.
---

# Narration in your own voice

The member uses their own ElevenLabs account and their own voice. This skill is how we narrate: the whole script in
ONE take, then cut per slide at the boundaries ElevenLabs' own timings give, levelled once. Separate takes per slide
drift in tone and volume even with identical settings, and listeners hear it.

## The command

Claude Code: `"${CLAUDE_PLUGIN_ROOT}/bin/tools-narration"`. Codex and Cursor: `tools-narration` (in `~/.local/bin`).

| Command | Cost | What it does |
|---|---|---|
| `doctor` | free | ffmpeg, the key (never shown) and the voice id. |
| `account` | free | Plan and characters used. Check before a long take. |
| `voices [--search name]` | free | Voices on their account, with ids. |
| `clone "<name>" <recordings...> --consent` | plan | Instant clone of THEIR OWN voice from their recordings. |
| `plan slides.json --out script.txt` | free | Joins the notes into the one script. They read it before paying. |
| `narrate slides.json --out <folder> --yes` | paid, one request | One take with timings, then one clip per slide and a manifest. |
| `split --slides --take --alignment --out` | free | Cuts an existing take again, without paying twice. |
| `say "text" -o line.mp3` | paid | One short line. |
| `sample <folder>` | free | Three fictional Acme Studio slides, a tone take and its timings, to practise the cut. |

`slides.json` is a list in slide order: `[{"title": "...", "notes": ["what is said", "..."]}]`.

## Setup (once)

1. `doctor`. Install ffmpeg if missing (`brew install ffmpeg` on a Mac).
2. Key: Claude Code `/plugin`, tools-narration, Configure. Codex and Cursor `export ELEVENLABS_API_KEY=...`.
   Never in a chat or a project file.
3. Voice: their own clone (`clone` with two or three clean minutes of their own speech, no music, then `--consent`),
   or a voice from their library. Save the id as "Your ElevenLabs voice id" (or `ELEVENLABS_VOICE_ID`).
   Clone only the member's own voice, or one whose owner gave written consent.

## The method

1. **Script first, in their words.** If the member has a voice skill (`tools-voice`), the script goes through it.
   Spell numbers and names the way they say them.
2. **Plan.** `plan slides.json --out script_v1.txt`. Show the character count and ask them to read the script once.
3. **One take.** `narrate slides.json --out narration_v1 --yes` only after they say go. It is one paid request.
   Never retry a failed paid call blindly: check the folder and `account` first, so they never pay twice.
4. **Check.** The manifest lists every clip with its start, end and length. They listen to the first, a middle and
   the last clip. A voice that sounds right is their judgement, not a number.
5. **Fix without paying again.** A cut in the wrong place: fix the slide notes to match what was said, then `split`.
   A wrong word: change that slide's notes and narrate a new version.
6. **Use it.** One MP3 per slide. Never put the API key in a page or a deck.

Scripts over about 9,500 characters are refused as one take: split the deck into chapters and narrate each as one take.

## Rules

- The member's voice and account only. Never use or copy anyone else's voice id.
- Paid commands wait for the member's explicit go (`--yes`).
- Keep the take, the timings and the manifest with the clips, versioned `_v1`, `_v2`. Never overwrite.
- Optional: ElevenLabs' own MCP server (`uvx elevenlabs-mcp`, with the member's key) gives agents its full toolset.
  This pack does not need it.
