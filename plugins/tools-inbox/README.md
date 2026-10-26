# tools-inbox (AIOS 2.0, module 12: the shelf, tools)

Inbox triage that never sends. You connect your own Gmail inside your own **Composio** account (composio.dev) and
add Composio's MCP server to your harness. This pack gives your agent our method: sort the inbox into Action needed,
Waiting on and FYI, write a one-line draft for each reply, and send nothing.

- **Your account, your inbox.** Composio is a public service with a free tier. Your connection stays yours.
- **Never sends.** A hook blocks every MCP tool that sends, replies or forwards email. Drafts are allowed.
- **Checked.** `tools-inbox check` fails a brief that is missing a sender, a date or a subject, or that claims a send.
- **Reminders to yourself.** `tools-inbox remind` emails only your own address; any other address is refused.

## Install

1. Install the start plugin `aios` first (module 1).
2. At composio.dev: create an account, connect Gmail (and Google Calendar if you want), and create an MCP server URL
   for them. Treat the URL like a password.
3. Add the URL to your harness yourself:
   - Claude Code: `claude mcp add --transport http composio-gmail "<your URL>"`
   - Codex: in `~/.codex/config.toml` add `[mcp_servers.composio-gmail]` with `url = "<your URL>"`
   - Cursor: Settings, MCP, Add server, paste the URL.

**Claude Code:** `/aios install tools-inbox` (or `/plugin install tools-inbox@navaigate-aios`), then `/reload-plugins`.
For reminders, open `/plugin`, tools-inbox, Configure, and paste your Composio API key.

**Codex and Cursor**, from your checkout of this repository:
```
./install.sh tools-inbox
./install.sh tools-inbox --check
```
For reminders, `export COMPOSIO_API_KEY=...` in your shell profile. Codex gets the never-send rule as written
guidance (Codex does not run Claude Code hooks); Cursor gets the hook.

Needs Python 3.9 or later.

## Use

```
tools-inbox doctor
tools-inbox sample ~/Inbox-practice
tools-inbox check ~/Inbox-practice/inbox-brief_practice_v1.md
tools-inbox accounts
tools-inbox remind --subject "Invoices day" --body "Send October's invoices" --yes
tools-inbox schedule --cron "0 8 * * 1" --subject "Invoices day" --body "Send October's invoices"
```

Three starter prompts: [prompts.md](prompts.md). The method: [skills/tools-inbox/SKILL.md](skills/tools-inbox/SKILL.md).
Optional sorting at volume with Jev: [skills/tools-inbox/references/jev.md](skills/tools-inbox/references/jev.md).

## Licence

MIT. Composio, Gmail and TypeSafe (Jev) are third-party services with their own terms. The Jev skill
(`dbreunig/building-with-jev-skill`) is linked, not copied.
