# aios-methods 2.0.0

Module 9 of YOUR AIOS 2.0: working methods. Depends on `aios`. Needs git and Python 3.9 or later.

## Install

Install the start plugin `aios` first (module 1). Then:

- Claude Code: type `/aios install the aios-methods pack`, or run `claude plugin install aios-methods@navaigate-aios`. Then `/reload-plugins`.
- Codex and Cursor, from your checkout of this repository: `./install.sh aios-methods`, then restart the harness.
  Codex and Cursor find `aios-methods` in `~/.local/bin`.

## What is inside

| Part | What it does |
|---|---|
| `/methods` | Picks the method for the job: `/loop`, a worktree, an interview, GSD or compound engineering |
| `/grill` | Interviews you one question at a time, then writes a spec and a glossary |
| `aios-methods worktree new/list/done` | A second folder on its own branch; refuses to remove anything unmerged or unsaved |
| `aios-methods glossary init/add/check` | One shared word list in `GLOSSARY.md` |
| `aios-methods spec new/check` | A short spec whose "Done when" lines are commands the agent can run |
| `aios-methods loop init` | A `.claude/loop.md` default prompt for bare `/loop` |

GSD Core and compound engineering are third-party projects under the MIT licence. This pack links
to them and gives their install commands in `skills/methods/references/third-party.md`. It copies none of their code.

## Learn it

`TOUR.md` is the step-by-step walkthrough that `/aios learn` follows in your own folder.

## Prove it

```
python3 -m unittest tests/aios-methods/test_methods.py
claude plugin validate plugins/aios-methods --strict
claude plugin eval plugins/aios-methods --runs 1
```

The three eval cases cover parallel work with a loop, interviewing before building, and the third-party installs.

The sandbox and eval runners write their evidence to `$AIOS_PROOF_DIR/<pack>/` (default `/tmp/aios-proof`), never into this repo.
