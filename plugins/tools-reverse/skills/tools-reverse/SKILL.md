---
name: tools-reverse
description: Explain how a shipped app, website bundle, Electron app or binary works using REA (the public rea-agents tool and its own skill), only inside a written scope the member is allowed to work in, with REA evidence behind every claim and unknowns kept separate. Use for "how does this website's calculator work", "what changed between these two versions", "what does this app send", "explain this binary".
---

# Reverse engineering with evidence, inside your scope

The member installs REA (`rea-agents` on npm, MIT, github.com/morluto/rea) with `npx rea-agents setup`, which registers
REA's MCP server with their agents and installs REA's own `reverse-engineer-anything` skill. Use that skill for the
tool details. This skill is how we run an investigation: scope first, then evidence, then a report a sceptic would accept.

## The command

Claude Code: `"${CLAUDE_PLUGIN_ROOT}/bin/tools-reverse"`. Codex and Cursor: `tools-reverse` (in `~/.local/bin`).

| Command | What it does |
|---|---|
| `doctor` | Node.js, the optional `rea` command, and REA's skill and registration. |
| `new <file> --target ... --question ...` | A scope and findings file. |
| `check <file>` | The scope has an owner and an allowed basis; every finding has evidence and a status. |
| `sample <folder>` | A practice investigation (a fictional Acme Studio price calculator). |

## Setup (once)

1. Node.js LTS (nodejs.org).
2. `npx rea-agents setup`: choose the agents, read the plan it shows, approve it, restart the agent.
3. Native apps need an engine REA supports (Ghidra, IDA or Hopper). Websites and JavaScript apps do not.
4. `doctor`.

## The method

1. **Scope first, always.** `new` the file and fill in whose it is and the basis: their own software, a public
   website, a licence that allows it, written permission, or interoperability where the law allows it. Run `check`.
   If there is no basis, stop and say so.
2. **Pick the cheapest evidence that answers the question.** A website or JavaScript app: static analysis of the
   shipped bundle. A desktop app: its packaged files first. Running a target and observing it is opt-in and only on
   the member's own machine and their own runs.
3. **Every claim gets evidence.** Cite REA's `evidence_id` (or file and offset) on each finding. Status:
   `observed` (REA saw it), `inferred` (follows from what it saw) or `unknown`. Never write "probably" on an observed line.
4. **Keep unknowns honest.** What the shipped files cannot show (server code, a database) goes under Unknowns with
   what would prove it.
5. **Check, then answer** from the file: what it does, how we know, what we do not know.

## Never

- Break or get round licence checks, DRM, logins, paywalls or rate limits.
- Attack, probe or load anyone's servers.
- Publish someone else's code or keys found in a bundle. If a secret turns up, tell the member to report it to the owner.
