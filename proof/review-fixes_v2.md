# Phase 1 audit fixes v2

All 16 findings from the review of ffddffb are fixed on aios-v2. The retained
v1 source and marketplace ID remain installable, with fixes-only support until
26 April 2027. Nothing is pushed, tagged or published.

The final run and counts are in checks_v2.md. Tests in
`tests/test_review_regressions.py` use the audit IDs below; every row has at least
one dedicated regression, and the original reproduction scripts are recorded
in reproductions_v2.md. The new test suite was also run against the unchanged
baseline code in a disposable /tmp checkout and failed there; its trace includes
missing new interfaces as well as behavioural failures.

| ID | Severity | Finding | State | Implementation and proof |
|---|---|---|---|---|
| R01 | Blocker | Broken v1 symlinks and missing catalogue entry | Fixed | Original skills, lessons, references and templates restored; old plugin manifest and marketplace entry retained; no-argument installer still installs v1. Guided migration needs an explicit flag and preserves old links in backups. R01 checks all 28 old skills across four harness directories. |
| R02 | High | Active sessions always unhealthy | Fixed | Captured append-only sessions get a 120-second grace window. A persisted first-pending marker prevents continuous writes from restarting it; uncaptured data fails after the window. |
| R03 | High | Failure rows never clear | Fixed | Invalid refs/URLs are rejected before operational failure recording. Missing-file failures are pruned; old valid media aliases are normalised. `brain failures list` and explicit `clear --scope`/`--all` acknowledge stale rows without deleting captured data or bypassing health. |
| R04 | High | Ignored harness folder overrides and false green on no sessions | Fixed | Capture and start inventory honour CLAUDE_CONFIG_DIR and CODEX_HOME. Installed/configured harnesses with zero session files are unhealthy. R04 covers custom folders and a completely empty installed harness. |
| R05 | High | Remote sync blocks local recall and fetches the entire corpus | Fixed | CLI/MCP search and read do not load remote credentials or call the network. Sync runs only on capture or explicit sync; catalogue pages contain 128 metadata rows, and only changed payloads are read in chunks of 100,000 characters. Offline and bounded-transfer regressions pass. |
| R06 | Medium | Unsafe TOML detection on Python 3.9 and CRLF | Fixed | Existing aios-brain text is refused unless it is the exact managed stanza; dotted keys, array tables, inline forms, BOM and multiline ambiguity cannot create duplicate tables. CRLF is normalised for comparison and retained in output. Tests force the no-tomllib path, then the reproduction output is checked independently with Python 3.14. |
| R07 | Medium | Dotfiles config symlinks replaced | Fixed | Both config paths are checked for symlinks before edits; the installer stops and preserves the link and its target, with a manual-merge instruction. |
| R08 | Medium | Recapture erases saved digest/title | Fixed | Existing digest JSON, digest document and title are carried forward. Changed sessions report that their retained digest predates the latest capture and can be refreshed explicitly. |
| R09 | Medium | A crash-cut final line loses every valid turn | Fixed | A final malformed line idle for at least five minutes is skipped with a stored warning; valid turns are captured atomically. Interior corruption remains an error and never advances the completed hash. |
| R10 | Medium | Cursor times use file mtime and touch breaks health | Fixed | Embedded Cursor timestamps are read before cleaning; assistant turns inherit the preceding clock. Unknown timestamps stay zero rather than becoming file mtime. The fixture now has the real JSONL shape, without artificial top-level timestamps. Touch/copy checks remain healthy. |
| R11 | Medium | Captured credentials kept and synced | Fixed | Generic redaction covers provider keys, JWTs, bearer values, private keys and credential assignments before storage, indexing or sync. Existing local text/index data is scrubbed on upgrade. Incoming unsafe remote bundles are sanitised and written back, including a future-version case. README states the best-effort scope. |
| R12 | Low | Header errors expose tokens; subprocesses inherit unrelated keys | Fixed | Token whitespace/control characters are rejected without echoing input. HTTP transport exceptions use fixed messages. Old unsafe invalid-header failure messages are scrubbed. Child processes get a minimal allowlist; only Claude’s required subscription environment reaches its digest process. |
| R13 | Low | Retention warning arrives after data loss | Fixed | Reads cleanupPeriodDays, defaults to 30, and warns after about two-thirds of the window with days left. Includes a 7-day-policy regression. |
| R14 | Low | Unchanged status loads/parses huge files | Fixed | Files are hashed in streaming chunks. Captured size/mtime/hash and a stored message fingerprint avoid parsing unchanged sessions while still detecting missing or altered DB messages. The regression checks a 16 MB file without whole-file reads or parsing and bounds traced memory below 8 MB; clockless Cursor capture is incremental too. |
| R15 | Low | Cleaner destroys the member’s own prompt markup | Fixed | Removes known leading injected envelopes and harness-specific wrappers only. Inline instructions/timestamps and quoted Thinking/tool headings survive in ordinary messages; Cursor TXT tool scaffolding is stripped only in that export format. |
| R16 | Low | Installer overwrites concurrent config edits | Fixed | Config edits are locked between cooperating installers. Both files are re-read before any edit, and each is checked again before/after backup and just before replacement. A simulated external write aborts without losing the new content. |

## Evidence and limits

- `checks_v2.md`: fresh unit/regression, strict validation, VHS and clip checks.
- `sandbox-run_v2.md`: new-member install/capture/recall/health/MCP proof, with portable paths.
- `reproductions_v2.md`: the reviewer’s scripts, independent TOML check and baseline failures.
- `video/SHOTLIST_v2.md`: exact commands, changed outputs, narration outline and deferred UI shots.
- `video/clips/manifest_v2.json`: measured durations and 1920 x 1080 dimensions.

All 15 tutorial clips were re-recorded from a physical scratch source copy under
/tmp. Their real software output contains no producer-Mac checkout path. Old
unsafe stills and recordings are replaced in the current tree. Textual historical
proof is retained with machine paths normalised to `<worktree>` and `$HOME`.

The current Turso Cloud limitations page does not publish a hosted response-size
contract. The upstream libSQL server exposes configurable defaults of 10 MB per
response and 32 MB total response size. The implementation avoids depending on
those maxima through metadata pagination and bounded payload reads. Sources:
[Turso Cloud limitations](https://docs.turso.tech/cloud/limitations),
[upstream libSQL server configuration](https://github.com/tursodatabase/libsql/blob/main/libsql-server/src/main.rs).
These are protocol/design checks, not a live hosted-account test.

The earlier model-eval attempts remain authentication-blocked in an isolated
member HOME. No real credentials were copied. Live Turso, paid transcription,
subscription digests and authenticated harness chat screens remain separate
acceptance checks; the unit doubles and real local CLI/MCP proof are labelled.
