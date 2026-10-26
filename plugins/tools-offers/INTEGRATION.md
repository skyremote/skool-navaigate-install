# tools-offers: integration notes for the chief of staff

## Overlap with shelf-hormozi (other thread)

`shelf-hormozi` (worktree branch of the shelf-v2 stream, not on origin yet) wraps the 1.x `/hormozi` front door: it
points members to a Skool gold lesson. `tools-offers` is the "public tool plus our skill" version: it installs the
public engine, builds and checks the member's own corpus, points the engine at it, and routes jobs between the five
skills. Recommendation: ship `tools-offers`, and either retire `shelf-hormozi` or have it point here. Do not ship both
under module 12 without that decision.

## Where the pack came from

| Source | Owner and licence | What this pack took |
|---|---|---|
| `hormozi-growth-engine` (skyremote, public) | Ours, no licence file | Not copied. The member clones it and runs its installer. The corpus layout and the `<CORPUS_ROOT>` step come from its README; `corpus point` automates that step. |
| `ask-hormozi`, `grand-slam-offer-builder`, `offer-enhancer`, `lead-engine-planner`, `money-model-architect` (local) | Ours | The routing table only. The skills reach members through the public engine. |
| `james-smith` (skyremote, public) | Ours, no licence file | Linked with the clone command. |

## Left out, and why

| Left out | Why |
|---|---|
| Daniel's book corpus | Derived from copyrighted books. Never ships; each member builds their own. |
| Venture-specific offer examples | Private. The examples use the fictional Northwind Bakery. |

## Shared-file changes needed (I did not edit these)

1. **`.claude-plugin/marketplace.json`**: add `plugins/tools-offers/MARKETPLACE_ENTRY.json`.
2. **`scripts/build_catalogue.py`**, `CAPABILITIES`: `'tools-offers':['offer','pricing','hormozi','leads','guarantee','money model']`.
3. **`README.md` and `ROADMAP.md`**: list `tools-offers` under module 12, tools.
4. **Tests in CI**: `python3 -m unittest discover -s tests/tools-offers`.
