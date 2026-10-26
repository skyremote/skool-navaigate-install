# Sandbox member install proof v2

Paths are normalised as <worktree> and $HOME for portability. All commands use HOME=/tmp/aios-member-sandbox and CLAUDE_CONFIG_DIR=$HOME/.claude.
The working directory is the review checkout. Fixtures are fictional. No real member data or tokens are used.

```sh
claude --version
```
```text
2.1.310 (Claude Code)
[exit 0]
```

```sh
claude plugin validate plugins/aios --strict
```
```text
Validating plugin manifest: <worktree>/plugins/aios/.claude-plugin/plugin.json

Plugin directory checks for <worktree>/plugins/aios. The plugin directory is the catalog that plugins are submitted to; this is a subset of what it runs.

⚠ Found 1 plugin directory warning:

  ❯ .claude-plugin/plugin.json icon: No icon (ICON_MISSING). No icon found in the plugin. The validator looked for `icon` in plugin.json and for a file at .claude-plugin/icon.png or .svg, assets/icon.png or .svg, or a similar path.
    Fix: Add a square PNG to the plugin folder at .claude-plugin/icon.png, or set `icon` in plugin.json to the path of a square PNG or JPEG in the plugin: 512 to 2048 px on each side, under 2 MB. SVG and WebP are not accepted. That file may become the listing icon only once: the first time the plugin is saved or submitted in the developer portal. Adding or changing it later does not change the icon.

These plugin directory checks do not change the result below.

The directory also runs a safety scan and a policy review that this command does not.

ℹ Advice (does not change the verdict):

  ❯ <worktree>/plugins/aios/README.md: This README has no line that installs "aios" from a marketplace. Add the install line, which works in one step on Claude Code 2.1.275 or later. Validate the folder that holds its marketplace.json to have <owner>/<repo> filled in, and the name its marketplace lists it under.
      /plugin install aios --marketplace <owner>/<repo>

✔ Validation passed
[exit 0]
```

```sh
claude plugin validate ./ --strict
```
```text
Validating marketplace manifest: <worktree>/.claude-plugin/marketplace.json

Plugin directory checks for <worktree>. The plugin directory is the catalog that plugins are submitted to; this is a subset of what it runs.

⚠ Found 1 plugin directory warning:

  ❯ .claude-plugin/plugin.json icon: No icon (ICON_MISSING). No icon found in the plugin. The validator looked for `icon` in plugin.json and for a file at .claude-plugin/icon.png or .svg, assets/icon.png or .svg, or a similar path.
    Fix: Add a square PNG to the plugin folder at .claude-plugin/icon.png, or set `icon` in plugin.json to the path of a square PNG or JPEG in the plugin: 512 to 2048 px on each side, under 2 MB. SVG and WebP are not accepted. That file may become the listing icon only once: the first time the plugin is saved or submitted in the developer portal. Adding or changing it later does not change the icon.

About these checks:

  ❯ This folder also holds a marketplace manifest. The plugin directory treats such a folder as a plugin, so these checks cover only the plugin in this folder. To check another plugin that the marketplace lists, run validate on that plugin's folder.

These plugin directory checks do not change the result below.

The directory also runs a safety scan and a policy review that this command does not.

ℹ Advice (does not change the verdict):

  ❯ <worktree>/README.md: This README has no line that installs "skool-navaigate-install" from a marketplace. Add the install line, which works in one step on Claude Code 2.1.275 or later. In it, replace <owner>/<repo> with the repository that holds the marketplace.
      /plugin install skool-navaigate-install --marketplace <owner>/<repo>

✔ Validation passed
[exit 0]
```

