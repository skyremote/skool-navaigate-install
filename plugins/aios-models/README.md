# aios-models 2.0.0

Module 10 of YOUR AIOS 2.0: models, effort and cost. Depends on `aios`. Needs Python 3.9 or later.

## Install

Install the start plugin `aios` first (module 1). Then:

- Claude Code: type `/aios install the aios-models pack`, or run `claude plugin install aios-models@navaigate-aios`. Then `/reload-plugins`.
- Codex and Cursor, from your checkout of this repository: `./install.sh aios-models`, then restart the harness.
  Codex and Cursor find `models-check` in `~/.local/bin`.

## What is inside

| Part | What it does |
|---|---|
| `/models` | Which model does what, medium effort first, the advisor, usage, and two logins for failover |
| `/models-check` | Runs `models-check` and explains the result |
| `models-check` | Prints model, effort, advisor and login state for Claude Code, Codex, Cursor and the bb account pool. It prints no tokens, keys or email addresses |
| `models-check login add <label>` | Records a second Claude Code login in `~/.claude-<label>` and prints the sign-in command and alias |

## Learn it

`TOUR.md` is the step-by-step walkthrough that `/aios learn` follows in your own folder.

## Prove it

```
python3 -m unittest tests/aios-models/test_models.py
claude plugin validate plugins/aios-models --strict
python3 tests/aios-methods/eval_lib_v1.py aios-models
```

The three eval cases cover the effort default, a second login for failover, and pairing Sonnet with an Opus advisor.

The sandbox and eval runners write their evidence to `$AIOS_PROOF_DIR/<pack>/` (default `/tmp/aios-proof`), never into this repo.
