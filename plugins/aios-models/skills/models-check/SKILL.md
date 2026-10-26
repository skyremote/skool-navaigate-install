---
name: models-check
description: Print my current models, effort level, advisor and logins for Claude Code, Codex, Cursor and the bb account pool, without showing any secret. Use for /models-check, "what model am I on", "which logins do I have", or before changing effort.
---

# /models-check

Run the check and show its output as it is:

- Claude Code: `models-check` (this plugin's `bin/` is on the Bash PATH).
- Codex and Cursor: `~/.local/bin/models-check` after `./install.sh aios-models`.
- Add `--project <folder>` to include that project's `.claude/settings.json` and `settings.local.json`.
- Add `--json` when another tool needs the result.

It reads settings files and asks each CLI for its login state (`claude auth status`, `codex login status`,
`cursor-agent status`, `bb pool account list`). It prints no tokens, keys or email addresses.
Never open or print the settings, credential or auth files yourself.

Then explain the result in plain words, one line per harness:

- **model**: the model and where it was set (user, project, local, env or not set).
- **effort**: if it shows `xhigh` or `max`, suggest `/effort medium` and raising it per task.
- **advisor**: if it is `off`, suggest `/advisor opus` for a Sonnet main model.
- **login**: anything `signed out` needs `claude auth login`, `codex login` or `cursor-agent login`.
- **failover**: if fewer than two Claude logins are ready, offer the `models` skill's two-subscription steps.
- **warnings**: say what each one means. An `ANTHROPIC_API_KEY` warning means metered API billing.

The check reports saved settings. A session can still differ because of `--model`, `--effort` or `/model` in
that session, so `/status` inside the session is the final word.

To record a second Claude Code login: `models-check login add <label>`. It saves the label in
`~/.config/aios-models/logins.json`, creates `~/.claude-<label>`, and prints the sign-in command and alias.

End with the one change you recommend, if any, then `/aios`. British English.
