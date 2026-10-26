# tools-boards: integration notes for the chief of staff

## Where the pack came from

| Source | Owner and licence | What this pack took |
|---|---|---|
| `bluplai-native-whiteboards` (our local skill) | Ours | The skill (renamed), `design-language.md`, `mcp-contracts.md`, the teaching-workflow example and `validate_scene.py` (now callable with arguments), with its tests. It held no private data. |
| `board-wall` (our local skill) | Ours | The conversation method only: read the whole transcript, quote real lines, leave a marked space to write back, end on a decision. |
| BluPlai MCP (`https://mcp.bluplai.com/mcp`) | Our product, hosted | Connected in `.mcp.json`. Sign-in is BluPlai's own browser flow; no key in `userConfig`. |

## Left out, and why

| Left out | Why |
|---|---|
| board-wall's example (a client hackathon feedback wall) and its screenshots | Client material. |
| board-wall's sketch icons and their source sketches | Daniel's own drawings and house style. |
| `bluplai-ingest` (customers, projects and entities in BluPlai) | Needs BluPlai's customer features and real client data to demonstrate; a later pack if members ask. |

## Shared-file changes needed (I did not edit these)

1. **`.claude-plugin/marketplace.json`**: add `plugins/tools-boards/MARKETPLACE_ENTRY.json`.
2. **`scripts/build_catalogue.py`**, `CAPABILITIES`: `'tools-boards':['whiteboard','bluplai','workshop board','feedback wall','diagram board']`.
3. **`README.md` and `ROADMAP.md`**: list `tools-boards` under module 12, tools.
4. **Tests in CI**: `python3 -m unittest discover -s tests/tools-boards`.

## Known limits

- Not tested against a live BluPlai account in the sandbox (no member account there; a test board in our account was
  not wanted). The scene format and limits are the ones our skill uses in production.
