# Tour: module 12, tools: narration

`/aios learn 12 tools-narration` follows these steps, one at a time. Show the real output, then check it.
Never ask for the key in the chat. Never run a paid command without the member's explicit go.

## Step 1: Find the command
- **Command:** `tools-narration --version`
- **They should see:** `tools-narration 2.0.0`.

## Step 2: Check the tools
- **Command:** `tools-narration doctor`
- **They should see:** `ffmpeg and ffprobe: found`. Key and voice id may say `not set` for now.
- **Check:** if ffmpeg is missing, `brew install ffmpeg` (Mac), then again.

## Step 3: Practise the cut (free)
- **Command:** `tools-narration sample ~/Narration-practice`, then the `split` line it prints.
- **They should see:** three clips with their lengths.
- **Check:** `cat ~/Narration-practice/clips_v1/manifest_v1.json` shows three tracks with no gaps between end and start.

## Step 4: Their key
- **Do:** the member creates a key at elevenlabs.io and adds it (plugin settings, or `export ELEVENLABS_API_KEY=...`).
- **Command:** `tools-narration account`
- **They should see:** their plan and characters used.

## Step 5: Their voice
- **Do:** two or three minutes of their own clean speech. They confirm it is their own voice.
- **Command:** `tools-narration clone "My voice" <recordings> --consent`, then save the id.
- **Check:** `tools-narration say "Testing my voice" -o test_v1.mp3` sounds like them.

## Step 6: One deck, one take
- **Command:** `tools-narration plan slides.json --out script_v1.txt`, they read it, then `tools-narration narrate slides.json --out narration_v1 --yes`.
- **They should see:** one line per slide clip.
- **Check:** they play the first, a middle and the last clip.

## Recap
Practise the cut free, add your key, clone your own voice, read the script, one take, listen. Never pay twice.
