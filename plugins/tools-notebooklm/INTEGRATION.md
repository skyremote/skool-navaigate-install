# tools-notebooklm: integration notes for the chief of staff

## Where the pack came from

| Source | Owner and licence | What this pack took |
|---|---|---|
| `notebooklm` (our local skill) | Ours | The command map and workflow, cleaned: no absolute paths, no "already signed in" assumption, no notebook ids. |
| notebooklm-py (teng-lin/notebooklm-py) | Third party, MIT, unofficial | Not bundled. The member installs it with pipx and signs in themselves. |

## Left out, and why

| Left out | Why |
|---|---|
| Our CLI path, our sign-in state file and "do not ask to log in" rule | Our machine and account. |
| Our Obsidian vault filing step | Our vault. |
| The sales-research workflow naming our companies and a past client | Private. |

## Shared-file changes needed (I did not edit these)

1. **`.claude-plugin/marketplace.json`**: add `plugins/tools-notebooklm/MARKETPLACE_ENTRY.json`.
2. **`scripts/build_catalogue.py`**, `CAPABILITIES`: `'tools-notebooklm':['notebooklm','audio overview','podcast','quiz','flashcards','study guide']`.
3. **`README.md` and `ROADMAP.md`**: list `tools-notebooklm` under module 12, tools.
4. **Tests in CI**: `python3 -m unittest discover -s tests/tools-notebooklm`.

## Known limits

- notebooklm-py is unofficial; a NotebookLM change can break it until its author updates it.
- The plan uses NotebookLM's free-plan limits (50 sources a notebook, 500,000 words or 200 MB a source); check
  NotebookLM's own help if those change.
