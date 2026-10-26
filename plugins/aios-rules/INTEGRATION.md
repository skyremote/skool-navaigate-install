# aios-rules: changes needed in shared files

This stream does not edit shared files. The chief of staff applies these when merging.
The sandbox install proof (`tests/aios-rules/sandbox_proof_v1.py`) and the core-installer test are described below.

## 1. `.claude-plugin/marketplace.json`
Add the object in `MARKETPLACE_ENTRY.json` to `plugins`, after `aios`.

## 2. `scripts/install_pack.py`: no change needed after `aios2/core` merges
The core thread's installer (`origin/aios2/core`, commit 053d118) lists every pack under `plugins/`, installs a
pack's `dependencies` first and links every executable in its `bin/` into `~/.local/bin`. Tested on 26 October
2026 in a throwaway HOME with this branch plus that installer: `./install.sh aios-rules` linked `aios` and both
`aios-rules` skills into Codex, Cursor and `.agents`, linked `~/.local/bin/aios-rules`, and exited 0.
The earlier `INTEGRATION.diff` for the phase 1 installer is withdrawn.

## 3. `plugins/aios/scripts/status.py`
Line 67: `'available_packs':['aios','aios-brain']` becomes `['aios','aios-rules','aios-brain']`.

## 4. `plugins/aios/skills/aios/SKILL.md`
"Only `aios` and `aios-brain` ship in phase 1." becomes
"`aios`, `aios-rules` and `aios-brain` ship now." Leave the rest unchanged.

## 5. `README.md`
In the opening paragraph, "Phase 1 includes **aios** and **aios-brain**." becomes
"Ready now: **aios**, **aios-rules** and **aios-brain**." Add `./install.sh aios-rules` to the
Codex and Cursor block, between `aios` and `aios-brain`.

## 6. `ROADMAP.md`
Module 2 row, last column: "Planned: AGENTS.md, short rules, CLAUDE.md bridge" becomes
"Shipped for local review: folder map, AGENTS.md starter, CLAUDE.md bridge, path-scoped rules, budget check, monthly audit".

## 7. Kept out of the repo
Course content and build evidence live in the classroom folders, not in Git (Daniel, 26 October 2026):
- `lessons/`: the Skool lessons for modules 1, 2 and 5;
- `video/`: tutorial scripts, tapes, shot lists, SRTs and clips;
- `plugins/*/proof/`: sandbox install and eval proof notes.
The proof scripts in `tests/aios-rules/` take `--out <folder>` and refuse a folder inside the repository.
