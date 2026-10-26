# shelf-design-brain: integration notes for the chief of staff

## Where the pack came from

- **Source:** `skills/design-brain/` at the repo root (the first-generation course skill). The pack ships a byte-for-byte copy.
- **This is a copy, not a link.** Symlinks break when Claude Code caches a plugin, so the files are real.
- The 1.x `skills/` folders are not moved or edited. First-generation members link to them.

| 1.x source | Copy inside this pack |
|---|---|
| `skills/design-brain/` | `plugins/shelf-design-brain/skills/design-brain/` |

## The sync rule

When a 1.x skill changes, run `python3 tests/shelf-wrappers/sync_copies.py` to recopy it, then
`python3 -m unittest discover -s tests/shelf-wrappers`. The drift test fails if any copy differs from its source, so a
change to `skills/design-brain/` cannot reach members through this pack by accident.

## Marketplace line to add (`.claude-plugin/marketplace.json`, `plugins` array)

```json
{
  "name": "shelf-design-brain",
  "source": "./plugins/shelf-design-brain",
  "version": "2.0.0",
  "description": "The shelf: query 1,119 sourced design fundamentals and get design critiques that cite the entry number and the named source."
}
```

The same object is in `MARKETPLACE_ENTRY.json`.

## Other shared-file changes

- `README.md` and `ROADMAP.md`: list `shelf-design-brain` under module 12: "Query 1,119 sourced design fundamentals and get design critiques that cite the entry number and the named source."
- CI: `python3 -m unittest discover -s tests/shelf-wrappers`.

## Known limits

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
the NAS: `lessons_v2/12-shelf-design-brain/`, `tutorials_v2/12-shelf-design-brain/`, `build-proof/shelf-design-brain/`.
