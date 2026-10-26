# Checks v2

All harness CLI checks use the isolated member HOME.

```sh
python3 --version
```
```text
Python 3.9.6
[exit 0]
```

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
test_proof_output_uses_placeholders_for_checkout_and_member_home (test_proof_paths.PortableProofTests) ... ok
test_R01_v1_symlinks_catalogue_and_explicit_preserved_migration (test_review_regressions.ReviewRegressions) ... ok
test_R02_active_append_gets_bounded_grace_not_permanent_green (test_review_regressions.ReviewRegressions) ... ok
test_R03_invalid_inputs_are_not_failures_and_acknowledge_exists (test_review_regressions.ReviewRegressions) ... ok
test_R03_moved_crashed_file_failure_clears (test_review_regressions.ReviewRegressions) ... ok
test_R04_harness_overrides_and_empty_installed_harness (test_review_regressions.ReviewRegressions) ... ok
test_R05_local_mcp_recall_survives_unreachable_and_invalid_remote (test_review_regressions.ReviewRegressions) ... ok
test_R05_sync_fetches_metadata_then_only_changed_payloads_in_chunks (test_review_regressions.ReviewRegressions) ... ok
test_R06_python39_toml_conflicts_and_crlf (test_review_regressions.ReviewRegressions) ... ok
test_R07_symlinked_config_sources_are_preserved (test_review_regressions.ReviewRegressions) ... ok
test_R08_recapture_preserves_paid_digest_and_title (test_review_regressions.ReviewRegressions) ... ok
test_R09_idle_truncated_tail_recovers_valid_turns_only (test_review_regressions.ReviewRegressions) ... ok
test_R10_cursor_embedded_time_and_touch_do_not_change_messages (test_review_regressions.ReviewRegressions) ... ok
test_R11_credentials_redacted_before_store_search_read_and_sync (test_review_regressions.ReviewRegressions) ... ok
test_R11_unsafe_remote_bundle_is_redacted_even_with_future_version (test_review_regressions.ReviewRegressions) ... ok
test_R11_upgrade_scrubs_prior_local_rows_and_fts (test_review_regressions.ReviewRegressions) ... ok
test_R12_malformed_token_and_header_exception_never_leak (test_review_regressions.ReviewRegressions) ... ok
test_R12_subprocesses_get_only_needed_credentials (test_review_regressions.ReviewRegressions) ... ok
test_R13_retention_warning_arrives_before_custom_cleanup (test_review_regressions.ReviewRegressions) ... ok
test_R14_unchanged_large_file_is_hashed_streaming_without_parsing (test_review_regressions.ReviewRegressions) ... ok
test_R14_unknown_timestamps_still_skip_unchanged_cursor_json (test_review_regressions.ReviewRegressions) ... ok
test_R15_user_prompt_examples_survive_harness_scoped_cleaning (test_review_regressions.ReviewRegressions) ... ok
test_R16_concurrent_config_edit_aborts_without_losing_it (test_review_regressions.ReviewRegressions) ... ok

----------------------------------------------------------------------
Ran 60 tests in 5.365s

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
vhs validate 'video/tapes/*_v2.tape'
```
```text

