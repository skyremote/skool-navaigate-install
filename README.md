# YOUR AIOS 2.0

Start with **aios**. Check what you have, follow the next module, and install one
pack when you need it. Phase 1 includes **aios** and **aios-brain**.

This is an unpublished review branch. No release or marketplace update has been
made. The old bundle is preserved in `legacy/v1/` and git history; it is not
loaded by the 2.0 marketplace. Existing installations are not migrated by this
checkout. See [ROADMAP.md](ROADMAP.md) for the twelve modules and every old skill.

## Claude Code: local review install

Requires Claude Code with plugin dependencies and userConfig support (verified
with 2.1.310), plus Python 3.9+ with SQLite FTS5. From this checkout:

```sh
claude plugin marketplace add ./
claude plugin install aios@navaigate-aios
```

Restart Claude Code and type `/aios` (or `/aios:aios` when namespaced). It asks
whether your machine is empty, halfway or already running, checks packs across
harnesses, and gives you the next step. The brain is optional:

```sh
claude plugin install aios-brain@navaigate-aios
```

`aios-brain` declares `aios` as its dependency. It contains `bin/`, so this pack
is for Claude Code on your computer; claude.ai and Cowork skip it.

After Daniel approves and publishes, the marketplace-add command will be
`/plugin marketplace add skyremote/skool-navaigate-install`. That GitHub command
still resolves to the old public version until release. Do not use it to review 2.0.

## Codex and Cursor

From this checkout:

```sh
./install.sh aios
./install.sh aios-brain
export PATH="$HOME/.local/bin:$PATH"
```

The installer links only the named pack's skills into `~/.codex/skills`,
`~/.cursor/skills` and `~/.agents/skills`. Install `aios` before a dependent pack.
It does not write Claude Code configuration. The brain command is linked to
`~/.local/bin/brain`. Keep the checkout where it is: these are links, not copies.

For the brain it merges an `aios-brain` MCP server into `~/.codex/config.toml`
and `~/.cursor/mcp.json`, backing up each file first. Other server entries stay.
It refuses conflicting skills, commands or custom Codex brain tables, and never
silently replaces them. Review the reported paths if it stops. Restart the
harness to load the links and server.

## Your first memory

```sh
brain init
brain capture
brain search "a topic from your work"
brain read REF_FROM_SEARCH
brain status
```

Local mode makes no network requests and needs no account. One database,
`~/.local/share/aios-brain/brain.db`, holds your captured text and FTS5 index.
Do not put it in a NAS or cloud-sync folder. Back it up as your own private data.

Capture reads top-level user and assistant turns from Claude Code JSONL, Codex
current/archived JSONL and Cursor agent-transcript JSONL or role-labelled TXT.
Cursor history stored only in its native application database needs a transcript
export first. Tool payloads, sub-agent forks and harness instructions are excluded.
Only new or changed files are imported; changed sessions replace their indexed
messages atomically. Partial or malformed files remain pending and are reported.

`status` checks file hashes and actual messages, shows newest stored/session
messages and file modification times separately, and reports failures. It exits
**1** when unhealthy. An empty fresh brain is labelled as having no captured
history; it does not prove capture works. Claude Code deletes session files
after 30 days, so run capture regularly. A recent job timestamp proves nothing
about whether text was stored.

## Optional: your second machine

Use your own empty Turso database and database token. You own the account and data.
For Claude Code's MCP tools, configure optional `turso_url` and sensitive
`turso_token` with `/plugin configure aios-brain@navaigate-aios`. The token is a
keychain value. Shell installs do not open the enable-time configuration dialog;
leave both options blank to stay local.

The MCP server receives these values in its environment; search, read and media
calls exchange captured data when configured. **Terminal commands** in any
harness use exported environment variables or this private file:

```sh
mkdir -p ~/.config/aios-brain
touch ~/.config/aios-brain/env
chmod 600 ~/.config/aios-brain/env
```

Edit that file privately, putting your own values against these names:

```text
AIOS_BRAIN_TURSO_URL=libsql://YOUR_DATABASE.turso.io
AIOS_BRAIN_TURSO_TOKEN=YOUR_DATABASE_TOKEN
```

Do not paste the token into a chat or commit the file. Install the same pack on
the second machine, configure your own database there, then run:

```sh
brain init
brain capture
brain sync
brain status
```

Capture also syncs when shell configuration is present. There is no scheduler
in phase 1: run capture/sync on each machine when needed. HTTP transactions,
message-before-hash ordering, full payload read-back and local/primary content
comparison replace CLI success markers and embedded-replica heartbeats.
FTS indexes remain local; Turso stores session/media/digest bundles. This is a
small initial sync design which reads the remote catalogue on each sync.

## Optional: video captions and digests

Install `yt-dlp` for free English YouTube captions, then:

```sh
brain media add "https://www.youtube.com/watch?v=VIDEO_ID"
```

If free captions fail, it stops. Paid transcription is enabled only when you set
your own `SUPADATA_API_KEY` in the private env file or process environment.

No digest runs automatically. To opt in for one item:

```sh
brain digest REF_FROM_SEARCH
```

This uses `claude -p --model haiku` on your signed-in Claude subscription. API
credentials and provider routes are removed; a subscription login is required.
It stores a generic summary, questions and atoms. No shared accounts or user data
are included. Very long items are refused instead of silently summarised in part.

The stdio MCP server exposes `brain_search`, `brain_read` and `brain_media_add`.
`brain mcp` starts it; the plugin and installer wire it to the harness.

## Checks and review evidence

```sh
python3 -m unittest discover -s tests -v
claude plugin validate plugins/aios --strict
claude plugin validate plugins/aios-brain --strict
claude plugin validate .claude-plugin/marketplace.json --strict
claude plugin eval plugins/aios-brain --trust-plugin --no-publish
```

Run evals under an isolated HOME using your own subscription login. The three
cases compare against a no-plugin baseline. No real MCP servers start in these
advice cases. The proof records an authentication block separately from scores.
See `proof/sandbox-run_v1.md`, `proof/checks_v1.md`, `proof/eval-results_v1.md` and
`proof/compatibility_v1.md` for actual results and limitations.

To repeat the fictional local proof in a **fresh** sandbox:

```sh
python3 scripts/sandbox_proof_v1.py
```

This helper hard-codes `/tmp/aios-member-sandbox`; move a previous sandbox aside
before rerunning. It never uses your real harness configuration.

Ordered tutorial clips, real terminal stills and VHS tapes are in `video/`.
`video/SHOTLIST_v1.md` gives each command, view and narration sentence.
These are raw materials for later 3–10 minute landscape NavMotion tutorials
narrated in Daniel's voice; this phase does not make those finished films.
Nothing has been pushed, tagged, submitted or published.

MIT.
