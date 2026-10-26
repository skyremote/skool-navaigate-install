# aios-skills 2.0.0

Module 6 of YOUR AIOS 2.0: skills that earn their place. Depends on `aios`.
Python 3.9 or later, standard library only. No account, key or network request.

## What is in the pack

| Part | What it does |
|---|---|
| `skill-craft` skill | Decide if a job deserves a skill, write it short, measure it, hide the long tail, prove it with three evals |
| `new-skill` skill | Scaffold a skill with a short SKILL.md and three eval cases |
| `aios-skill new` | Creates `~/.claude/skills/<name>/` (or `--project`): SKILL.md, plugin manifest and `evals/` with should-fire, edge-case and should-not-fire cases. Never overwrites |
| `aios-skill check` | Checks description length and sentences, body under 500 lines, leftover `TODO:` markers and at least three eval cases. Exit 1 on an error |
| `aios-skill audit` | Lists personal and project skills by listing cost, with their `skillOverrides` state |
| `aios-skill hide` | Sets a skill to `on`, `name-only`, `user-invocable-only` or `off` in `skillOverrides`, with a backup |
| `examples/meeting-actions` | A finished example skill with three passing-style eval cases, used in the lesson |

## Install

Claude Code, once `aios` is installed (module 1):

```
/aios install aios-skills
```

It says what the pack adds, asks before installing, shows the proof, and then you type
`/reload-plugins`. The direct command is `/plugin install aios-skills@navaigate-aios`.

Codex and Cursor, from your checkout of this repository:

```
./install.sh aios-skills
./install.sh aios-skills --check
```

That links the two skills into `~/.codex/skills`, `~/.cursor/skills` and
`~/.agents/skills`, and `aios-skill` into `~/.local/bin`.

## First use

```
aios-skill new meeting-actions --description "Turn meeting notes into a numbered action list with one owner and one due date per line. Use when someone pastes notes and asks for the actions."
aios-skill check ~/.claude/skills/meeting-actions
claude plugin eval ~/.claude/skills/meeting-actions --runs 1 --no-publish
```

`claude plugin eval` runs each case with and without the skill and prints
`WITH`, `W/OUT` and `Δ`. Every run is a real model call on your own plan.
`/skill-doctor` and `skillOverrides` are Claude Code features; in Codex and
Cursor, use `aios-skill check` and `aios-skill audit`, and hide a skill by
removing its link.

## Proof

- Unit tests: `python3 -m unittest discover -s tests/aios-skills -v` from the repository root.
- `claude plugin validate plugins/aios-skills --strict`.
- Eval suite: `plugins/aios-skills/evals/` (write-a-skill, hide-long-tail, prove-it-works). Run it from
  the repository root: `claude plugin eval plugins --eval-dir aios-skills/evals --runs 1 --no-publish`.
- Sandbox install: `python3 tests/aios-skills/sandbox_proof_v1.py aios-skills <steps.json> <out.md>`.
  Eval results and sandbox records are build evidence, kept with the course material, not in this repository.
