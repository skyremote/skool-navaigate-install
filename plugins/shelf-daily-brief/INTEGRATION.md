# shelf-daily-brief: integration notes for the chief of staff

## Where the pack came from

- **Source:** `skills/daily-brief/` at the repo root (the first-generation course skill). The pack ships a byte-for-byte copy.
- **This is a copy, not a link.** Symlinks break when Claude Code caches a plugin, so the files are real.
- The 1.x `skills/` folders are not moved or edited. First-generation members link to them.

| 1.x source | Copy inside this pack |
|---|---|
| `skills/daily-brief/` | `plugins/shelf-daily-brief/skills/daily-brief/` |

## The sync rule

When a 1.x skill changes, run `python3 tests/shelf-wrappers/sync_copies.py` to recopy it, then
`python3 -m unittest discover -s tests/shelf-wrappers`. The drift test fails if any copy differs from its source, so a
change to `skills/daily-brief/` cannot reach members through this pack by accident.

## Marketplace line to add (`.claude-plugin/marketplace.json`, `plugins` array)

```json
{
  "name": "shelf-daily-brief",
  "source": "./plugins/shelf-daily-brief",
  "version": "2.0.0",
  "description": "The shelf: a morning brief you will actually read: your numbers, yesterday's meetings and Slack, and what needs attention, written by one model call and saved to your project."
}
```

The same object is in `MARKETPLACE_ENTRY.json`.

## Other shared-file changes

- `README.md` and `ROADMAP.md`: list `shelf-daily-brief` under module 12: "A morning brief you will actually read: your numbers, yesterday's meetings and Slack, and what needs attention, written by one model call and saved to your project."
- CI: `python3 -m unittest discover -s tests/shelf-wrappers`.

## Known limits

- `scripts/model.py` run alone reads only the shell environment, not `~/.claude/.env`, and prints the first six characters of the key. In the proof it named Gemini while `daily_brief.py` (which loads the `.env`) used OpenAI. The tour therefore reads the provider from the test run instead. Raise it as a 1.x fix if wanted.
- `daily_brief.py` imports matplotlib at start, even for `--test`. On a Mac where `system_profiler SPFontsDataType` hangs (as on the build Mac) the first import hangs while matplotlib builds its font cache. The proof pre-seeded the sandbox font cache; members on a healthy Mac are unaffected.
- Python 3.10+ is required. The macOS system Python is 3.9, and Homebrew Python refuses `pip install --user` (PEP 668), so the README shows the virtual environment route.
- The `userConfig` keys are stored by Claude Code in the keychain. The wrapped 1.x scripts read `~/.claude/.env` or the
  shell environment, not `CLAUDE_PLUGIN_OPTION_*`, and the copy must not be edited. The README therefore tells members
  to use `~/.claude/.env`.
- The skill text still says `/aios` at the end, and names `~/.claude/skills/...` paths (for example
  `~/.claude/skills/web-scrape/scripts/webscrape.py`). Those folders exist only for a first-generation install. In a
  plugin install Claude finds the real folder from the skill's base directory, at the cost of one failed command first
  (seen in the prompt proof). Fixing it means editing the 1.x skill text, which this pack must not do; raise it as a
  change to `skills/` if you want it gone.

## Kept out of the repo (Daniel's ruling, 26 October 2026)

Lessons, tutorial scripts and build evidence (prompt proof, eval results, sandbox proof) live in the classroom folder on
the NAS: `lessons_v2/12-shelf-daily-brief/`, `tutorials_v2/12-shelf-daily-brief/`, `build-proof/shelf-daily-brief/`.
