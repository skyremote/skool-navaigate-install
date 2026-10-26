# aios-agents 2.0.0

Module 7 of YOUR AIOS 2.0: agents without sprawl. Depends on `aios`.
Python 3.9 or later, standard library only.

## What is in the pack

| Part | What it does |
|---|---|
| `agent-or-not` skill | When a sub-agent earns its place (parallel work, isolation, a context that would flood), the org-chart trap, and how to measure one loop against one loop plus a reviewer |
| `agent-brief` skill | Write and check a brief: measurable objective, format, tools, boundaries, stopping point |
| `agents/code-reviewer.md` | Read-only reviewer (Read, Grep, Glob). Reports findings with file and line, never edits |
| `agents/design-critic.md` | Read-only design critic (Read, Grep, Glob, WebFetch) for pages, slides and screenshots |
| `agents/researcher.md` | Researcher (WebSearch, WebFetch, Read, Grep, Glob) that returns a short cited answer |
| `templates/brief_v1.md` | The brief template |
| `aios-agent brief new` / `check` | Print or write the template; check a brief is ready to send (exit 1 if not) |
| `aios-agent compare` | Compare two `claude -p --output-format json` results: time, turns, tokens, cost, sub-agents |
| `aios-agent result` | Print the final reply of a `claude -p --output-format json` run, and which sub-agents it used |
| `aios-agent crew` | List the three agents and their tools |
| `examples/compare-task` | A small invoice task for the one-loop against reviewer comparison |

All three agents set `omitClaudeMd: true`, so they start from the brief rather than your
rules files, and `model: sonnet` with medium effort.

## Install

Claude Code:

```
/plugin marketplace add skyremote/skool-navaigate-install
/plugin install aios@navaigate-aios
/plugin install aios-agents@navaigate-aios
```

Codex and Cursor, from your checkout of this repository:

```
./install.sh aios
./install.sh aios-agents
```

That links the two skills and `aios-agent`. The three agent files are Claude Code plugin
agents; in Codex or Cursor, paste an agent file's body and your brief into a new chat.

## Proof

- Unit tests: `python3 -m unittest discover -s tests/aios-agents -v` from the repository root.
- `claude plugin validate plugins/aios-agents --strict`.
- Eval suite: `evals/` (department-crew, write-a-brief, small-change). Run it from the repository root:
  `claude plugin eval plugins --eval-dir aios-agents/evals --runs 1 --no-publish`.
- The comparison of one loop against one loop plus the reviewer: `examples/compare-task/TASK.md`.
  Results and sandbox records are build evidence, kept with the course material, not in this repository.
