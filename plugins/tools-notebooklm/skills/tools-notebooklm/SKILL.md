---
name: tools-notebooklm
description: Turn the member's own files and links into Google NotebookLM notebooks on their own Google account, then ask questions and make audio overviews, quizzes, flashcards, reports and mind maps, with the public notebooklm-py CLI. Use for "make a NotebookLM notebook from these", "audio overview", "podcast from my files", "quiz me on this", "study guide", "flashcards".
---

# NotebookLM from your own files

The member uses their own Google account and the public `notebooklm-py` CLI (teng-lin/notebooklm-py, MIT). It is an
unofficial client: say so once, and say that Google can change NotebookLM at any time. This skill is how we use it:
check which files can go in, one notebook per topic, then generate and download what they asked for.

## Commands

This pack: `"${CLAUDE_PLUGIN_ROOT}/bin/tools-notebooklm"` (Claude Code) or `tools-notebooklm` (Codex, Cursor).

| Command | What it does |
|---|---|
| `doctor` | notebooklm-py installed? Signed in? |
| `plan <folder>` | Every file (and the links in `links.txt`) that can be a source, what cannot and why, and how many notebooks. |
| `sample <folder>` | A practice folder of fictional sources. |

The public CLI, `notebooklm` (after `pipx install notebooklm-py`):

| Job | Command |
|---|---|
| Sign in (once, browser) | `notebooklm login`; check with `notebooklm auth check` |
| Notebooks | `notebooklm list`, `notebooklm create "Name"`, `notebooklm use <id>` (part of the id is enough) |
| Sources | `notebooklm source add <file or link>`, `source add -t text "..."`, `source list` |
| Ask | `notebooklm ask "question"` |
| Make | `notebooklm generate audio "<instructions>" --wait` (also `report`, `quiz`, `flashcards`, `mind-map`, `slide-deck`, `video`) |
| Download | `notebooklm download audio ./overview_v1.mp3` (also `report`, `quiz --format json`, `flashcards --format json`) |

Run `notebooklm <command> --help` for the current options; the client changes faster than this page.

## The method

1. `doctor`. If not signed in, the member runs `notebooklm login` in their own terminal (it opens a browser). Never
   try to log in for them.
2. `plan <their folder>`. Show what will go in and what will not. Over 50 sources: one notebook per topic.
3. `create` the notebook with a clear name, `use` it, `source add` each file from the plan.
4. Ask a question first (`ask`) to confirm the sources loaded and say what the notebook is about.
5. Generate only what they asked for, with `--wait`. Audio overviews take minutes.
6. Download into their folder with `_v1` names. Tell them the file paths.

## Rules

- Their own files only, or files they are allowed to upload to Google.
- Do not add confidential client material unless the member confirms their Google account terms allow it.
- Sharing (`notebooklm share add`) only to addresses the member names, and only as viewer unless they say otherwise.
