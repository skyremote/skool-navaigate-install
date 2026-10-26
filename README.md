# YOUR AIOS 2.0

Install **one thing**: the start pack `aios`. It works straight away. It knows every
pack in this repository (its module, dependencies, hooks, MCP servers and settings),
installs what you need when you need it, and teaches each module inside your own
folder, one checked step at a time.

The lessons and tutorial videos for every module are in the YOUR AIOS classroom on
Skool (members only). This repository holds the plugins, the skills and the
instructions to install them. Nothing else.

## Install

### Claude Code

```sh
claude plugin marketplace add skyremote/skool-navaigate-install
claude plugin install aios@navaigate-aios
```

In an open session, type `/reload-plugins` (or restart). Then type `/aios`
(or `/aios:aios` if Claude Code shows it namespaced). It asks whether your
machine is empty, halfway or already running, and gives you one next step.

Reviewing before release? GitHub still serves the old version, so add your
local clone instead: `claude plugin marketplace add ./` from the clone.

### Codex and Cursor

```sh
git clone https://github.com/skyremote/skool-navaigate-install.git
cd skool-navaigate-install
./install.sh aios
export PATH="$HOME/.local/bin:$PATH"
```

Restart Codex or Cursor. In Cursor, type `/aios` in the Agent chat. In Codex, type
`$aios` (Codex calls a skill by name with `$`), or ask "use the aios skill". The first
run records where your clone lives, so the skill can install every later pack from any folder.
Keep the clone where it is: the installer links to it, it does not copy.

The bb kit keeps its own copy in `~/.local/share/aios/kit`. If you use both, install packs with
`aios-guide install <pack>`, which uses the copy AIOS recorded. To move AIOS to your own clone instead, run
`./install.sh <pack> --use-this-checkout` there: it keeps the old links in a backup.

## Build it step by step

`/aios` installs each pack when you reach its module, or when you ask for a
capability ("set up my brain"). It uses the same command in every harness:

```sh
aios-guide next                     # what you have and the one next step
aios-guide list                     # every pack and its module
aios-guide install aios-brain       # install a pack and its dependencies, then prove it
aios-guide verify aios-brain        # prove it again at any time
aios-guide learn 1                  # walk a module's tour inside your folder
```

In Claude Code, `/aios` runs `claude plugin install <pack>@navaigate-aios`.
Claude Code installs the pack's dependencies with it. Type `/reload-plugins` after.

In Codex (`$aios`) and Cursor (`/aios`), the skill runs `install.sh <pack>` from your clone. The
installer installs dependencies first, in order, once each. It stops on a
dependency cycle and writes nothing until every check passes. Running it twice
changes nothing. `./install.sh <pack> --check` proves a pack is in place, and
`./install.sh <pack> --dry-run` shows what it would change.

### The whole framework in one go

```sh
claude plugin install aios-complete@navaigate-aios   # Claude Code
./install.sh aios-complete                            # Codex and Cursor
```

`aios-complete` installs `aios`, `aios-brain` and every core pack for modules
2 to 11. Shelf packs (module 12) stay optional.

## Hooks in each harness

- **Claude Code** runs a pack's hooks itself. `aios-guide verify <pack>` checks
  they are active (`claude plugin details <pack>`).
- **Cursor:** the installer merges a pack's hooks into `~/.cursor/hooks.json`.
  It backs the file up first, keeps every existing entry, and never adds a hook
  twice. It tells you about any hook that has no Cursor event.
- **Codex:** the installer writes the same rule into `~/.codex/AGENTS.md`, in a
  marked block. Codex does not enforce it: it is a written rule only.

## What each pack touches (Codex and Cursor)

- Skills: linked into `~/.codex/skills`, `~/.cursor/skills` and `~/.agents/skills`.
- Commands in a pack's `bin/`: linked into `~/.local/bin`.
- MCP servers: merged into `~/.codex/config.toml` and `~/.cursor/mcp.json`.
- Hooks: as above.

Every config file is backed up before a change. Other entries stay. The
installer refuses to replace a skill or command it did not create, and it
preserves symlinked (dotfiles) config files. It locks its config edits and
re-reads each file before writing, stopping if another program changed it.
Claude Code configuration is never written by `install.sh`.

## The packs

`plugins/aios/catalogue.json` lists every pack. It is generated:

```sh
python3 scripts/build_catalogue.py --merge-entries   # after merging a new pack
python3 scripts/build_catalogue.py --check           # in CI: exit 1 if anything is stale
```

The generator copies each pack's `MARKETPLACE_ENTRY.json` into the marketplace,
adds its module number, keeps `aios-complete`'s dependency list equal to the
core packs, and fails when the catalogue and the marketplace disagree.
See [ROADMAP.md](ROADMAP.md) for the twelve modules.

## v1 members

The first-generation (v1) bundle stays at its original `skills/`, `references/`
and `templates/` paths, with the `skool-navaigate-install` marketplace entry.
A v1 member can pull this repository without breaking their skill links.
**V1 receives fixes-only support until 26 April 2027.** No member is moved
automatically. `./install.sh` with no arguments still runs the v1 installer.

### v1: the guided, optional move

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

## Release (maintainers)

`scripts/release_tags.sh --dry-run` lists every pack whose `plugin.json` version
has no `<pack>--v<version>` git tag. Without `--dry-run` it creates them with
`claude plugin tag`. Version ranges such as `^2.0` resolve against these tags.

## Tests

```sh
python3 -m unittest discover -s tests
for p in plugins/*/ ./ .claude-plugin/marketplace.json; do claude plugin validate "$p" --strict; done
```

## The brain (module 5)

Requires Python 3.9+ with SQLite FTS5. Install it with
`aios-guide install aios-brain`. `aios-brain` contains `bin/`, so it is for
Claude Code on your computer; claude.ai and Cowork skip it.

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
AIOS_BRAIN_TURSO_URL=YOUR_DATABASE_URL_FROM_turso_db_show_--url
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
