# aios-harnesses 2.0.0

Module 3 of YOUR AIOS 2.0. One AIOS folder, four harnesses, the same rules, skills and MCP servers in each.

| Piece | What it is |
|---|---|
| `skills/harness-setup` | Installs what is missing, sets up the folder, adds MCP servers to every harness, and sets model and effort defaults |
| `skills/harness-check` | `/harness-check`: proves Claude Code, Codex, Cursor and Grok Bot see the same rules, skills and MCP servers, and prints what differs |
| `bin/harness` | The tool both skills run. Python 3.9+, standard library only, no network, no keys |

## Install

Claude Code:

```
/plugin marketplace add skyremote/skool-navaigate-install
/plugin install aios@navaigate-aios
/plugin install aios-harnesses@navaigate-aios
```

Codex and Cursor, from your checkout of this repository:

```
./install.sh aios
./install.sh aios-harnesses
```

## Use

```
cd <your-folder>
harness setup            # AGENTS.md, CLAUDE.md bridge, .aios/mcp.json, skill links
harness mcp add acme-notes -- npx -y @acme/notes-mcp
harness check            # exit 0 when every harness matches, 1 when something differs
harness grok             # what to paste into Grok Bot, and the probe prompt
harness defaults         # model and effort per harness
```

## What it writes

Only inside your AIOS folder (`AGENTS.md`, `CLAUDE.md`, `.aios/`, `.mcp.json`, `.codex/config.toml`,
`.cursor/mcp.json`, `.claude/settings.json` with `defaults --apply`) and symlinks in `~/.claude/skills`.
It never changes `~/.claude/settings.json`, `~/.codex/config.toml` or `~/.cursor/mcp.json`, and it never
overwrites a real folder or a file it did not write last without a backup.

## Tests

`python3 -m unittest discover -s tests/aios-harnesses` from the repository root.
