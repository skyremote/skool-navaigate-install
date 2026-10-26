# shelf-deep-research: integration notes for the chief of staff

## Where the pack came from

- **Source:** `skills/deep-research/` at the repo root (the first-generation course skill). The pack ships a byte-for-byte copy.
- **This is a copy, not a link.** Symlinks break when Claude Code caches a plugin, so the files are real.
- The 1.x `skills/` folders are not moved or edited. First-generation members link to them.

| 1.x source | Copy inside this pack |
|---|---|
| `skills/deep-research/` | `plugins/shelf-deep-research/skills/deep-research/` |
| `skills/web-scrape/` | `plugins/shelf-deep-research/skills/web-scrape/` |

## The sync rule

When a 1.x skill changes, run `python3 tests/shelf-wrappers/sync_copies.py` to recopy it, then
`python3 -m unittest discover -s tests/shelf-wrappers`. The drift test fails if any copy differs from its source, so a
change to `skills/deep-research/` cannot reach members through this pack by accident.

## Marketplace line to add (`.claude-plugin/marketplace.json`, `plugins` array)

```json
{
  "name": "shelf-deep-research",
  "source": "./plugins/shelf-deep-research",
  "version": "2.0.0",
  "description": "The shelf: run a multi-source research pass: scope the question, recon the sources, read them in parallel, run a critic pass, then write up with confidence labels."
}
```

The same object is in `MARKETPLACE_ENTRY.json`.

## Other shared-file changes

- `README.md` and `ROADMAP.md`: list `shelf-deep-research` under module 12: "Run a multi-source research pass: scope the question, recon the sources, read them in parallel, run a critic pass, then write up with confidence labels."
- CI: `python3 -m unittest discover -s tests/shelf-wrappers`.

## Shared skill name: `web-scrape` (Codex and Cursor)

Four packs carry a `web-scrape` copy (`shelf-web-scrape`, `shelf-deep-research`, `shelf-transcripts`,
`shelf-podcasts`), because their SKILL.md files call its scripts "from this plugin". Claude Code namespaces plugin
skills, so there is no clash there. `scripts/install_pack.py` links by skill name, so the second pack would stop with
"Existing skill preserved". `plugins/shelf-web-scrape/install_pack.diff` (tested in `tests/shelf-wrappers`) lets the
installer treat an already linked, byte-identical copy as installed. Apply it once, before merging any of the four.

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
the NAS: `lessons_v2/12-shelf-deep-research/`, `tutorials_v2/12-shelf-deep-research/`, `build-proof/shelf-deep-research/`.
