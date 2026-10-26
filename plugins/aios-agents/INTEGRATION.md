# Integration: aios-agents (stream C)

The chief of staff applies these changes to shared files. This stream did not edit them.

1. `.claude-plugin/marketplace.json`: append the object in `MARKETPLACE_ENTRY.json` to `plugins`.
2. `scripts/install_pack.py`: apply the one patch in `plugins/aios-skills/INTEGRATION.md`,
   section 2. It covers this pack too (links `bin/aios-agent` into `~/.local/bin`).
3. `plugins/aios/scripts/status.py`: map `aios-agents` to the skill `agent-or-not` for the
   Codex/Cursor link check (same section 3 of the aios-skills note).
4. `plugins/aios/skills/aios/SKILL.md`: list `aios-agents` as available once merged.
5. Root `README.md`: one row, `aios-agents`, module 7, "When a sub-agent earns its place, a brief, a small read-only crew".

Eval note for every pack that depends on `aios`: run from the repository root as
`claude plugin eval plugins --eval-dir <pack>/evals`, and list
`plugins: ["../..", "../../../aios"]` in each case. Otherwise the pack does not load in the
eval and the WITH arm silently runs without it (details in the aios-skills eval results, kept in the course build-proof folder).

## Kept out of the repo (Daniel, 26 October 2026)
The repository holds plugins, skills, tests, evals and install instructions only. These stay
outside it, in the course folders the chief of staff publishes from:
- `lessons/` (lesson Markdown and Skool HTML)
- `video/` (tutorial scripts, shot lists, SRTs, clips)
- `plugins/*/proof/` (eval results, sandbox install records, comparisons)
