# Checks v1

Historical phase-1 evidence for ffddffb; superseded by the v2 review-fix proof.

All harness CLI checks use the isolated member HOME.

```sh
python3 -m unittest discover -s tests -v
```
```text
test_all_harnesses_capture_and_unchanged (test_brain.BrainCase) ... ok
test_bm25_strong_old_match_survives_recency (test_brain.BrainCase) ... ok
test_change_replaces_removed_messages_and_fts (test_brain.BrainCase) ... ok
test_cli_status_exits_one_when_unhealthy (test_brain.BrainCase) ... ok
test_codex_first_meta_and_subagents (test_brain.BrainCase) ... ok
test_config_half_pair_and_private_permissions (test_brain.BrainCase) ... ok
test_cursor_text_export (test_brain.BrainCase) ... ok
test_digest_subscription_only_and_no_automatic_digest (test_brain.BrainCase) ... ok
test_digest_validates_output_and_removes_api_credentials (test_brain.BrainCase) ... ok
test_failure_recovers_only_after_success (test_brain.BrainCase) ... ok
test_harness_noise_and_tools_absent (test_brain.BrainCase) ... ok
test_invalid_json_does_not_advance_hash (test_brain.BrainCase) ... ok
test_local_mode_does_not_use_network (test_brain.BrainCase) ... ok
test_mcp_exact_schema_and_round_trip (test_brain.BrainCase) ... ok
test_media_capture_and_idempotency (test_brain.BrainCase) ... ok
test_media_fallback_requires_own_key (test_brain.BrainCase) ... ok
test_media_rejects_non_video_and_insecure_urls (test_brain.BrainCase) ... ok
test_query_is_literal_and_limits_bounded (test_brain.BrainCase) ... ok
test_read_pagination_has_no_lost_text (test_brain.BrainCase) ... ok
test_recency_breaks_equal_relevance_tie (test_brain.BrainCase) ... ok
test_status_30_day_warning (test_brain.BrainCase) ... ok
test_status_detects_missing_message_even_with_real_hash (test_brain.BrainCase) ... ok
test_status_does_not_treat_recent_heartbeat_as_health (test_brain.BrainCase) ... ok
test_status_pending_new_file_and_newest_message (test_brain.BrainCase) ... ok
test_status_same_mtime_changed_file (test_brain.BrainCase) ... ok
test_strong_old_bm25_match_beats_weak_recent_match (test_brain.BrainCase) ... ok
test_transaction_rolls_back_messages_and_hash (test_brain.BrainCase) ... ok
test_existing_arrays_after_our_table_are_preserved (test_brain.InstallerTests) ... ok
test_foreign_skill_is_preserved_and_brain_needs_real_start_pack (test_brain.InstallerTests) ... ok
test_sandbox_install_backup_and_no_other_skill_links (test_brain.InstallerTests) ... ok
test_toml_unrelated_entries_preserved (test_brain.InstallerTests) ... ok
test_inventory_reports_each_harness_without_completing_lessons (test_brain.StartStatusTests) ... ok
test_http_200_error_is_not_success_and_token_not_printed (test_brain.SyncTests) ... ok
test_readback_failure_surfaces_despite_successful_write (test_brain.SyncTests) ... ok
test_transaction_missing_commit_rejected (test_brain.SyncTests) ... ok
test_transport_never_forwards_a_token_on_redirect (test_brain.SyncTests) ... ok
test_two_machines_exchange_and_verify_actual_contents (test_brain.SyncTests) ... ok

----------------------------------------------------------------------
Ran 37 tests in 1.059s

OK
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
vhs validate 'video/tapes/*_v1.tape'
```
```text

[exit 0]
```

```sh
python3 video/check_clips_v1.py
```
```text
[
  {
    "file": "video/clips/01_install-aios.mp4",
    "seconds": 27.76,
    "width": 1920,
    "height": 1080
  },
  {
    "file": "video/clips/02_install-brain.mp4",
    "seconds": 23.52,
    "width": 1920,
    "height": 1080
  },
  {
    "file": "video/clips/03_install-aios-codex-cursor.mp4",
    "seconds": 15.12,
    "width": 1920,
    "height": 1080
  },
  {
    "file": "video/clips/04_install-brain-codex-cursor.mp4",
    "seconds": 28.48,
    "width": 1920,
    "height": 1080
  },
  {
    "file": "video/clips/05_init-brain.mp4",
    "seconds": 16.44,
    "width": 1920,
    "height": 1080
  },
  {
    "file": "video/clips/06_prepare-demo-sessions.mp4",
    "seconds": 17.64,
    "width": 1920,
    "height": 1080
  },
  {
    "file": "video/clips/07_capture-sessions.mp4",
    "seconds": 20.6,
    "width": 1920,
    "height": 1080
  },
  {
    "file": "video/clips/08_repeat-capture.mp4",
    "seconds": 16.72,
    "width": 1920,
    "height": 1080
  },
  {
    "file": "video/clips/09_search-memory.mp4",
    "seconds": 21.56,
    "width": 1920,
    "height": 1080
  },
  {
    "file": "video/clips/10_read-memory.mp4",
    "seconds": 25.44,
    "width": 1920,
    "height": 1080
  },
  {
    "file": "video/clips/11_check-health.mp4",
    "seconds": 25.64,
    "width": 1920,
    "height": 1080
  },
  {
    "file": "video/clips/12_verify-claude-code.mp4",
    "seconds": 22.76,
    "width": 1920,
    "height": 1080
  },
  {
    "file": "video/clips/13_verify-codex.mp4",
    "seconds": 22.52,
    "width": 1920,
    "height": 1080
  },
  {
    "file": "video/clips/14_verify-cursor-config.mp4",
    "seconds": 15.04,
    "width": 1920,
    "height": 1080
  },
  {
    "file": "video/clips/15_check-all-harnesses.mp4",
    "seconds": 71.24,
    "width": 1920,
    "height": 1080
  }
]
[exit 0]
```

## Scope checks

All 28 old skill directories have a row in ROADMAP.md. The old source is preserved, not installed by the new marketplace.

Both plugins and the marketplace pass strict validation. The listing directory check warns that icons are absent; it explicitly does not change the validation result.

The unit/integration suite covers incremental capture and rollback, harness noise, Codex fork identities, Cursor exports, recency/relevance, actual-data health and exit codes, local no-network operation, media opt-in, subscription-only digest calls, stdio MCP, HTTP errors/read-back/redirects, inventory and installer preservation/backups.

Remote exchange, captions and digest paths use independent fictional doubles. Live member Turso, Supadata, YouTube captions and a subscription digest have not been exercised. All three model evals are authentication-blocked in the isolated HOME; see eval-results_v1.md.

The real sandbox proof covers local marketplace installation, both pack installs, fictional capture/search/read/status, unrelated MCP entries/backups, the installed stdio handshake/search and Codex’s real MCP inventory.

The revised raw tutorial sequence contains 15 ordered landscape clips. ffprobe checks their inventory, 1920 x 1080 dimensions and positive durations. The earlier 40-second cap has been removed. Full command/output views and reading pauses are documented in video/SHOTLIST_v1.md; the full inventory includes a page-by-page hold.

Actual terminal screenshots of Claude Code, Codex and the Cursor sandbox configuration are saved in video/screens. Authenticated chats and the live Cursor profile are not presented as verified UI; the shot list marks the later capture/mock-up boundary.

No push, PR, tag, publication, Skool operation or write to real harness/brain configuration was performed. The pre-existing untracked excalidraw.log is outside this change.
