# shelf-hormozi: integration notes for the chief of staff

## Where the pack came from

- **Source:** `skills/hormozi/` at the repo root (the first-generation course skill). The pack ships a byte-for-byte copy.
- **This is a copy, not a link.** Symlinks break when Claude Code caches a plugin, so the files are real.
- The 1.x `skills/` folders are not moved or edited. First-generation members link to them.

| 1.x source | Copy inside this pack |
|---|---|
| `skills/hormozi/` | `plugins/shelf-hormozi/skills/hormozi/` |

## The sync rule

When a 1.x skill changes, run `python3 tests/shelf-wrappers/sync_copies.py` to recopy it, then
`python3 -m unittest discover -s tests/shelf-wrappers`. The drift test fails if any copy differs from its source, so a
change to `skills/hormozi/` cannot reach members through this pack by accident.

## Marketplace line to add (`.claude-plugin/marketplace.json`, `plugins` array)

```json
{
  "name": "shelf-hormozi",
  "source": "./plugins/shelf-hormozi",
  "version": "2.0.0",
  "description": "The shelf: run the Hormozi offer engine on your own offer, grounded in the books you own, citing book, chapter and page and refusing to invent."
}
```

The same object is in `MARKETPLACE_ENTRY.json`.

## Other shared-file changes

- `README.md` and `ROADMAP.md`: list `shelf-hormozi` under module 12: "Run the Hormozi offer engine on your own offer, grounded in the books you own, citing book, chapter and page and refusing to invent."
- CI: `python3 -m unittest discover -s tests/shelf-wrappers`.

## Known limits

- The cited, book-grounded path is NOT proven here: it needs the member's own book-derived skills, and the repo must never contain them. What is proven is the no-corpus path: Claude says what is missing, points to the gold lesson, and invents no citation. A first proof run also showed that a headless session can search the whole disk for book files; prompt 2 now tells Claude to use only the installed skills.
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
the NAS: `lessons_v2/12-shelf-hormozi/`, `tutorials_v2/12-shelf-hormozi/`, `build-proof/shelf-hormozi/`.
