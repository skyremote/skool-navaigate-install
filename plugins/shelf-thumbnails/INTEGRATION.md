# shelf-thumbnails: integration notes for the chief of staff

## Where the pack came from

- **Source:** `skills/thumbnails/` at the repo root (the first-generation course skill). The pack ships a byte-for-byte copy.
- **This is a copy, not a link.** Symlinks break when Claude Code caches a plugin, so the files are real.
- The 1.x `skills/` folders are not moved or edited. First-generation members link to them.

| 1.x source | Copy inside this pack |
|---|---|
| `skills/thumbnails/` | `plugins/shelf-thumbnails/skills/thumbnails/` |

## The sync rule

When a 1.x skill changes, run `python3 tests/shelf-wrappers/sync_copies.py` to recopy it, then
`python3 -m unittest discover -s tests/shelf-wrappers`. The drift test fails if any copy differs from its source, so a
change to `skills/thumbnails/` cannot reach members through this pack by accident.

## Marketplace line to add (`.claude-plugin/marketplace.json`, `plugins` array)

```json
{
  "name": "shelf-thumbnails",
  "source": "./plugins/shelf-thumbnails",
  "version": "2.0.0",
  "description": "The shelf: make four on-brand video thumbnail concepts from your own photos, then add the headline as a real text layer so it is spelled correctly."
}
```

The same object is in `MARKETPLACE_ENTRY.json`.

## Other shared-file changes

- `README.md` and `ROADMAP.md`: list `shelf-thumbnails` under module 12: "Make four on-brand video thumbnail concepts from your own photos, then add the headline as a real text layer so it is spelled correctly."
- CI: `python3 -m unittest discover -s tests/shelf-wrappers`.

## Known limits

- Prompt 2 (four concepts) calls the Gemini image API. The only Gemini key on the build Mac was rejected (`API_KEY_INVALID`), so that step is not proven end to end; Claude stopped honestly and said so. Prompts 1 and 3 are proven. The sandbox photos are drawn placeholders, not a real person.
- The `userConfig` keys are stored by Claude Code in the keychain. The wrapped 1.x scripts read `~/.claude/.env` or the
  shell environment, not `CLAUDE_PLUGIN_OPTION_*`, and the copy must not be edited. The README therefore tells members
  to use `~/.claude/.env`.
- The skill text still says `/aios` at the end. Script paths are fixed (26 October 2026, in the 1.x skill and this
  copy alike): the skills name "the `scripts/` folder next to this SKILL.md" and the Python uses
  `Path(__file__).resolve().parent`, so they work from the plugin cache and from `~/.codex` and `~/.cursor` skill
  folders. `tests/shelf-wrappers` fails if a shipped file names the old first-generation install folder.

## Kept out of the repo (Daniel's ruling, 26 October 2026)

Lessons, tutorial scripts and build evidence (prompt proof, eval results, sandbox proof) live in the classroom folder on
the NAS: `lessons_v2/12-shelf-thumbnails/`, `tutorials_v2/12-shelf-thumbnails/`, `build-proof/shelf-thumbnails/`.
