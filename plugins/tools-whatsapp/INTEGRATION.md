# tools-whatsapp: integration notes for the chief of staff

## Where the pack came from

| Source | Owner and licence | What this pack took |
|---|---|---|
| `whatscribe` (GoodLadTom/whatscribe) | GoodLadTom, MIT | Not copied. The member clones and installs it. Its `transcript.jsonl` fields (`at`, `who`, `type`, `text`) are what `find` and `extract` read. |
| Our `whatscribe` skill notes | Ours | The safe-sending rules (confirm every send, `--dry-run` to test), the voice-note backlog advice, and reading `transcript.jsonl` for structured questions. |

## Left out, and why

| Left out | Why |
|---|---|
| Our private chat corpus repository and its daily publish-to-GitHub schedule | Private chats; and pushing chats to git is unsafe advice for members. |
| The contractor "daily manager brief" | About a named person in our team. |
| Any chat names, numbers or exports | Private. The sample chat is fictional. |

## Shared-file changes needed (I did not edit these)

1. **`.claude-plugin/marketplace.json`**: add `plugins/tools-whatsapp/MARKETPLACE_ENTRY.json`.
2. **`scripts/build_catalogue.py`**, `CAPABILITIES`: `'tools-whatsapp':['whatsapp','voice notes','chat archive','whatscribe']`.
3. **`README.md` and `ROADMAP.md`**: list `tools-whatsapp` under module 12, tools.
4. **Tests in CI**: `python3 -m unittest discover -s tests/tools-whatsapp`.

## Known limits

- `extract` finds amounts, dates and times by pattern. It lists candidates with their message; the agent still reads
  the message before stating a figure.
