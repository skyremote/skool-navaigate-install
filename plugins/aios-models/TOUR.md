# Tour: module 10, models, effort and cost

Followed by `/aios learn 10` on the member's own machine. Set the defaults, use the advisor once, add a second login.
Do one step at a time. Show the real output, then ask the member to confirm before the next step.
Never print, open or ask for a token, key or password.

## Before you start

- Check: `models-check` prints one block per harness. In Codex and Cursor it is `~/.local/bin/models-check`.
  If it is missing, install the pack first (see README.md).

## Step 1: see what you are on

- Do: `models-check`
- Expect: for each harness, `login`, `model` and `effort` lines, each with where it was set (`<- user`, `<- project`,
  `<- env ...` or `not set`).
- Check: the member can say which model and effort they are on, and where it came from.
- If a warning says `ANTHROPIC_API_KEY is set`, the terminal bills the metered API. Ask whether they meant that.

## Step 2: pick the model for the job

- Do (in Claude Code): `/model sonnet`, then Enter to save it as the default.
- Explain the split: Sonnet for daily building, Opus for planning, hard bugs and reviews, Haiku for summaries and
  volume work, Codex for GPT models, Cursor or Grok Bot for Grok.
- Check: `/status` names the model.

## Step 3: set effort to medium

- Do: `/effort medium`, then Enter.
- Expect: the session header says the effort level.
- Check: `models-check` shows `effort   medium   <- modelSettings`.
- For one hard task only: `/effort high`, then `s` (this session only). For one message: put `ultrathink` in the prompt.
- Codex: set `model_reasoning_effort = "medium"` in `~/.codex/config.toml`.

## Step 4: switch on the advisor and use it once

- Do: `/advisor opus`
- Expect: `Advisor Tool (experimental) is on` when the next session starts.
- Do: give one real hard call and add "consult the advisor before you pick the approach".
- Expect: an `Advising` line while it runs.
- Check: press `Ctrl+O` to read the advice. `models-check` shows `advisor  opus`.
- If it says the advisor is less capable than the main model, pick Opus or Fable for an Opus main model.

## Step 5: check usage

- Do: `/usage`
- Expect: plan usage bars and what used them.
- If it offers `f to fix`, press `f` to apply the fixes it can.

## Step 6: add a second login (only if the member has a second subscription)

Option A, any terminal:

- Do: `models-check login add <label>` (for example `work`).
- Expect: the sign-in command and an alias line.
- Do: `CLAUDE_CONFIG_DIR=~/.claude-<label> claude auth login`, sign in with the second subscription in the browser.
- Do: add the printed `alias claude-<label>=...` line to `~/.zshrc` (or `~/.bashrc`), then open a new terminal.
- Check: `claude-<label>`, then `/status`, shows the second account. `models-check` ends with
  `Claude logins ready for failover: 2`.
- Remind: plugins and chat history are per folder. Install the aios packs inside `claude-<label>` too.

Option B, bb:

- Do: `bb pool account add --provider claude --login`, then
  `bb pool account login-complete --session <id> --code-stdin` with the code from the browser.
- Do: `bb pool routing claude`
- Check: `bb pool account list` shows both accounts enabled. Lower priority numbers run first:
  `bb pool account priority <id> 10`.

## Step 7: check it all

- Do: `models-check --strict`
- Expect: exit 0, no warnings.

## Done

Module 10 is complete when effort is medium, the advisor has been used once, and (if they have two subscriptions)
two logins are ready. Ask the member to confirm, then hand back to `/aios`.