```sh
claude plugin validate plugins/aios-brain --strict
```
```text
Validating plugin manifest: <worktree>/plugins/aios-brain/.claude-plugin/plugin.json

Plugin directory checks for <worktree>/plugins/aios-brain. The plugin directory is the catalog that plugins are submitted to; this is a subset of what it runs.

⚠ Found 1 plugin directory warning:

  ❯ .claude-plugin/plugin.json icon: No icon (ICON_MISSING). No icon found in the plugin. The validator looked for `icon` in plugin.json and for a file at .claude-plugin/icon.png or .svg, assets/icon.png or .svg, or a similar path.
    Fix: Add a square PNG to the plugin folder at .claude-plugin/icon.png, or set `icon` in plugin.json to the path of a square PNG or JPEG in the plugin: 512 to 2048 px on each side, under 2 MB. SVG and WebP are not accepted. That file may become the listing icon only once: the first time the plugin is saved or submitted in the developer portal. Adding or changing it later does not change the icon.

These plugin directory checks do not change the result below.

The directory also runs a safety scan and a policy review that this command does not.

ℹ Advice (does not change the verdict):

  ❯ <worktree>/plugins/aios-brain/README.md: This README has no line that installs "aios-brain" from a marketplace. Add the install line, which works in one step on Claude Code 2.1.275 or later. Validate the folder that holds its marketplace.json to have <owner>/<repo> filled in, and the name its marketplace lists it under.
      /plugin install aios-brain --marketplace <owner>/<repo>

✔ Validation passed
[exit 0]
```

```sh
claude plugin validate .claude-plugin/marketplace.json --strict
```
```text
Validating marketplace manifest: <worktree>/.claude-plugin/marketplace.json

✔ Validation passed
[exit 0]
```

```sh
claude plugin marketplace add <worktree>
```
```text
Adding marketplace…✔ Successfully added marketplace: navaigate-aios (declared in user settings)
[exit 0]
```

```sh
claude plugin install aios@navaigate-aios
```
```text
Installing plugin "aios@navaigate-aios"...✔ Successfully installed plugin: aios@navaigate-aios (scope: user)
[exit 0]
```

```sh
claude plugin install aios-brain@navaigate-aios
```
```text
Installing plugin "aios-brain@navaigate-aios"...✔ Successfully installed plugin: aios-brain@navaigate-aios (scope: user)
2 userConfig options not yet set — run /plugin configure aios-brain@navaigate-aios in Claude Code, or pass --config KEY=VALUE.
[exit 0]
```

```sh
claude plugin list --json
```
```text
[
  {
    "id": "aios-brain@navaigate-aios",
    "version": "2.0.0",
    "scope": "user",
    "enabled": true,
    "installPath": "/tmp/aios-member-sandbox/.claude/plugins/cache/navaigate-aios/aios-brain/2.0.0",
    "readFromFolder": "<worktree>/plugins/aios-brain",
    "folderVersion": "2.0.0",
    "installedAt": "2026-10-26T09:59:36.916Z",
    "lastUpdated": "2026-10-26T09:59:36.916Z",
    "mcpServers": {
      "aios-brain": {
        "command": "${CLAUDE_PLUGIN_ROOT}/bin/brain",
        "args": [
          "mcp"
        ],
        "env": {
          "AIOS_BRAIN_TURSO_URL": "${user_config.turso_url}",
          "AIOS_BRAIN_TURSO_TOKEN": "${user_config.turso_token}"
        }
      }
    },
    "projectEnabled": false,
    "hasUserConfig": true
  },
  {
    "id": "aios@navaigate-aios",
    "version": "2.0.0",
    "scope": "user",
    "enabled": true,
    "installPath": "/tmp/aios-member-sandbox/.claude/plugins/cache/navaigate-aios/aios/2.0.0",
    "readFromFolder": "<worktree>/plugins/aios",
    "folderVersion": "2.0.0",
    "installedAt": "2026-10-26T09:59:36.282Z",
    "lastUpdated": "2026-10-26T09:59:36.282Z",
    "projectEnabled": false
  }
]
[exit 0]
```

```sh
python3 scripts/sandbox_config_v1.py seed
```
```text
Seeded unrelated fictional MCP entries.
[exit 0]
```

```sh
./install.sh aios
```
```text
Linked .codex/skills/aios
Linked .cursor/skills/aios
Linked .agents/skills/aios
Installed aios 2.0.0. Restart Codex and Cursor. Add ~/.local/bin to PATH for brain.
[exit 0]
```

```sh
./install.sh aios-brain
```
```text
Configured .codex/config.toml; backup config.toml.backup-1793008778227999000
Configured .cursor/mcp.json; backup mcp.json.backup-1793008778228486000
Linked .codex/skills/brain
Linked .cursor/skills/brain
Linked .agents/skills/brain
Linked .local/bin/brain
Installed aios-brain 2.0.0. Restart Codex and Cursor. Add ~/.local/bin to PATH for brain.
[exit 0]
```

