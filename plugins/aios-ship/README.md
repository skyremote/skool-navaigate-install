# aios-ship 2.0.0

Module 11 of YOUR AIOS 2.0: ship it to others. Depends on `aios`. Needs Python 3.9 or later.

## Install

Install the start plugin `aios` first (module 1). Then:

- Claude Code: type `/aios install the aios-ship pack`, or run `claude plugin install aios-ship@navaigate-aios`. Then `/reload-plugins`.
- Codex and Cursor, from your checkout of this repository: `./install.sh aios-ship`, then restart the harness.
  Codex and Cursor find `ship-pack` in `~/.local/bin`.

## What is inside

| Part | What it does |
|---|---|
| `/ship` | The layout, `plugin.json`, dependencies, secrets in `userConfig`, evals, marketplace, installers and versions |
| `/ship-pack` | Runs the scaffold with you and checks the result |
| `ship-pack new <name>` | A new pack with a skill, three eval cases, tests, `install.sh`, a changelog and a marketplace entry |
| `ship-pack from-skill <folder>` | Turns an existing skill into a pack; refuses if it holds a key or a personal home path |
| `ship-pack check <pack>` | Placeholders, secrets, home paths, skill length, evals and versions, with no network |
| `ship-pack bump <pack> patch\|minor\|major --note "..."` | Raises the version in `plugin.json`, the marketplace entry and the changelog together |
| `ship-pack marketplace <pack> --file <marketplace.json>` | Adds or updates the pack's entry in your marketplace |

## Learn it

`TOUR.md` is the step-by-step walkthrough that `/aios learn` follows in your own folder.

## Prove it

```
python3 -m unittest tests/aios-ship/test_ship.py
claude plugin validate plugins/aios-ship --strict
python3 tests/aios-methods/eval_lib_v1.py aios-ship
```

The three eval cases cover packaging a skill, keeping a member's key out of files, and releasing a fix.

The sandbox and eval runners write their evidence to `$AIOS_PROOF_DIR/<pack>/` (default `/tmp/aios-proof`), never into this repo.
