# Audit reproductions v2

The review scripts run only against synthetic /tmp homes and the review checkout. Their diagnostics are preserved below; the named regression tests provide assertions for each finding.
Machine-specific paths are represented by <worktree> and $HOME.
The supplied cursor_jsonl.py script still labels its stored timestamp as file mtime; that diagnostic label is stale. The observed value now comes from the embedded Cursor timestamp. The final section deliberately shows failures against the unchanged baseline, separately from the passing current build.

```sh
bash /tmp/aios-review-scripts/runtime.sh <worktree>
```
```text
1. after capture: status exit=0
2. active-session append: healthy= True []
   after recapture: status exit=0
3. media add playlist exit=1
   status after capture: healthy= True []
{"error": "Unknown ref. Run brain search first."}

   failures now: []

[exit 0]
```

```sh
bash /tmp/aios-review-scripts/runtime2.sh <worktree>
```
```text
{"captured":1,"unchanged":0,"messages":1,"skipped_subagents":0,"failures":[],"warnings":[],"sync":{"mode":"local","network":"off"}}
4. CLAUDE_CONFIG_DIR member: status exit=0
   healthy= True session_files= 1 problems= []
5. capture with unreachable Turso exit=1
{"jsonrpc": "2.0", "id": 2, "result": {"content": [{"type": "text", "text": "{\"hits\": [{\"ref\": \"claude:65112e8db51c:s2\", \"kind\": \"message\", \"title\": \"\", \"timestamp\": 1793008800.0, \"score\": 2.1241174360238222e-06, \"snippet\": \"[Lighthouse] budget offline\"}]}"}]}}
{  "hits": [    {      "ref": "claude:65112e8db51c:s2",      "kind": "message",      "title": "",      "timestamp": 1793

{"error": "Credential contains whitespace or control characters; paste it again privately"}
0
^ count of token fragments printed by a later brain status

[exit 0]
```

```sh
bash /tmp/aios-review-scripts/stale_failure.sh <worktree>
```
```text
{  "captured": 1,  "unchanged": 0,  "messages": 1,  "skipped_subagents": 0,  "failures": [    "crashed.jsonl: Incomplete final session line; retry after the writer finishes"  ],  "warnings": [],  "sync": {    "mode": "lo
 exit=0
{"hits":[]}
capture after file gone exit=0
status healthy= True failures= [] warnings= 1

[exit 0]
```

```sh
python3 /tmp/aios-review-scripts/cursor_jsonl.py <worktree>
```
```text
stored ts = 1787550300.0 (file mtime; Aug 24 2026 07:45 UTC+2 would be 1787550300)
healthy after capture: True
healthy after mtime-only change + capture: True []

[exit 0]
```

```sh
python3 /tmp/aios-review-scripts/digest_loss.py <worktree>
```
```text
A. after digest: title='Lighthouse budget' has_digest=1 digest_docs=1
   after the session grows and is recaptured: title='Lighthouse budget' has_digest=1 digest_docs=1
B. TXT captured, healthy=True
   after touch only: capture captured=0 unchanged=4 failures=0; status healthy=True problems=[]
   after another capture: healthy=True

[exit 0]
```

```sh
python3 /tmp/aios-review-scripts/toml_cases.py <worktree>
```
```text
{"dotted_in_mcp_servers": {"ok": false, "error": "ValueError: Existing custom aios-brain TOML preserved; merge it manually"}, "root_dotted": {"ok": false, "error": "ValueError: Existing custom aios-brain TOML preserved; merge it manually"}, "root_dotted_other": {"ok": true, "result": "mcp_servers.other.command = \"/x\"\n\n[mcp_servers.aios-brain]\ncommand = \"$HOME/.local/bin/brain\"\nargs = [\"mcp\"]\n"}, "array_tables": {"ok": false, "error": "ValueError: Existing custom aios-brain TOML preserved; merge it manually"}, "crlf_existing": {"ok": true, "result": "[mcp_servers.aios-brain]\r\ncommand = \"$HOME/.local/bin/brain\"\r\nargs = [\"mcp\"]\r\n"}, "bom_first_header": {"ok": false, "error": "ValueError: TOML byte-order mark found; remove it manually before installing"}, "inline_in_parent": {"ok": true, "result": "[mcp_servers]\nother = { command = \"x\" }\n\n[mcp_servers.aios-brain]\ncommand = \"$HOME/.local/bin/brain\"\nargs = [\"mcp\"]\n"}, "multiline_string_header": {"ok": false, "error": "ValueError: aios-brain in a multiline TOML string; merge the MCP entry manually"}, "no_trailing_newline": {"ok": true, "result": "model = \"o3\"\n\n[mcp_servers.aios-brain]\ncommand = \"$HOME/.local/bin/brain\"\nargs = [\"mcp\"]\n"}, "quoted_existing_exact": {"ok": false, "error": "ValueError: Existing custom aios-brain TOML preserved; merge it manually"}}

[exit 0]
```

