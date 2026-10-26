# Claude Code compatibility evidence v1

Tested with Claude Code 2.1.310. All writes use a separate empty /tmp HOME.

```sh
claude plugin marketplace add .
```
```text
✘ Invalid marketplace source format. Try: owner/repo, https://..., or ./path
[exit 1]
```

```sh
claude plugin marketplace add ./
```
```text
Adding marketplace…✔ Successfully added marketplace: navaigate-aios (declared in user settings)
[exit 0]
```

```sh
claude plugin install aios-brain@navaigate-aios
```
```text
Installing plugin "aios-brain@navaigate-aios"...✔ Successfully installed plugin: aios-brain@navaigate-aios (scope: user) (+ 1 dependency: aios)
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
    "installPath": "/tmp/aios-dependency-proof_v1/.claude/plugins/cache/navaigate-aios/aios-brain/2.0.0",
    "readFromFolder": "/Users/sky/.bb/plugins/environment-git-worktree/host-data/worktrees/thr_a8ducu6yie-1/skool-navaigate-install/plugins/aios-brain",
    "folderVersion": "2.0.0",
    "installedAt": "2026-10-26T07:33:19.489Z",
    "lastUpdated": "2026-10-26T07:33:19.489Z",
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
    "installPath": "/tmp/aios-dependency-proof_v1/.claude/plugins/cache/navaigate-aios/aios/2.0.0",
    "readFromFolder": "/Users/sky/.bb/plugins/environment-git-worktree/host-data/worktrees/thr_a8ducu6yie-1/skool-navaigate-install/plugins/aios",
    "folderVersion": "2.0.0",
    "installedAt": "2026-10-26T07:33:19.494Z",
    "lastUpdated": "2026-10-26T07:33:19.494Z",
    "projectEnabled": false
  }
]
[exit 0]
```

## Findings

`marketplace add .` is rejected by this CLI. `marketplace add ./` and an absolute checkout path work. Documentation and tapes use those forms.

Installing only aios-brain also installs and enables aios. The manifests use the tested bare dependency name.

A shell plugin install does not show the userConfig dialog. Both optional options can be left unset for local mode; configure them later for MCP sync. No non-empty sensitive values were entered.

userConfig substitutions reach the MCP environment. Do not assume a terminal command receives them; the CLI also supports the private env file. Exported hook option names are uppercase.

Strict validation succeeds. The listing directory check warns that square listing icons are absent; it says this check does not change the validation result.

The installed CLI exposes evals with a no-plugin baseline and --no-publish. All three eval attempts are blocked by the empty sandbox not having a subscription login; see eval-results_v1.md.

The local-path marketplace loads plugin source from this checkout in place. Keep the checkout present; plugin list readFromFolder is the source authority even if installPath names an absent cache folder.

References: [manifest/userConfig and bin layout](https://code.claude.com/docs/en/plugins-reference), [eval suite format](https://code.claude.com/docs/en/plugin-evals). The CLI probes above are the evidence for this build.

The optional integrations use the primary specifications: [Turso HTTP v2 batch protocol](https://github.com/tursodatabase/libsql/blob/main/docs/HTTP_V2_SPEC.md) and [Supadata transcript endpoint](https://github.com/supadata-ai/skills/blob/main/skills/supadata/references/video.md). These references confirm protocol shapes; they are not a live-account test.