```sh
python3 scripts/sandbox_fixtures_v1.py --home /tmp/aios-member-sandbox
```
```text
Wrote 3 fictional session files.
[exit 0]
```

```sh
/tmp/aios-member-sandbox/.local/bin/brain init
```
```text
{
  "initialised": true,
  "database": "/tmp/aios-member-sandbox/.local/share/aios-brain/brain.db",
  "mode": "local; no account needed"
}
[exit 0]
```

```sh
/tmp/aios-member-sandbox/.local/bin/brain status
```
```text
{
  "healthy": false,
  "session_files": 3,
  "files_by_harness": {
    "claude": 1,
    "codex": 1,
    "cursor": 1
  },
  "active_files": [],
  "active_grace_seconds": 120,
  "newest_session_file": {
    "name": "fictional-cursor.jsonl",
    "modified": 1793008778.2631822
  },
  "newest_session_message": 1793008800.0,
  "newest_stored_message": null,
  "newest_message_all_machines": null,
  "pending_files": [
    "fictional-claude.jsonl",
    "fictional-codex.jsonl",
    "fictional-cursor.jsonl"
  ],
  "problems": [
    "3 session file(s) not captured; run brain capture"
  ],
  "failures": [],
  "warnings": [
    "Claude Code retention is 30 days. Capture regularly; keep the database off cloud-sync folders.",
    "No verified capture time recorded yet; run brain capture."
  ],
  "mode": "local"
}
[exit 1]
```

```sh
/tmp/aios-member-sandbox/.local/bin/brain capture
```
```text
{
  "captured": 3,
  "unchanged": 0,
  "messages": 6,
  "skipped_subagents": 0,
  "failures": [],
  "warnings": [],
  "sync": {
    "mode": "local",
    "network": "off"
  }
}
[exit 0]
```

```sh
/tmp/aios-member-sandbox/.local/bin/brain capture
```
```text
{
  "captured": 0,
  "unchanged": 3,
  "messages": 0,
  "skipped_subagents": 0,
  "failures": [],
  "warnings": [],
  "sync": {
    "mode": "local",
    "network": "off"
  }
}
[exit 0]
```

```sh
/tmp/aios-member-sandbox/.local/bin/brain search 'Lighthouse budget'
```
```text
{
  "hits": [
    {
      "ref": "claude:4fb3a9c25acb:fictional-claude",
      "kind": "message",
      "title": "",
      "timestamp": 1793008800.0,
      "score": 3.133247719148103,
      "snippet": "The fictional [Lighthouse] launch [budget] is 2400 pounds. Use the blue invitation."
    }
  ]
}
[exit 0]
```

```sh
/tmp/aios-member-sandbox/.local/bin/brain read claude:4fb3a9c25acb:fictional-claude
```
```text
{
  "ref": "claude:4fb3a9c25acb:fictional-claude",
  "title": "",
  "text": "user: Plan the Lighthouse launch.\n\nassistant: The fictional Lighthouse launch budget is 2400 pounds. Use the blue invitation.",
  "total_chars": 125,
  "next_start": null
}
[exit 0]
```

```sh
/tmp/aios-member-sandbox/.local/bin/brain status
```
```text
{
  "healthy": true,
  "session_files": 3,
  "files_by_harness": {
    "claude": 1,
    "codex": 1,
    "cursor": 1
  },
  "active_files": [],
  "active_grace_seconds": 120,
  "newest_session_file": {
    "name": "fictional-cursor.jsonl",
    "modified": 1793008778.2631822
  },
  "newest_session_message": 1793008800.0,
  "newest_stored_message": 1793008800.0,
  "newest_message_all_machines": 1793008800.0,
  "pending_files": [],
  "problems": [],
  "failures": [],
  "warnings": [
    "Claude Code retention is 30 days. Capture regularly; keep the database off cloud-sync folders."
  ],
  "mode": "local"
}
[exit 0]
```

