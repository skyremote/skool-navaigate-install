# shelf-exec-brief: integration notes for the chief of staff

## Where the pack came from

- **Source:** `skills/exec-brief/` at the repo root (the first-generation course skill). The pack ships a byte-for-byte copy.
- **This is a copy, not a link.** Symlinks break when Claude Code caches a plugin, so the files are real.
- The 1.x `skills/` folders are not moved or edited. First-generation members link to them.

| 1.x source | Copy inside this pack |
|---|---|
| `skills/exec-brief/` | `plugins/shelf-exec-brief/skills/exec-brief/` |

## The sync rule

When a 1.x skill changes, run `python3 tests/shelf-wrappers/sync_copies.py` to recopy it, then
`python3 -m unittest discover -s tests/shelf-wrappers`. The drift test fails if any copy differs from its source, so a
change to `skills/exec-brief/` cannot reach members through this pack by accident.

## Marketplace line to add (`.claude-plugin/marketplace.json`, `plugins` array)

```json
{
  "name": "shelf-exec-brief",
  "source": "./plugins/shelf-exec-brief",
  "version": "2.0.0",
  "description": "The shelf: build a cream-paper A4 decision brief as one HTML file, with your own figures, ready to print to PDF."
}
```

The same object is in `MARKETPLACE_ENTRY.json`.

## Other shared-file changes

- `README.md` and `ROADMAP.md`: list `shelf-exec-brief` under module 12: "Build a cream-paper A4 decision brief as one HTML file, with your own figures, ready to print to PDF."
- CI: `python3 -m unittest discover -s tests/shelf-wrappers`.

## Known limits

- The `userConfig` keys are stored by Claude Code in the keychain. The wrapped 1.x scripts read `~/.claude/.env` or the
  shell environment, not `CLAUDE_PLUGIN_OPTION_*`, and the copy must not be edited. The README therefore tells members
  to use `~/.claude/.env`.
- The skill text still says `/aios` at the end. Script paths are fixed (26 October 2026, in the 1.x skill and this
  copy alike): the skills name "the `scripts/` folder next to this SKILL.md" and the Python uses
  `Path(__file__).resolve().parent`, so they work from the plugin cache and from `~/.codex` and `~/.cursor` skill
  folders. `tests/shelf-wrappers` fails if a shipped file names the old first-generation install folder.

## Kept out of the repo (Daniel's ruling, 26 October 2026)

Lessons, tutorial scripts and build evidence (prompt proof, eval results, sandbox proof) live in the classroom folder on
the NAS: `lessons_v2/12-shelf-exec-brief/`, `tutorials_v2/12-shelf-exec-brief/`, `build-proof/shelf-exec-brief/`.
