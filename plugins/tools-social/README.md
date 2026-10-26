# tools-social (AIOS 2.0, module 12: the shelf, tools)

One source, every platform, and nothing posts without your go. You use your own **Blotato** account (blotato.com),
connected to your own social accounts. This pack gives your agent our method: a checked post pack from one source,
then a release gate that only lets Blotato post on "publish now" or on a date, time and timezone you gave.

- **Your accounts.** Your Blotato key is stored in your keychain; the plugin connects Blotato's official MCP server.
- **Release gate.** A hook denies any Blotato post or reschedule without a matching release you gave.
- **Checked copy.** `tools-social check` catches over-long posts, missing hooks, placeholder links and comment-for-link
  promises with nothing behind them.

## Install

1. Install the start plugin `aios` first (module 1).
2. Create a Blotato account, connect your social accounts in it, and copy your API key (Settings, API).

**Claude Code:** `/aios install tools-social` (or `/plugin install tools-social@navaigate-aios`), `/reload-plugins`,
then `/plugin`, tools-social, Configure, and paste the key.

**Codex and Cursor**, from your checkout of this repository:
```
./install.sh tools-social
./install.sh tools-social --check
```
Then add Blotato's MCP yourself. Codex, in `~/.codex/config.toml`:
```
[mcp_servers.blotato]
url = "https://mcp.blotato.com/mcp"
http_headers = { "blotato-api-key" = "<your key>" }
```
Cursor: Settings, MCP, Add server, the same URL with the header `blotato-api-key`. Cursor runs the release gate as a
hook; Codex gets it as written guidance.

Needs Python 3.9 or later.

## Use

```
tools-social doctor
tools-social sample ~/Social-practice
tools-social check ~/Social-practice/northwind_posts_v1.json
tools-social release schedule --words "Tuesday at 9am London time" --at 2026-10-27T09:00 --tz Europe/London
```

Three starter prompts: [prompts.md](prompts.md). The method: [skills/tools-social/SKILL.md](skills/tools-social/SKILL.md).

## Licence

MIT. Blotato is a third-party service with its own terms.
