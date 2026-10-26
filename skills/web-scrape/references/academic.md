# Academic — OpenAlex + Unpaywall (free, no key)

Scholarly search over **OpenAlex** (250M+ works) plus **Unpaywall** to find free,
legal PDFs of paywalled papers. Both APIs are free and unauthenticated. They reward
"polite pool" callers who identify with an email — set `OPENALEX_EMAIL` in
`~/.claude/.env`; otherwise a safe default (`research@navaigate.dev`) is used. No
secret involved.

Use Academic for the **research frontier and primary sources**: peer-reviewed and
preprint work, citation counts as a credibility signal, and the gap between what
papers claim and what practitioners report. A primary paper from 2022 beats AI
commentary on it from last week.

## CLI

```bash
A=~/.claude/skills/web-scraping/scripts/sources/academic.py

# Search OpenAlex; sort by relevance (default), cites, or date
python3 $A search "retrieval augmented generation evaluation" --limit 10 --from-year 2023 --sort cites
python3 $A search "small language models on-device" --oa --min-cites 10   # OA-only, well-cited

# One paper by DOI (or --id <openalex_id>)
python3 $A paper --doi 10.1038/s41586-023-06291-2

# Forward citations: works that cite a given OpenAlex ID
python3 $A citations "https://openalex.org/W..." --limit 20

# Find a free PDF for a DOI via Unpaywall
python3 $A pdf 10.1038/s41586-023-06291-2

# Full pipeline: search -> enrich paywalled hits with free PDFs (-> optional full text)
python3 $A research "AI code generation testing" --papers 5 --from-year 2024 --full-text
```

Add `--json` (before or after the subcommand) for the raw payload.

## What you get

Each paper: `title, abstract` (reconstructed from OpenAlex's inverted index),
`year, cited_by, doi, doi_url, open_access, oa_url, authors:[{name, institution}],
venue, type, openalex_id`. `research` adds `free_pdf_url` (Unpaywall) and, with
`--full-text`, `full_text` (scraped via this skill's `webscrape.py` → Firecrawl,
capped at 50k chars).

## Notes

- `--full-text` shells out to `webscrape.py scrape`, so it needs `FIRECRAWL_API_KEY`
  in `~/.claude/.env`. Search, paper, citations and PDF lookup need **no key at all**.
- OpenAlex `cited_by` is a fast, reliable credibility proxy — sort by `cites` to find
  the canonical works, by `date` to find the frontier.
- Citation graph: `citations` (forward) shows who built on a paper; `paper` returns
  `referenced_works_count` and `related_works` for backward/lateral traversal.
