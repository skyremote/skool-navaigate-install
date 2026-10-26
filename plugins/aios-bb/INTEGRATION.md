# Integration notes for aios-bb

The shared-file changes for this pack are written once, in `plugins/aios-harnesses/INTEGRATION.md`:
the marketplace entry (from `MARKETPLACE_ENTRY.json` here), the `scripts/install_pack.py` patch (it links
`bin/aios-bb` into `~/.local/bin`), the `/aios` skill line, and the note that evals skip packs with `dependencies`.

The kanban: Daniel's own board plugin is private and unlicensed, so this pack does not ship it. Members get the
four lanes as bb sidebar sections, and `aios-bb card` uses any plugin that adds a `bb kanban` command with the
columns backlog, in-progress, review and done. If Daniel publishes his board plugin, add it to the bb-setup skill.

Kept out of the repo: lessons, tutorial files and proof notes (see aios-harnesses INTEGRATION.md, section 7).
The sandbox proof needs a separate bb server; `tests/aios-bb/sandbox_proof.py` explains how it is pointed at one.
