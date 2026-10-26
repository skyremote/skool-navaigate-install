# aios-brain 2.0.0

Your own session memory. Depends on aios. Requires Python 3.9+ with SQLite FTS5.
Local SQLite by default; no account, API key or network request is needed.

Commands: brain init, capture, search, read, media add, digest, status and sync.
Use brain --help for syntax. Run /brain or /aios-brain:brain for setup guidance.

Read the repository README for optional member-owned Turso, yt-dlp captions,
paid Supadata opt-in, subscription-only digests and health checks. There are no
bundled user records, credentials or personal account paths in this pack.

The three eval cases test setup advice, silent-failure diagnosis and media cost
boundaries. A real subscription login is needed to score them; unit/integration
tests in tests/ exercise capture, ranking, status, MCP and the transport separately.
