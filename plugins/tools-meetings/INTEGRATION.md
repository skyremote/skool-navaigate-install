# tools-meetings: integration notes for the chief of staff

This is the first of the "tools" packs (module 12): the member installs the public tool on their own account, and
we give them our skill that uses it the way we do. Every tools pack is named `tools-<slug>`, its lesson lives in
`lessons_v2/12-tools-<slug>/`, and its build proof in `build-proof/tools-<slug>/` on the NAS.

## Where the pack came from

| Source | Owner and licence | What this pack took |
|---|---|---|
| `granola-transcripts` (our local skill) | Ours | The read-only API client (list, search, summary, transcript, turn merging), rewritten as a package with tests. Key lookup changed: shell variable, Claude Code plugin setting, or `~/.config/aios-tools/env` (0600). No key file under `~/.claude`. |
| `navaudit` (our local skill) | Ours | The method only: fact, inference, assumption and unknown; never invent an owner, a date or a number; cite the source. Rewritten as a Markdown decision record and a `check` command. |
| Granola | Third party, granola.ai | Not bundled. The member installs the app and creates their own API key. |

## Left out, and why

| Left out | Why |
|---|---|
| The NavAudit four-page HTML/PDF layout, its CSS and both logos (NavAIgate, a client) | House design and a client brand. |
| The worked example (a real client workshop) and the reference PDF | Client data. |
| Default names (`--me "Daniel"`) and the meeting titles in the old examples | Private. The default is `Me`. |
| Whisper transcription for any audio (`transcribe`) | A separate tool and key. A later pack if members ask. |

## Shared-file changes needed (I did not edit these)

1. **`.claude-plugin/marketplace.json`**: add `plugins/tools-meetings/MARKETPLACE_ENTRY.json`
   (`python3 scripts/build_catalogue.py --merge-entries` does this for every tools pack at once).
2. **`scripts/build_catalogue.py`**, `CAPABILITIES`: add
   `'tools-meetings':['meeting','meetings','granola','transcript','call notes','action items']`.
3. **`README.md` and `ROADMAP.md`**: list `tools-meetings` under module 12, tools: "Granola meetings on your own key,
   turned into checked decisions, owners and open questions."
4. **Tests in CI**: `python3 -m unittest discover -s tests/tools-meetings`.

## Known limits

- Granola's API needs a Business or Enterprise plan. The sample call teaches the method without it.
- Granola does not name the other people in a transcript; the pack labels them `Others`.
- The owner check matches names as text. It cannot tell two people with the same first name apart.
