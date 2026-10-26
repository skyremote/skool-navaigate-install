# Prompts: tools-narration

Paste one into Claude Code, Codex or Cursor.

## 1. Learn the cut for free

```text
Use tools-narration. Make the practice files in ~/Narration-practice, cut the take into one clip per slide, and show me the manifest.
```

**What it does:** makes three fictional Acme Studio slides, a tone recording and its timings, then cuts it per slide.
**How you know it worked:** you get `slide-01.mp3` to `slide-03.mp3` and a `manifest_v1.json` listing each clip's start
and end. No account was used.

## 2. Clone your own voice

```text
Use tools-narration. Clone my own voice from the recordings in ~/Recordings/me (it is my voice, I consent), then read "Welcome to my course" in it and save the MP3.
```

**What it does:** sends your recordings to your ElevenLabs account, makes your voice, and reads one line.
**How you know it worked:** it prints your new voice id and saves the MP3, and when you play it, it sounds like you.
Save the id in the plugin settings.

## 3. Narrate a deck in one take

```text
Use tools-narration. Narrate the slides in ~/Decks/q3-review/slides.json in my voice. Show me the script and the character count first, and only make the paid take after I say go.
```

**What it does:** joins the notes into one script, waits for your go, makes one take and cuts it per slide.
**How you know it worked:** one clip per slide in a new `narration_v1` folder, a manifest, and the clips sound like
one continuous recording when played in order.