[exit 0]
```

```sh
python3 video/check_clips_v2.py
```
```text
[
  {
    "file": "video/clips/01_install-aios_v2.mp4",
    "seconds": 27.8,
    "width": 1920,
    "height": 1080
  },
  {
    "file": "video/clips/02_install-brain_v2.mp4",
    "seconds": 23.52,
    "width": 1920,
    "height": 1080
  },
  {
    "file": "video/clips/03_install-aios-codex-cursor_v2.mp4",
    "seconds": 15.12,
    "width": 1920,
    "height": 1080
  },
  {
    "file": "video/clips/04_install-brain-codex-cursor_v2.mp4",
    "seconds": 28.52,
    "width": 1920,
    "height": 1080
  },
  {
    "file": "video/clips/05_init-brain_v2.mp4",
    "seconds": 16.48,
    "width": 1920,
    "height": 1080
  },
  {
    "file": "video/clips/06_prepare-demo-sessions_v2.mp4",
    "seconds": 17.68,
    "width": 1920,
    "height": 1080
  },
  {
    "file": "video/clips/07_capture-sessions_v2.mp4",
    "seconds": 20.64,
    "width": 1920,
    "height": 1080
  },
  {
    "file": "video/clips/08_repeat-capture_v2.mp4",
    "seconds": 16.72,
    "width": 1920,
    "height": 1080
  },
  {
    "file": "video/clips/09_search-memory_v2.mp4",
    "seconds": 22.24,
    "width": 1920,
    "height": 1080
  },
  {
    "file": "video/clips/10_read-memory_v2.mp4",
    "seconds": 25.48,
    "width": 1920,
    "height": 1080
  },
  {
    "file": "video/clips/11_check-health_v2.mp4",
    "seconds": 45.64,
    "width": 1920,
    "height": 1080
  },
  {
    "file": "video/clips/12_verify-claude-code_v2.mp4",
    "seconds": 23.0,
    "width": 1920,
    "height": 1080
  },
  {
    "file": "video/clips/13_verify-codex_v2.mp4",
    "seconds": 22.64,
    "width": 1920,
    "height": 1080
  },
  {
    "file": "video/clips/14_verify-cursor-config_v2.mp4",
    "seconds": 21.88,
    "width": 1920,
    "height": 1080
  },
  {
    "file": "video/clips/15_check-all-harnesses_v2.mp4",
    "seconds": 81.04,
    "width": 1920,
    "height": 1080
  }
]
[exit 0]
```

## Scope checks

All 28 old skill directories have a row in ROADMAP.md. The original v1 source is preserved, retained at its old paths and installable for six months, with fixes only.

Both plugins and the marketplace pass strict validation. The listing directory check warns that icons are absent; it explicitly does not change the validation result.

The unit/integration suite covers incremental capture and rollback, harness noise, Codex fork identities, Cursor exports, recency/relevance, actual-data health and exit codes, local no-network operation, media opt-in, subscription-only digest calls, stdio MCP, HTTP errors/read-back/redirects, inventory and installer preservation/backups.

Remote exchange, captions and digest paths use independent fictional doubles. Live member Turso, Supadata, YouTube captions and a subscription digest have not been exercised. All three model evals are authentication-blocked in the isolated HOME; see eval-results_v1.md.

The real sandbox proof covers local marketplace installation, both pack installs, fictional capture/search/read/status, unrelated MCP entries/backups, the installed stdio handshake/search and Codex’s real MCP inventory. Findings R01–R16 have dedicated regression tests; see review-fixes_v2.md.

The revised raw tutorial sequence contains 15 ordered landscape clips. ffprobe checks their inventory, 1920 x 1080 dimensions and positive durations. The earlier 40-second cap has been removed. Full command/output views and reading pauses are documented in video/SHOTLIST_v2.md; the full inventory includes a page-by-page hold.

Actual terminal screenshots of Claude Code, Codex and the Cursor sandbox configuration are saved in video/screens. Authenticated chats and the live Cursor profile are not presented as verified UI; the shot list marks the later capture/mock-up boundary.

No push, PR, tag, publication, Skool operation or write to real harness/brain configuration was performed. The pre-existing untracked excalidraw.log is outside this change.

## Additional Python 3.14 check

```sh
TMPDIR=/tmp /opt/homebrew/bin/python3.14 -m unittest discover -s tests -v
```

```text
test_all_harnesses_capture_and_unchanged (test_brain.BrainCase.test_all_harnesses_capture_and_unchanged) ... ok
test_bm25_strong_old_match_survives_recency (test_brain.BrainCase.test_bm25_strong_old_match_survives_recency) ... ok
test_change_replaces_removed_messages_and_fts (test_brain.BrainCase.test_change_replaces_removed_messages_and_fts) ... ok
test_cli_status_exits_one_when_unhealthy (test_brain.BrainCase.test_cli_status_exits_one_when_unhealthy) ... ok
test_codex_first_meta_and_subagents (test_brain.BrainCase.test_codex_first_meta_and_subagents) ... ok
test_config_half_pair_and_private_permissions (test_brain.BrainCase.test_config_half_pair_and_private_permissions) ... ok
test_cursor_text_export (test_brain.BrainCase.test_cursor_text_export) ... ok
test_digest_subscription_only_and_no_automatic_digest (test_brain.BrainCase.test_digest_subscription_only_and_no_automatic_digest) ... ok
test_digest_validates_output_and_removes_api_credentials (test_brain.BrainCase.test_digest_validates_output_and_removes_api_credentials) ... ok
test_failure_recovers_only_after_success (test_brain.BrainCase.test_failure_recovers_only_after_success) ... ok
test_harness_noise_and_tools_absent (test_brain.BrainCase.test_harness_noise_and_tools_absent) ... ok
test_invalid_json_does_not_advance_hash (test_brain.BrainCase.test_invalid_json_does_not_advance_hash) ... ok
test_local_mode_does_not_use_network (test_brain.BrainCase.test_local_mode_does_not_use_network) ... ok
test_mcp_exact_schema_and_round_trip (test_brain.BrainCase.test_mcp_exact_schema_and_round_trip) ... ok
test_media_capture_and_idempotency (test_brain.BrainCase.test_media_capture_and_idempotency) ... ok
test_media_fallback_requires_own_key (test_brain.BrainCase.test_media_fallback_requires_own_key) ... ok
test_media_rejects_non_video_and_insecure_urls (test_brain.BrainCase.test_media_rejects_non_video_and_insecure_urls) ... ok
test_query_is_literal_and_limits_bounded (test_brain.BrainCase.test_query_is_literal_and_limits_bounded) ... ok
test_read_pagination_has_no_lost_text (test_brain.BrainCase.test_read_pagination_has_no_lost_text) ... ok
test_recency_breaks_equal_relevance_tie (test_brain.BrainCase.test_recency_breaks_equal_relevance_tie) ... ok
test_status_30_day_warning (test_brain.BrainCase.test_status_30_day_warning) ... ok
test_status_detects_missing_message_even_with_real_hash (test_brain.BrainCase.test_status_detects_missing_message_even_with_real_hash) ... ok
test_status_does_not_treat_recent_heartbeat_as_health (test_brain.BrainCase.test_status_does_not_treat_recent_heartbeat_as_health) ... ok
test_status_pending_new_file_and_newest_message (test_brain.BrainCase.test_status_pending_new_file_and_newest_message) ... ok
test_status_same_mtime_changed_file (test_brain.BrainCase.test_status_same_mtime_changed_file) ... ok
test_strong_old_bm25_match_beats_weak_recent_match (test_brain.BrainCase.test_strong_old_bm25_match_beats_weak_recent_match) ... ok
test_transaction_rolls_back_messages_and_hash (test_brain.BrainCase.test_transaction_rolls_back_messages_and_hash) ... ok
test_existing_arrays_after_our_table_are_preserved (test_brain.InstallerTests.test_existing_arrays_after_our_table_are_preserved) ... ok
test_foreign_skill_is_preserved_and_brain_needs_real_start_pack (test_brain.InstallerTests.test_foreign_skill_is_preserved_and_brain_needs_real_start_pack) ... ok
test_sandbox_install_backup_and_no_other_skill_links (test_brain.InstallerTests.test_sandbox_install_backup_and_no_other_skill_links) ... ok
test_toml_unrelated_entries_preserved (test_brain.InstallerTests.test_toml_unrelated_entries_preserved) ... ok
test_inventory_reports_each_harness_without_completing_lessons (test_brain.StartStatusTests.test_inventory_reports_each_harness_without_completing_lessons) ... ok
test_http_200_error_is_not_success_and_token_not_printed (test_brain.SyncTests.test_http_200_error_is_not_success_and_token_not_printed) ... ok
test_readback_failure_surfaces_despite_successful_write (test_brain.SyncTests.test_readback_failure_surfaces_despite_successful_write) ... ok
test_transaction_missing_commit_rejected (test_brain.SyncTests.test_transaction_missing_commit_rejected) ... ok
test_transport_never_forwards_a_token_on_redirect (test_brain.SyncTests.test_transport_never_forwards_a_token_on_redirect) ... ok
test_two_machines_exchange_and_verify_actual_contents (test_brain.SyncTests.test_two_machines_exchange_and_verify_actual_contents) ... ok
test_proof_output_uses_placeholders_for_checkout_and_member_home (test_proof_paths.PortableProofTests.test_proof_output_uses_placeholders_for_checkout_and_member_home) ... ok
test_R01_v1_symlinks_catalogue_and_explicit_preserved_migration (test_review_regressions.ReviewRegressions.test_R01_v1_symlinks_catalogue_and_explicit_preserved_migration) ... ok
test_R02_active_append_gets_bounded_grace_not_permanent_green (test_review_regressions.ReviewRegressions.test_R02_active_append_gets_bounded_grace_not_permanent_green) ... ok
test_R03_invalid_inputs_are_not_failures_and_acknowledge_exists (test_review_regressions.ReviewRegressions.test_R03_invalid_inputs_are_not_failures_and_acknowledge_exists) ... ok
test_R03_moved_crashed_file_failure_clears (test_review_regressions.ReviewRegressions.test_R03_moved_crashed_file_failure_clears) ... ok
test_R04_harness_overrides_and_empty_installed_harness (test_review_regressions.ReviewRegressions.test_R04_harness_overrides_and_empty_installed_harness) ... ok
test_R05_local_mcp_recall_survives_unreachable_and_invalid_remote (test_review_regressions.ReviewRegressions.test_R05_local_mcp_recall_survives_unreachable_and_invalid_remote) ... ok
test_R05_sync_fetches_metadata_then_only_changed_payloads_in_chunks (test_review_regressions.ReviewRegressions.test_R05_sync_fetches_metadata_then_only_changed_payloads_in_chunks) ... ok
test_R06_python39_toml_conflicts_and_crlf (test_review_regressions.ReviewRegressions.test_R06_python39_toml_conflicts_and_crlf) ... ok
test_R07_symlinked_config_sources_are_preserved (test_review_regressions.ReviewRegressions.test_R07_symlinked_config_sources_are_preserved) ... ok
test_R08_recapture_preserves_paid_digest_and_title (test_review_regressions.ReviewRegressions.test_R08_recapture_preserves_paid_digest_and_title) ... ok
test_R09_idle_truncated_tail_recovers_valid_turns_only (test_review_regressions.ReviewRegressions.test_R09_idle_truncated_tail_recovers_valid_turns_only) ... ok
test_R10_cursor_embedded_time_and_touch_do_not_change_messages (test_review_regressions.ReviewRegressions.test_R10_cursor_embedded_time_and_touch_do_not_change_messages) ... ok
test_R11_credentials_redacted_before_store_search_read_and_sync (test_review_regressions.ReviewRegressions.test_R11_credentials_redacted_before_store_search_read_and_sync) ... ok
test_R11_unsafe_remote_bundle_is_redacted_even_with_future_version (test_review_regressions.ReviewRegressions.test_R11_unsafe_remote_bundle_is_redacted_even_with_future_version) ... ok
test_R11_upgrade_scrubs_prior_local_rows_and_fts (test_review_regressions.ReviewRegressions.test_R11_upgrade_scrubs_prior_local_rows_and_fts) ... ok
test_R12_malformed_token_and_header_exception_never_leak (test_review_regressions.ReviewRegressions.test_R12_malformed_token_and_header_exception_never_leak) ... ok
test_R12_subprocesses_get_only_needed_credentials (test_review_regressions.ReviewRegressions.test_R12_subprocesses_get_only_needed_credentials) ... ok
test_R13_retention_warning_arrives_before_custom_cleanup (test_review_regressions.ReviewRegressions.test_R13_retention_warning_arrives_before_custom_cleanup) ... ok
test_R14_unchanged_large_file_is_hashed_streaming_without_parsing (test_review_regressions.ReviewRegressions.test_R14_unchanged_large_file_is_hashed_streaming_without_parsing) ... ok
test_R14_unknown_timestamps_still_skip_unchanged_cursor_json (test_review_regressions.ReviewRegressions.test_R14_unknown_timestamps_still_skip_unchanged_cursor_json) ... ok
test_R15_user_prompt_examples_survive_harness_scoped_cleaning (test_review_regressions.ReviewRegressions.test_R15_user_prompt_examples_survive_harness_scoped_cleaning) ... ok
test_R16_concurrent_config_edit_aborts_without_losing_it (test_review_regressions.ReviewRegressions.test_R16_concurrent_config_edit_aborts_without_losing_it) ... ok

----------------------------------------------------------------------
Ran 60 tests in 4.355s

OK
```
