# Integration: aios-verify (stream C)

The chief of staff applies these changes to shared files. This stream did not edit them.

1. `.claude-plugin/marketplace.json`: append the object in `MARKETPLACE_ENTRY.json` to `plugins`.
2. `scripts/install_pack.py`: apply the one patch in `plugins/aios-skills/INTEGRATION.md`,
   section 2. It covers this pack too (links `bin/aios-verify` into `~/.local/bin`).
   The installer does not add hooks to Codex or Cursor; members run `aios-verify init --git-hook`
   in each project instead.
3. `plugins/aios/scripts/status.py`: map `aios-verify` to the skill `verify-setup` for the
   Codex/Cursor link check.
4. `plugins/aios/skills/aios/SKILL.md`: list `aios-verify` as available once merged.
5. Root `README.md`: one row, `aios-verify`, module 8, "Checks, a Stop gate, REVIEW.md and a PR template, and hooks for three hard rules".

## Note for anyone with this pack enabled
The PreToolUse hook applies in every project while the plugin is enabled. It denies
destructive git and secret-carrying commits, and asks before production commands, including
`git push` to `main`. Merging this branch is done by the chief of staff by hand, outside an
agent session with this plugin enabled, or the push to `main` will ask first (as designed).

## Kept out of the repo (Daniel, 26 October 2026)
The repository holds plugins, skills, tests, evals and install instructions only. These stay
outside it, in the course folders the chief of staff publishes from:
- `lessons/` (lesson Markdown and Skool HTML)
- `video/` (tutorial scripts, shot lists, SRTs, clips)
- `plugins/*/proof/` (eval results, sandbox install records, gate demonstrations)
