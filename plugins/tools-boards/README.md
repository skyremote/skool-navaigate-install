# tools-boards (AIOS 2.0, module 12: the shelf, tools)

Whiteboards your team can actually move. You sign in to your own **BluPlai** account (bluplai.com), and this pack
gives your agent our method: plan the board as native shapes, zones and a few story arrows, validate it, write it
through BluPlai's MCP, and read it back to prove it landed.

- **Your account.** BluPlai signs you in through your browser. No key is stored by this pack.
- **Validated first.** `tools-boards validate` checks limits, overlaps and label fit before anything is written.
- **From a call.** Pair it with `tools-meetings` to turn a transcript into a board people can talk on.

## Install

1. Install the start plugin `aios` first (module 1).
2. Create a BluPlai account at bluplai.com.

**Claude Code:** `/aios install tools-boards` (or `/plugin install tools-boards@navaigate-aios`), then `/reload-plugins`.
The plugin connects `https://mcp.bluplai.com/mcp`; the first board you ask for opens BluPlai's sign-in.

**Codex and Cursor**, from your checkout of this repository:
```
./install.sh tools-boards
./install.sh tools-boards --check
```
Then add the MCP server yourself. Codex, in `~/.codex/config.toml`:
```
[mcp_servers.bluplai]
url = "https://mcp.bluplai.com/mcp"
```
Cursor: Settings, MCP, Add server, the same URL. Sign in when asked.

Needs Python 3.9 or later.

## Use

```
tools-boards sample ~/Boards-practice
tools-boards validate ~/Boards-practice/northwind-workshop_scene_v1.json --payload ~/Boards-practice/northwind-workshop.mcp.json --strict
```

Three starter prompts: [prompts.md](prompts.md). The method: [skills/tools-boards/SKILL.md](skills/tools-boards/SKILL.md).

## Licence

MIT. BluPlai is a product of NavAIgate with its own terms of service.
