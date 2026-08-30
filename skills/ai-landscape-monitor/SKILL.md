---
name: ai-landscape-monitor
description: >
  A daily scan of the public AI leaderboards (text, code, vision, image,
  video, speech) that spots ranking changes and keeps an ai-docs/ folder
  current with the best model per job, its API ID and price. Use when they
  type /ai-landscape-monitor, ask which model is best right now, or want
  their agents to stop guessing at model names.
---

# /ai-landscape-monitor

Which model is best for text, code, vision, image, video, speech, today,
not in the training data. A scan runs every morning against the public
leaderboards, writes what moved, and an `update` pass rewrites the docs
for the categories that changed. Their agents read `ai-docs/` before
picking a model.

## Keys

Nothing required. The leaderboards are public pages. Optional, in
`~/.claude/.env`:

```
OPENROUTER_API_KEY=sk-or-v1-...   # free account, adds pricing and context length
```

Python 3.10+. `pip install -r scripts/requirements.txt` (requests,
python-dotenv). The scripts run **from their project folder**; that is
where `data/`, `ai-docs/` and `outputs/ai-landscape/` go.

## Ten categories

LMArena (ELO): text, code, vision, text-to-image, image-edit, search,
text-to-video, image-to-video. TTS Arena V2 (ELO): text-to-speech. Voice
Writer (WER, lower is better): speech-to-text.

## Do this

1. Ask which categories they actually care about. Default is all ten; if
   they only build with text and code, trim `CATEGORIES` in
   `scripts/lmarena.py`.
2. First scan, from their project folder:
   ```bash
   cd <their project>
   python3 ~/.claude/skills/ai-landscape-monitor/scripts/scanner.py
   ```
   It creates `data/workspace.db` (or uses `DB_PATH`), writes
   `data/ai-scan-latest.json` and `outputs/ai-landscape/YYYY-MM-DD.md`.
   First run shows everything as new; that is expected. Expect 100+
   models. Zero models means the site changed or the network is down.
3. Make the docs folder:
   ```bash
   mkdir -p ai-docs/{text,code,vision,text-to-image,image-edit,search,text-to-video,image-to-video,text-to-speech,speech-to-text}
   cp ~/.claude/skills/ai-landscape-monitor/templates/ai-docs-readme.md ai-docs/README.md
   ```
4. `/ai-landscape-monitor update` (or `update text` for one category) runs
   the unattended pass in `references/update-ai-docs.md`: rankings, diff,
   one research subagent per changed category, docs rewritten. It uses
   their Claude Code session, so a full ten-category run costs real usage;
   try one category first.
5. Schedule the scan. macOS: `templates/com.aios.ai-landscape.plist`
   (fill `__PYTHON__`, `__HOME__`, `__WORKSPACE__`, copy to
   `~/Library/LaunchAgents/`, `launchctl load`). Linux:
   `30 6 * * * cd /path/to/project && python3 ~/.claude/skills/ai-landscape-monitor/scripts/scanner.py >> data/ai-scan.log 2>&1`.
6. Add two lines to their `CLAUDE.md`: `ai-docs/README.md` is the model
   reference, read it before choosing a model; the scan runs at 06:30.
7. If they run `/daily-brief`, the scan JSON is at
   `data/ai-scan-latest.json`. A line in the brief's context about it is
   enough for the brief to mention leader changes.

## Known gaps

- The collectors parse public HTML (arena.ai Next.js payload, TTS Arena
  divs, Voice Writer table). When a site changes its markup a collector
  returns `skipped` and the scan carries on without it. Fix is in the one
  collector file; `update` falls back to `WebFetch` on the source URL.
- The old `/prime` hook is gone; the `CLAUDE.md` line in step 6 does the
  same job.
- OpenRouter categories are inferred from modality fields, so a few
  models land in the wrong bucket. It only affects pricing lookups.

Then `/aios`.
