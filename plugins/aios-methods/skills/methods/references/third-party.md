# Third-party methods: links, installs and licences

Checked on 26 October 2026. These projects belong to their authors. This pack links to them
and gives their own install commands. It copies none of their code or prompts.

## GSD Core (Get Shit Done)

- Started by glittercowboy as `get-shit-done`. That repository is now archived.
  The project continues as GSD Core: https://github.com/open-gsd/gsd-core
- Licence: MIT.
- Install (needs Node.js): `npx @opengsd/gsd-core@latest`. The installer asks which harness
  (Claude Code, Codex, Cursor and others) and whether to install globally or in this project.
  Do not copy files from its folders by hand: its README says the installer is required.
- Start: `/gsd-new-project` for a new project, `/gsd-onboard` for an existing codebase.
- The loop, one phase at a time: discuss, plan, execute, verify, ship.
- Use it when: a project has several phases and you want a roadmap, state files and fresh-context
  workers for each plan. It is heavier than one interview and one spec, so skip it for a one-day feature.

## Compound engineering (Every)

- Repository: https://github.com/EveryInc/compound-engineering-plugin
- Licence: MIT.
- Install in Claude Code:
  - `/plugin marketplace add EveryInc/compound-engineering-plugin`
  - `/plugin install compound-engineering`
- Install in Cursor: in Agent chat, `/add-plugin compound-engineering`.
- Install in the Codex CLI:
  - `codex plugin marketplace add EveryInc/compound-engineering-plugin`
  - `codex plugin add compound-engineering@compound-engineering-plugin`
  - In Codex, call its skills with `$`, for example `$ce-plan`.
- The loop: brainstorm (`/ce-brainstorm`), plan (`/ce-plan`), work (`/ce-work`), review,
  then compound (`/ce-compound`), which writes what you learned into `docs/solutions/`
  so the next plan reads it.
- Use it when: you fix the same kind of problem more than once and want each fix written down.

## Matt Pocock's skills (the original "grill me")

- Repository: https://github.com/mattpocock/skills
- Licence: MIT.
- Install in Claude Code: `claude plugin install mattpocock-skills@claude-plugins-official`.
- Install for Cursor and others: `npx skills@latest add mattpocock/skills -a cursor`.
- `/grill-me` interviews you about a plan. `/grill-with-docs` also keeps a `GLOSSARY.md` and
  decision records. This pack's `/grill` is our own short version of the same idea, written for
  the AIOS spec and glossary files. Install one or the other, not both, to keep the skill list short.

## Built into the harnesses (nothing to install)

- `/loop` and scheduled tasks: https://code.claude.com/docs/en/scheduled-tasks
- Claude Code worktrees: `claude -w <name>` (see `claude --help`).
- Codex worktrees: `codex --worktree`.
- Cursor CLI worktrees: `cursor-agent -w <name>`, created under `~/.cursor/worktrees/<repo>/<name>`.
