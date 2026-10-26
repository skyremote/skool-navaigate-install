# tools-images: integration notes for the chief of staff

## Where the pack came from

| Source | Owner and licence | What this pack took |
|---|---|---|
| `higgsfield-generate`, `-product-photoshoot`, `-marketplace-cards`, `-soul-id` | Higgsfield (`higgsfield-ai/skills`), MIT | Not copied. These are Higgsfield's own published skills; the member installs them from Higgsfield. |
| Higgsfield CLI (`higgsfield-ai/cli`) | Higgsfield, MIT | Not bundled. The install line is given. |
| `video-prompt-builder` (our local skill) | Ours | The four-section video prompt method and the shot counts by length, rewritten as a reference and a `check` command. |

## Left out, and why

| Left out | Why |
|---|---|
| Our Soul characters, character ids, saved prompts and reference images | Daniel's likeness and our assets. |
| `nav-seedance` and `sirio-seedance` | Built on a named third party's methodology; the member download already exists separately. |
| `seedance-setup` and `seedance-unrestricted` (Enhancor API) | A second paid provider and our account; Higgsfield covers Seedance for members. |
| `daniel-images` | Daniel's portraits. |

## Shared-file changes needed (I did not edit these)

1. **`.claude-plugin/marketplace.json`**: add `plugins/tools-images/MARKETPLACE_ENTRY.json`.
2. **`scripts/build_catalogue.py`**, `CAPABILITIES`: `'tools-images':['image','images','ai video','higgsfield','seedance','product photo']`.
3. **`README.md` and `ROADMAP.md`**: list `tools-images` under module 12, tools.
4. **Tests in CI**: `python3 -m unittest discover -s tests/tools-images`.