## Independent TOML validation (Python 3.14)

```sh
/opt/homebrew/bin/python3.14 /tmp/aios-review-scripts/toml_validate.py
```
```text
dotted_in_mcp_servers        REFUSED  ValueError: Existing custom aios-brain TOML preserved; merge it manually
root_dotted                  REFUSED  ValueError: Existing custom aios-brain TOML preserved; merge it manually
root_dotted_other            written, valid TOML
array_tables                 REFUSED  ValueError: Existing custom aios-brain TOML preserved; merge it manually
crlf_existing                written, valid TOML
bom_first_header             REFUSED  ValueError: TOML byte-order mark found; remove it manually before installing
inline_in_parent             written, valid TOML
multiline_string_header      REFUSED  ValueError: aios-brain in a multiline TOML string; merge the MCP entry manually
no_trailing_newline          written, valid TOML
quoted_existing_exact        REFUSED  ValueError: Existing custom aios-brain TOML preserved; merge it manually

[exit 0]
```

## Baseline regression run

The 22 new regression tests were also run against the original ffddffb code in /tmp. Only the new test file and its import-only privacy helper were copied into that snapshot; the implementation stayed unchanged. The failures below demonstrate missing behaviour or missing new interfaces.

```text
test_R01_v1_symlinks_catalogue_and_explicit_preserved_migration (test_review_regressions.ReviewRegressions) ... ERROR
test_R02_active_append_gets_bounded_grace_not_permanent_green (test_review_regressions.ReviewRegressions) ... FAIL
test_R03_invalid_inputs_are_not_failures_and_acknowledge_exists (test_review_regressions.ReviewRegressions) ... FAIL
test_R03_moved_crashed_file_failure_clears (test_review_regressions.ReviewRegressions) ... FAIL
test_R04_harness_overrides_and_empty_installed_harness (test_review_regressions.ReviewRegressions) ... FAIL
test_R05_local_mcp_recall_survives_unreachable_and_invalid_remote (test_review_regressions.ReviewRegressions) ... FAIL
test_R05_sync_fetches_metadata_then_only_changed_payloads_in_chunks (test_review_regressions.ReviewRegressions) ... FAIL
test_R06_python39_toml_conflicts_and_crlf (test_review_regressions.ReviewRegressions) ... FAIL
test_R07_symlinked_config_sources_are_preserved (test_review_regressions.ReviewRegressions) ... test_R08_recapture_preserves_paid_digest_and_title (test_review_regressions.ReviewRegressions) ... FAIL
test_R09_idle_truncated_tail_recovers_valid_turns_only (test_review_regressions.ReviewRegressions) ... ERROR
test_R10_cursor_embedded_time_and_touch_do_not_change_messages (test_review_regressions.ReviewRegressions) ... FAIL
test_R11_credentials_redacted_before_store_search_read_and_sync (test_review_regressions.ReviewRegressions) ... FAIL
test_R11_unsafe_remote_bundle_is_redacted_even_with_future_version (test_review_regressions.ReviewRegressions) ... FAIL
test_R11_upgrade_scrubs_prior_local_rows_and_fts (test_review_regressions.ReviewRegressions) ... FAIL
test_R12_malformed_token_and_header_exception_never_leak (test_review_regressions.ReviewRegressions) ... FAIL
test_R12_subprocesses_get_only_needed_credentials (test_review_regressions.ReviewRegressions) ... FAIL
test_R13_retention_warning_arrives_before_custom_cleanup (test_review_regressions.ReviewRegressions) ... ERROR
test_R14_unchanged_large_file_is_hashed_streaming_without_parsing (test_review_regressions.ReviewRegressions) ... ERROR
test_R14_unknown_timestamps_still_skip_unchanged_cursor_json (test_review_regressions.ReviewRegressions) ... ERROR
test_R15_user_prompt_examples_survive_harness_scoped_cleaning (test_review_regressions.ReviewRegressions) ... ERROR
test_R16_concurrent_config_edit_aborts_without_losing_it (test_review_regressions.ReviewRegressions) ... ERROR

======================================================================
ERROR: test_R01_v1_symlinks_catalogue_and_explicit_preserved_migration (test_review_regressions.ReviewRegressions)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/aios-review-baseline-v2/tests/test_review_regressions.py", line 36, in test_R01_v1_symlinks_catalogue_and_explicit_preserved_migration
    skills=sorted((ROOT/'skills').iterdir())
  File "/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/pathlib.py", line 1150, in iterdir
    for name in self._accessor.listdir(self):
FileNotFoundError: [Errno 2] No such file or directory: '/private/tmp/aios-review-baseline-v2/skills'

======================================================================
ERROR: test_R07_symlinked_config_sources_are_preserved (test_review_regressions.ReviewRegressions) (relative='.cursor/mcp.json')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/aios-review-baseline-v2/tests/test_review_regressions.py", line 168, in test_R07_symlinked_config_sources_are_preserved
    dest.symlink_to(source)
  File "/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/pathlib.py", line 1393, in symlink_to
    self._accessor.symlink(target, self, target_is_directory)
  File "/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/pathlib.py", line 446, in symlink
    return os.symlink(a, b)
FileExistsError: [Errno 17] File exists: '/tmp/aios-test-oy9tnmrb/source-mcp.json' -> '/tmp/aios-test-oy9tnmrb/.cursor/mcp.json'

======================================================================
ERROR: test_R09_idle_truncated_tail_recovers_valid_turns_only (test_review_regressions.ReviewRegressions)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/aios-review-baseline-v2/tests/test_review_regressions.py", line 193, in test_R09_idle_truncated_tail_recovers_valid_turns_only
    old=time.time()-capture.CRASH_TAIL_SECONDS-10
AttributeError: module 'aios_brain.capture' has no attribute 'CRASH_TAIL_SECONDS'

======================================================================
ERROR: test_R13_retention_warning_arrives_before_custom_cleanup (test_review_regressions.ReviewRegressions)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/aios-review-baseline-v2/tests/test_review_regressions.py", line 301, in test_R13_retention_warning_arrives_before_custom_cleanup
    folder=capture.config_dirs()['claude'];(folder/'settings.json').write_text('{"cleanupPeriodDays":7}')
AttributeError: module 'aios_brain.capture' has no attribute 'config_dirs'

======================================================================
ERROR: test_R14_unchanged_large_file_is_hashed_streaming_without_parsing (test_review_regressions.ReviewRegressions)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/aios-review-baseline-v2/tests/test_review_regressions.py", line 318, in test_R14_unchanged_large_file_is_hashed_streaming_without_parsing
    with patch.object(capture.Session,'turns',side_effect=AssertionError('Unchanged file must not be parsed')),patch.object(Path,'read_bytes',side_effect=AssertionError('No whole-file read')):
AttributeError: module 'aios_brain.capture' has no attribute 'Session'

======================================================================
ERROR: test_R14_unknown_timestamps_still_skip_unchanged_cursor_json (test_review_regressions.ReviewRegressions)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/aios-review-baseline-v2/tests/test_review_regressions.py", line 330, in test_R14_unknown_timestamps_still_skip_unchanged_cursor_json
    with patch.object(capture.Session,'turns',side_effect=AssertionError('Unchanged clockless file must not be parsed')):
AttributeError: module 'aios_brain.capture' has no attribute 'Session'

======================================================================
ERROR: test_R15_user_prompt_examples_survive_harness_scoped_cleaning (test_review_regressions.ReviewRegressions)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/aios-review-baseline-v2/tests/test_review_regressions.py", line 337, in test_R15_user_prompt_examples_survive_harness_scoped_cleaning
    self.assertEqual(capture.clean(text,source),text)
TypeError: clean() takes 1 positional argument but 2 were given

======================================================================
ERROR: test_R16_concurrent_config_edit_aborts_without_losing_it (test_review_regressions.ReviewRegressions)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/aios-review-baseline-v2/tests/test_review_regressions.py", line 346, in test_R16_concurrent_config_edit_aborts_without_losing_it
    snapshot=installer.snapshot
AttributeError: module 'install_pack' has no attribute 'snapshot'

======================================================================
FAIL: test_R02_active_append_gets_bounded_grace_not_permanent_green (test_review_regressions.ReviewRegressions)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/aios-review-baseline-v2/tests/test_review_regressions.py", line 67, in test_R02_active_append_gets_bounded_grace_not_permanent_green
    self.assertTrue(report['healthy'],report)
AssertionError: False is not true : {'healthy': False, 'session_files': 3, 'newest_session_file': {'name': 'fictional-claude.jsonl', 'modified': 1793006194.0358336}, 'newest_session_message': 1793009100.0, 'newest_stored_message': 1793008800.0, 'newest_message_all_machines': 1793008800.0, 'pending_files': ['fictional-claude.jsonl'], 'problems': ['1 session file(s) not captured; run brain capture', 'Newest stored message is behind the newest session message'], 'failures': [], 'warnings': ['Claude Code deletes session files after 30 days. Capture regularly; keep your database off cloud-sync folders.', 'No verified capture in the last 30 days. Session history may already be missing.']}

======================================================================
FAIL: test_R03_invalid_inputs_are_not_failures_and_acknowledge_exists (test_review_regressions.ReviewRegressions)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/aios-review-baseline-v2/tests/test_review_regressions.py", line 84, in test_R03_invalid_inputs_are_not_failures_and_acknowledge_exists
    self.assertEqual(self.conn.execute('SELECT count(*) FROM failures').fetchone()[0],0)
AssertionError: 2 != 0

======================================================================
FAIL: test_R03_moved_crashed_file_failure_clears (test_review_regressions.ReviewRegressions)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/aios-review-baseline-v2/tests/test_review_regressions.py", line 95, in test_R03_moved_crashed_file_failure_clears
    self.assertTrue(status.status(self.conn)['healthy'])
AssertionError: False is not true

======================================================================
FAIL: test_R04_harness_overrides_and_empty_installed_harness (test_review_regressions.ReviewRegressions)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/aios-review-baseline-v2/tests/test_review_regressions.py", line 105, in test_R04_harness_overrides_and_empty_installed_harness
    self.assertEqual(capture.capture(self.conn)['captured'],3)
AssertionError: 1 != 3

======================================================================
FAIL: test_R05_local_mcp_recall_survives_unreachable_and_invalid_remote (test_review_regressions.ReviewRegressions)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/aios-review-baseline-v2/tests/test_review_regressions.py", line 119, in test_R05_local_mcp_recall_survives_unreachable_and_invalid_remote
    self.assertTrue(call('brain_search',{'query':'Lighthouse'})['hits'])
  File "/private/tmp/aios-review-baseline-v2/plugins/aios-brain/aios_brain/mcp_server.py", line 34, in call
    sync_if_configured(conn,values)
  File "/private/tmp/aios-review-baseline-v2/plugins/aios-brain/aios_brain/cli.py", line 14, in sync_if_configured
    result = sync.synchronise(conn,sync.HTTP(values['AIOS_BRAIN_TURSO_URL'],values['AIOS_BRAIN_TURSO_TOKEN']))
  File "/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/unittest/mock.py", line 1093, in __call__
    return self._mock_call(*args, **kwargs)
  File "/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/unittest/mock.py", line 1097, in _mock_call
    return self._execute_mock_call(*args, **kwargs)
  File "/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/unittest/mock.py", line 1152, in _execute_mock_call
    raise effect
AssertionError: Recall must not connect

======================================================================
FAIL: test_R05_sync_fetches_metadata_then_only_changed_payloads_in_chunks (test_review_regressions.ReviewRegressions)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/aios-review-baseline-v2/tests/test_review_regressions.py", line 136, in test_R05_sync_fetches_metadata_then_only_changed_payloads_in_chunks
    self.assertFalse(any('SELECT *' in sql for sql in calls))
AssertionError: True is not false

======================================================================
FAIL: test_R06_python39_toml_conflicts_and_crlf (test_review_regressions.ReviewRegressions) (text='[mcp_servers]\naios-brain.command="custom"\n')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/aios-review-baseline-v2/tests/test_review_regressions.py", line 156, in test_R06_python39_toml_conflicts_and_crlf
    installer.codex_config(text,exe)
AssertionError: ValueError not raised

======================================================================
FAIL: test_R06_python39_toml_conflicts_and_crlf (test_review_regressions.ReviewRegressions) (text='mcp_servers.aios-brain.command="custom"\n')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/aios-review-baseline-v2/tests/test_review_regressions.py", line 156, in test_R06_python39_toml_conflicts_and_crlf
    installer.codex_config(text,exe)
AssertionError: ValueError not raised

======================================================================
FAIL: test_R06_python39_toml_conflicts_and_crlf (test_review_regressions.ReviewRegressions) (text='[[mcp_servers.aios-brain]]\ncommand="custom"\n')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/aios-review-baseline-v2/tests/test_review_regressions.py", line 156, in test_R06_python39_toml_conflicts_and_crlf
    installer.codex_config(text,exe)
AssertionError: ValueError not raised

======================================================================
FAIL: test_R06_python39_toml_conflicts_and_crlf (test_review_regressions.ReviewRegressions)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/aios-review-baseline-v2/tests/test_review_regressions.py", line 158, in test_R06_python39_toml_conflicts_and_crlf
    self.assertEqual(installer.codex_config(block,exe),block)
AssertionError: '[mcp[67 chars]cp"]\n\n[mcp_servers.aios-brain]\ncommand = "/[31 chars]"]\n' != '[mcp[67 chars]cp"]\r\n'
  [mcp_servers.aios-brain]
  command = "/tmp/member/brain"
- args = ["mcp"]
+ args = ["mcp"]
?               +
-
- [mcp_servers.aios-brain]
- command = "/tmp/member/brain"
- args = ["mcp"]


======================================================================
FAIL: test_R07_symlinked_config_sources_are_preserved (test_review_regressions.ReviewRegressions) (relative='.codex/config.toml')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/aios-review-baseline-v2/tests/test_review_regressions.py", line 170, in test_R07_symlinked_config_sources_are_preserved
    installer.install('aios-brain')
AssertionError: ValueError not raised

======================================================================
FAIL: test_R08_recapture_preserves_paid_digest_and_title (test_review_regressions.ReviewRegressions)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/aios-review-baseline-v2/tests/test_review_regressions.py", line 185, in test_R08_recapture_preserves_paid_digest_and_title
    self.assertEqual(value['item']['title'],'Saved subscription digest')
AssertionError: '' != 'Saved subscription digest'
+ Saved subscription digest

======================================================================
FAIL: test_R10_cursor_embedded_time_and_touch_do_not_change_messages (test_review_regressions.ReviewRegressions)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/aios-review-baseline-v2/tests/test_review_regressions.py", line 212, in test_R10_cursor_embedded_time_and_touch_do_not_change_messages
    self.assertEqual(search.search(self.conn,'Buzz')[0]['timestamp'],1787550300)
AssertionError: 1793006194.1137586 != 1787550300

======================================================================
FAIL: test_R11_credentials_redacted_before_store_search_read_and_sync (test_review_regressions.ReviewRegressions)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/aios-review-baseline-v2/tests/test_review_regressions.py", line 229, in test_R11_credentials_redacted_before_store_search_read_and_sync
    self.assertNotIn(secret,text)
AssertionError: 'sk-proj-A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1' unexpectedly found in 'user: Plan the Lighthouse launch.\n\nassistant: The fictional Lighthouse launch budget is 2400 pounds. Use the blue invitation.\n\nuser: Use navy paint. sk-proj-A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1A1 ghp_B2B2B2B2B2B2B2B2B2B2B2B2B2B2B2B2 eyJabcdefghi.abcdefghijkl.abcdefghijklm\nTURSO_TOKEN=fictional-private-value\npassword: "fictional-password"\nWe should discuss password rotation.'

======================================================================
FAIL: test_R11_unsafe_remote_bundle_is_redacted_even_with_future_version (test_review_regressions.ReviewRegressions)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/aios-review-baseline-v2/tests/test_review_regressions.py", line 267, in test_R11_unsafe_remote_bundle_is_redacted_even_with_future_version
    self.assertNotIn(secret,db.serialise(db.bundle(self.conn,ref)))
AssertionError: 'ghp_D4D4D4D4D4D4D4D4D4D4D4D4D4D4D4D4D4D4D4D4' unexpectedly found in '{"documents":[{"body":"A captured key: ghp_D4D4D4D4D4D4D4D4D4D4D4D4D4D4D4D4D4D4D4D4","id":"claude:aaeed4eddad8:fictional-claude:00000000","kind":"message","ref":"claude:aaeed4eddad8:fictional-claude","role":"user","ts":1793008800.0},{"body":"The fictional Lighthouse launch budget is 2400 pounds. Use the blue invitation.","id":"claude:aaeed4eddad8:fictional-claude:00000001","kind":"message","ref":"claude:aaeed4eddad8:fictional-claude","role":"assistant","ts":1793008800.0}],"item":{"device":"aaeed4eddad8","digest":null,"file_hash":"5e34dc47a3a3e6a929d33dcbcf040bd7f27ad0700b336f759a30fbb2c574397d","latest":1793008800.0,"modified":1793006194.1291645,"path":"/tmp/aios-test-4kts3b4d/.claude/projects/fictional/fictional-claude.jsonl","ref":"claude:aaeed4eddad8:fictional-claude","source":"claude","title":"","updated":1793009794.1300778,"url":null}}'

======================================================================
FAIL: test_R11_upgrade_scrubs_prior_local_rows_and_fts (test_review_regressions.ReviewRegressions)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/aios-review-baseline-v2/tests/test_review_regressions.py", line 251, in test_R11_upgrade_scrubs_prior_local_rows_and_fts
    self.assertNotIn(secret,db.serialise(value))
AssertionError: 'sk-proj-C3C3C3C3C3C3C3C3C3C3C3C3C3C3C3C3C3C3C3C3' unexpectedly found in '{"documents":[{"body":"sk-proj-C3C3C3C3C3C3C3C3C3C3C3C3C3C3C3C3C3C3C3C3","id":"claude:22b48f6f8671:fictional-claude:00000000","kind":"message","ref":"claude:22b48f6f8671:fictional-claude","role":"user","ts":1793008800.0},{"body":"sk-proj-C3C3C3C3C3C3C3C3C3C3C3C3C3C3C3C3C3C3C3C3","id":"claude:22b48f6f8671:fictional-claude:00000001","kind":"message","ref":"claude:22b48f6f8671:fictional-claude","role":"assistant","ts":1793008800.0}],"item":{"device":"22b48f6f8671","digest":"{\\"token\\": \\"sk-proj-C3C3C3C3C3C3C3C3C3C3C3C3C3C3C3C3C3C3C3C3\\"}","file_hash":"5e34dc47a3a3e6a929d33dcbcf040bd7f27ad0700b336f759a30fbb2c574397d","latest":1793008800.0,"modified":1793006194.1370466,"path":"/tmp/aios-test-gyv325cl/.claude/projects/fictional/fictional-claude.jsonl","ref":"claude:22b48f6f8671:fictional-claude","source":"claude","title":"sk-proj-C3C3C3C3C3C3C3C3C3C3C3C3C3C3C3C3C3C3C3C3","updated":1793006194.1379461,"url":null}}'

======================================================================
FAIL: test_R12_malformed_token_and_header_exception_never_leak (test_review_regressions.ReviewRegressions)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/aios-review-baseline-v2/tests/test_review_regressions.py", line 276, in test_R12_malformed_token_and_header_exception_never_leak
    self.assertNotIn('SECRETPART',out+err)
AssertionError: 'SECRETPART' unexpectedly found in '{"error": "Invalid header value b\'Bearer SECRETPART1\\\\nSECRETPART2\'"}\n'

======================================================================
FAIL: test_R12_subprocesses_get_only_needed_credentials (test_review_regressions.ReviewRegressions)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/aios-review-baseline-v2/tests/test_review_regressions.py", line 293, in test_R12_subprocesses_get_only_needed_credentials
    self.assertTrue(set(env).isdisjoint(item.kwargs['env']))
AssertionError: False is not true

----------------------------------------------------------------------
Ran 22 tests in 0.224s

FAILED (failures=18, errors=8)
Backed up .codex/config.toml -> config.toml.backup-1793006194089243000
Configured .codex/config.toml
Configured .cursor/mcp.json
Linked .codex/skills/brain
Linked .cursor/skills/brain
Linked .agents/skills/brain
Linked .local/bin/brain
Installed aios-brain 2.0.0. Restart Codex and Cursor. Add ~/.local/bin to PATH for brain.
```
