# Prompts: tools-notebooklm

Paste one into Claude Code, Codex or Cursor.

## 1. Which of my files can go in?

```text
Use tools-notebooklm. Make the practice folder in ~/NotebookLM-practice and tell me which files can become NotebookLM sources and which cannot, and why.
```

**What it does:** checks every file and link in the folder against what NotebookLM accepts.
**How you know it worked:** three sources marked `ok` and one `.pages` file marked `SKIP` with the reason.

## 2. An audio overview for a walk

```text
Use tools-notebooklm. Make a NotebookLM notebook from the four PDFs in ~/Reading/pricing and generate a ten-minute audio overview I can listen to on a walk. Save the MP3 in that folder.
```

**What it does:** checks the files, makes the notebook, adds them, asks one question to confirm, then makes the audio.
**How you know it worked:** an `overview_v1.mp3` in the folder, and the notebook shows four sources in NotebookLM.

## 3. Quiz me

```text
Use tools-notebooklm. From my notebook "Pricing reading", make a quiz and flashcards, download both as JSON into ~/Reading/pricing, and then ask me the first five questions one at a time.
```

**What it does:** generates both, downloads them, then runs a short quiz in the chat.
**How you know it worked:** `quiz_v1.json` and `flashcards_v1.json` in the folder, and the questions match your sources.
