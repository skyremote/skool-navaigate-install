# tools-notebooklm (AIOS 2.0, module 12: the shelf, tools)

Your own files, turned into Google **NotebookLM** notebooks, audio overviews, quizzes, flashcards and study guides,
on your own Google account. You install the public **notebooklm-py** CLI (MIT, unofficial). This pack gives your agent
our way of using it: check which files can go in, one notebook per topic, ask first, then make and download exactly
what you asked for.

## Install

1. Install the start plugin `aios` first (module 1).
2. `pipx install notebooklm-py` (install pipx first if needed: `brew install pipx`), then `notebooklm login`, which opens
   your browser once.

**Claude Code:** `/aios install tools-notebooklm` (or `/plugin install tools-notebooklm@navaigate-aios`), then `/reload-plugins`.

**Codex and Cursor**, from your checkout of this repository:
```
./install.sh tools-notebooklm
./install.sh tools-notebooklm --check
```

## Use

```
tools-notebooklm doctor
tools-notebooklm sample ~/NotebookLM-practice
tools-notebooklm plan ~/NotebookLM-practice
notebooklm create "Practice: Northwind"
notebooklm source add ~/NotebookLM-practice/northwind-brief.md
notebooklm generate audio "short and practical" --wait
notebooklm download audio ~/NotebookLM-practice/overview_v1.mp3
```

Three starter prompts: [prompts.md](prompts.md). The method: [skills/tools-notebooklm/SKILL.md](skills/tools-notebooklm/SKILL.md).

## Licence

MIT. notebooklm-py is MIT and unofficial; it uses your own Google account, and Google can change NotebookLM at any time.
