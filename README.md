# YOUR AIOS 2.0

Start with **aios**. Check what you have, follow the next module, and install one
pack when you need it. Phase 1 includes **aios** and **aios-brain**.

The lessons and tutorial videos for every module are in the YOUR AIOS classroom on
Skool (members only). This repo holds the plugins, the skills and the instructions to
install them. The first-generation (v1) bundle stays at its original `skills/`,
`references/` and `templates/` paths, with the `skool-navaigate-install` catalogue
entry retained. A v1 member can pull this branch without breaking their skill
links. **V1 receives fixes-only support for six months, until 26 April 2027.**
No member is migrated automatically. The old manifest retains its original
0.1.0 version; “v1” describes that generation. See [ROADMAP.md](ROADMAP.md) for the twelve modules and every old skill.

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
It refuses conflicting skills, commands, custom Codex brain tables and
symlinked config files, preserving dotfiles links. It locks its config edits and
re-reads both files before writing, stopping if another process changed them. Review the reported paths if it stops. Restart the
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
Capture honours `CLAUDE_CONFIG_DIR` and `CODEX_HOME`. Only new or changed files
are imported; changed sessions replace messages atomically and retain any saved
digest and title. Refresh a saved digest explicitly after the session changes.
A malformed interior line remains an error. If only the final line is cut off
and the file has been idle for five minutes, valid turns are saved with a warning.
Files are hashed and parsed as streams; unchanged health checks use a stored
fingerprint without parsing the transcript again.

`status` checks file hashes and actual messages, shows newest stored/session
messages and file modification times separately, and reports failures. It exits
**1** when unhealthy, including an installed harness with zero sessions in its
configured folders. Fresh append-only changes to an already captured active
session have a two-minute grace window; continued writes cannot restart that
window. Claude Code defaults to 30-day session retention; the health check reads
`cleanupPeriodDays` and warns at about two-thirds of it, with days left. A recent job timestamp proves nothing
about whether text was stored.

## Optional: your second machine

Use your own empty Turso database and database token. You own the account and data.
For Claude Code's MCP tools, configure optional `turso_url` and sensitive
`turso_token` with `/plugin configure aios-brain@navaigate-aios`. The token is a
keychain value. Shell installs do not open the enable-time configuration dialog;
leave both options blank to stay local.

The MCP server receives these values in its environment for tools that need
configuration. **Search and read always use the local database**, even offline
or if remote credentials are invalid. Sync runs only during capture or an
explicit `brain sync`. **Terminal commands** in any
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

Capture also syncs when shell configuration is present. Sync first reads paged
`ref`, `updated` and `sha256` metadata, then fetches only changed payloads in
bounded chunks. A remote failure never prevents local search/read. There is no scheduler
in phase 1: run capture/sync on each machine when needed. HTTP transactions,
message-before-hash ordering, full payload read-back and local/primary content
comparison replace CLI success markers and embedded-replica heartbeats.
FTS indexes remain local; Turso stores session/media/digest bundles. The local index is not sent to Turso; remote catalogue pages contain only
small metadata rows.


## Existing v1 member: guided, optional move

Run `/aios` to detect old skill links and review the choice. Continue v1 if you
prefer; its paths and marketplace ID remain available until 26 April 2027.
For a reviewed Codex/Cursor move, explicitly run:

```sh
./install.sh aios --migrate-v1
./install.sh aios-brain
```

The first command preserves the three conflicting v1 start links under
`~/.local/share/aios/v1-backups/` before linking the new start skill. It does not
delete anything, touch the Claude v1 skill, or change the other v1 tools. Without
the flag a conflict stops the installer. With no arguments, `./install.sh` still
runs the v1 installer. Claude Code can install the new namespaced plugins beside
the old `skool-navaigate-install` plugin.

## Credential handling and clearing failures

**Common credentials are redacted before storage, indexing, recall or sync:**
provider key prefixes, JWTs, bearer values, private-key blocks and credential
assignments such as `api_key=…` or `password: …`. This is best-effort pattern
matching, not a guarantee for every arbitrary secret. Avoid pasting credentials
into chats. Known process credential values are redacted too; existing local
text from the earlier build is scrubbed on upgrade. yt-dlp receives no brain or
API credentials; Claude digest subprocesses receive only the environment needed
for the member's own subscription, never the Turso or Supadata credentials.
Whitespace/control characters in token input are rejected without echoing them.

Invalid refs and URLs are input errors, not permanent health failures. Failures
for session files that no longer exist are removed from the failure list.
Review and explicitly acknowledge an old operational failure with:

```sh
brain failures list
brain failures clear --scope sync
```

`--all` can acknowledge the entire failure list. It never deletes captured data
or makes a still-missing session or an unhealthy remote connection pass health.

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
Build evidence (sandbox runs, checks, eval results) is kept with the course
materials, outside this repo.

To repeat the fictional local proof in a **fresh** sandbox:

```sh
python3 scripts/sandbox_proof_v1.py
```

This helper hard-codes `/tmp/aios-member-sandbox`; move a previous sandbox aside
before rerunning. It never uses your real harness configuration.

Step-by-step tutorial videos for each module are in the Skool classroom.

MIT.
