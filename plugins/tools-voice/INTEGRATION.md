# tools-voice: integration notes for the chief of staff

## Where the pack came from

| Source | Owner and licence | What this pack took |
|---|---|---|
| `daniel-voice` (private) | Ours | The METHOD only: build from verbatim evidence, the read-aloud test, the de-slop list, the jargon ban, the no-metaphor rule, chained rhythm over fragments, proof over promises, and the calibration log as the authority. No profile, no quotes, no examples, no calibration entries, no name. |
| `voice-skill-builder` (skyremote, public) | Ours, MIT | Not copied. The pack finds the member's clone and runs its evidence script. |
| `your-voice` (1.x member skill) | Ours | Superseded for 2.0 members by this pack; it pointed at the same public kit. |

## Left out, and why

| Left out | Why |
|---|---|
| `daniel-voice`: PROFILE.md, EXAMPLES.md, the calibration log | Built from Daniel's 54 calls and his own edits. Never ships. |
| Daniel's trained ElevenLabs voice | Audio, and private. Narration is `tools-narration`, on the member's own clone. |

## Shared-file changes needed (I did not edit these)

1. **`.claude-plugin/marketplace.json`**: add `plugins/tools-voice/MARKETPLACE_ENTRY.json`.
2. **`scripts/build_catalogue.py`**, `CAPABILITIES`: `'tools-voice':['voice','my voice','writing style','sounds like ai','de-slop','tone']`.
3. **`README.md` and `ROADMAP.md`**: list `tools-voice` under module 12, tools.
4. **Tests in CI**: `python3 -m unittest discover -s tests/tools-voice`.

## Known limits

- The check catches words and shapes. Rhythm and truth still need the read-aloud test and the member's own edits.
- The adjective-stack rule looks at word endings, so it misses some stacks and flags few false ones.