```sh
python3 plugins/aios/scripts/status.py
```
```text
{
  "v1": {
    "skills_by_harness": {
      "claude": [],
      "codex": [],
      "cursor": [],
      "agents": []
    },
    "marketplace_plugin_installed": false,
    "support_until": "2027-04-26",
    "policy": "Fixes only; no automatic migration",
    "guided_move": "Keep v1 or review ./install.sh aios --migrate-v1; preserve old links in backups after the member confirms"
  },
  "packs": [
    {
      "pack": "aios",
      "harnesses": {
        "claude": {
          "installed": true,
          "files_present": true,
          "enabled": true
        },
        "codex": {
          "skills_present": true,
          "receipt_version": "2.0.0"
        },
        "cursor": {
          "skills_present": true,
          "receipt_version": "2.0.0"
        },
        "agents": {
          "skills_present": true,
          "receipt_version": "2.0.0"
        }
      }
    },
    {
      "pack": "aios-brain",
      "harnesses": {
        "claude": {
          "installed": true,
          "files_present": true,
          "enabled": true
        },
        "codex": {
          "skills_present": true,
          "receipt_version": "2.0.0"
        },
        "cursor": {
          "skills_present": true,
          "receipt_version": "2.0.0"
        },
        "agents": {
          "skills_present": true,
          "receipt_version": "2.0.0"
        }
      }
    }
  ],
  "harness_commands": {
    "claude": true,
    "codex": true,
    "cursor": true
  },
  "rules_present": false,
  "next_module": 1,
  "next_title": "Start here",
  "progress_basis": "Only member-confirmed modules in ~/.local/share/aios/progress.json count. Installed does not mean completed.",
  "available_packs": [
    "aios",
    "aios-brain"
  ],
  "errors": []
}
[exit 0]
```

```sh
python3 scripts/sandbox_config_v1.py verify
```
```text
Both unrelated MCP entries and both backups verified.
[exit 0]
```

```sh
python3 scripts/sandbox_mcp_v1.py
```
```text
Server command: ["/tmp/aios-member-sandbox/.local/bin/brain", "mcp"]
{"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2025-06-18", "capabilities": {"tools": {}}, "serverInfo": {"name": "aios-brain", "version": "2.0.0"}}}
{"jsonrpc": "2.0", "id": 2, "result": {"tools": [{"name": "brain_search", "description": "Search your captured messages, digests and video captions using BM25 and recency. Returns refs for brain_read.", "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}, "limit": {"type": "integer", "minimum": 1, "maximum": 50}, "recency": {"type": "boolean"}}, "required": ["query"], "additionalProperties": false}}, {"name": "brain_read", "description": "Open a search ref. Long items return next_start; pass it as start for the next part.", "inputSchema": {"type": "object", "properties": {"ref": {"type": "string"}, "start": {"type": "integer", "minimum": 0}, "max_chars": {"type": "integer", "minimum": 1, "maximum": 60000}}, "required": ["ref"], "additionalProperties": false}}, {"name": "brain_media_add", "description": "Fetch and store one YouTube transcript. Tries free captions first; paid Supadata only with your own configured key. Does not digest automatically.", "inputSchema": {"type": "object", "properties": {"url": {"type": "string"}, "refresh": {"type": "boolean"}}, "required": ["url"], "additionalProperties": false}}]}}
{"jsonrpc": "2.0", "id": 3, "result": {"content": [{"type": "text", "text": "{\"hits\": [{\"ref\": \"cursor:4fb3a9c25acb:fictional-cursor\", \"kind\": \"message\", \"title\": \"\", \"timestamp\": 1793008800.0, \"score\": 3.5905325214021504, \"snippet\": \"[Juniper] uses a [navy] heading and a cream background.\"}]}"}]}}
MCP handshake, inventory and fictional search verified through the installed server command.
[exit 0]
```

```sh
codex --version
```
```text
codex-cli 0.164.0
[exit 0]
```

```sh
codex mcp list
```
```text
Name        Command                                    Args  Env  Cwd  Status   Auth
aios-brain  /tmp/aios-member-sandbox/.local/bin/brain  mcp   -    -    enabled  Unsupported
fictional   fictional-server                           -     -    -    enabled  Unsupported
[exit 0]
```

## Result

PASS: all expected exit codes, search/read and backup assertions passed.

This proves installation and the local CLI flow. Harness reload and live remote Turso/paid media/subscription digest use are separate checks.
