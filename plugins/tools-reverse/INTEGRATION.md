# tools-reverse: integration notes for the chief of staff

## Where the pack came from

| Source | Owner and licence | What this pack took |
|---|---|---|
| REA (`rea-agents`, github.com/morluto/rea) | Third party, MIT | Not bundled. `npx rea-agents setup` registers its MCP server and installs its own skill. |
| `reverse-engineer-anything` (installed on our Macs) | REA's own skill | Not copied: it is the vendor's, kept current by REA's setup. Its evidence rules (cite `evidence_id`, keep unknowns, static differences are candidates) shaped our check. |

## Why no `.mcp.json`

REA's setup writes the MCP registration for each agent and keeps it in step with its skill. Shipping a second
registration here would duplicate it and pin a stale version.

## Left out

Nothing private: our use of REA holds no NavAIgate data. Our own investigation files are not included.

## Shared-file changes needed (I did not edit these)

1. **`.claude-plugin/marketplace.json`**: add `plugins/tools-reverse/MARKETPLACE_ENTRY.json`.
2. **`scripts/build_catalogue.py`**, `CAPABILITIES`: `'tools-reverse':['reverse engineer','how does this app work','decompile','rea','binary']`.
3. **`README.md` and `ROADMAP.md`**: list `tools-reverse` under module 12, tools.
4. **Tests in CI**: `python3 -m unittest discover -s tests/tools-reverse`.
