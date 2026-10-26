# Integration notes for aios-ship (stream D)

All shared-file changes for stream D are in `plugins/aios-methods/INTEGRATION.md`: the marketplace entries,
the `scripts/install_pack.py` patch that links this pack's `bin/ship-pack` into `~/.local/bin`, and the
`/aios` skill wording (module 11 is `aios-ship`, not `aios-ship-it`). Add `MARKETPLACE_ENTRY.json` from this
folder to `.claude-plugin/marketplace.json`.
