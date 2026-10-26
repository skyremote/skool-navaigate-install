# aios-bb 2.0.0

Module 4 of YOUR AIOS 2.0: bb (getbb.app) as the cockpit for your AIOS folder.

| Piece | What it is |
|---|---|
| `skills/bb-setup` | Install bb, add the AIOS folder as a bb project, create the four lanes, check bb is ready |
| `skills/bb-cockpit` | Threads, sections, the kanban, a worktree per thread, inline artifacts, slash commands, mods, the fleet |
| `skills/bb-daily` | The daily loop: start the day, hand work to threads, review, close |
| `bin/aios-bb` | The tool the skills run. Python 3.9+, standard library, talks only to your own `bb` CLI |

## Install

Install `aios` once (module 1). Then, in Claude Code, type `/aios`, say you are on module 4, and accept
`aios-bb`; type `/reload-plugins` afterwards. `/aios` runs `aios-guide install aios-bb`, which you can also type yourself.

Codex and Cursor, from your checkout of this repository:

```
./install.sh aios-bb
```

## Use

```
aios-bb doctor                       # is bb ready for this folder?
aios-bb setup --name "Acme Studio AIOS"
aios-bb today                        # start of day
aios-bb hand "Acme weekly report" --prompt-file brief.md --provider codex
aios-bb card review --note "Report ready"   # inside a thread
aios-bb close --archive-done         # end of day
```

It never deletes a project, a section or a thread. `close --archive-done` archives (it does not delete).

## Tests

`python3 -m unittest discover -s tests/aios-bb` from the repository root (uses a fake `bb`, no server needed).
