# tools-research: integration notes for the chief of staff

## Overlap with the shelf research packs (other thread)

`shelf-web-scrape`, `shelf-deep-research` and `shelf-transcripts` (shelf-v2 stream, not on origin yet) already cover
Exa, Firecrawl, Supadata transcripts and the multi-source method. This pack ships only what they lack: OpenAlex papers,
Substack reading, Reddit on the member's own app, the YouTube consensus link, and a ledger check. It does not depend on
those packs (they are not on origin), and the skill names `shelf-web-scrape` for general web search.

## Where the pack came from

| Source | Owner and licence | What this pack took |
|---|---|---|
| `web-scraping` sources: `reddit.py`, `academic.py`, `substack.py` (our local skill) | Ours | The three source ideas and endpoints, rewritten small in the standard library with tests. |
| `web-scraping` `research-method.md` | Ours | The scope, recon, read, critic and confidence-label method, as the ledger and its check. |
| `consensus` (GoodLadTom/consensus) | GoodLadTom, MIT | Linked with the clone command. Not copied. |

## Changed from our version, and why

- **Reddit:** our keyless `.json` path returned HTTP 403 from this Mac on 26 October 2026. The member pack uses Reddit's
  official app-only OAuth with the member's own free app. Not tested live (no member app in the sandbox).
- **Our Composio Reddit route** (user id and our key) is left out: our account.
- **Polite email:** our default contact address is removed. OpenAlex works without one; members may add their own.
- **Substack search** needed Exa; members name the publication, or find it with their web search tool.
- **X search** (xAI) is left out: dormant and paid.

## Shared-file changes needed (I did not edit these)

1. **`.claude-plugin/marketplace.json`**: add `plugins/tools-research/MARKETPLACE_ENTRY.json`.
2. **`scripts/build_catalogue.py`**, `CAPABILITIES`: `'tools-research':['research papers','reddit','substack','sources','citations','what do people say']`.
3. **`README.md` and `ROADMAP.md`**: list `tools-research` under module 12, tools.
4. **Tests in CI**: `python3 -m unittest discover -s tests/tools-research`.
