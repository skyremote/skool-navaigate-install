# Tour: module 12, tools: inbox

`/aios learn 12 tools-inbox` follows these steps in the member's own folder, one at a time.
Run each command for the member, or have them type it. Show the real output, then check it before the next step.
Never ask for a key or the Composio URL in the chat. Never send email.

## Step 1: Find the command
- **Do:** check that the pack's command runs.
- **Command:** `tools-inbox --version` (Claude Code: `"${CLAUDE_PLUGIN_ROOT}/bin/tools-inbox" --version`).
- **They should see:** `tools-inbox 2.0.0`.
- **Check:** exit code 0. If missing, `export PATH="$HOME/.local/bin:$PATH"` or `/aios install tools-inbox`.

## Step 2: The guard
- **Do:** show that sending is blocked before any inbox is connected.
- **Command:** `echo '{"tool_name":"mcp__composio-gmail__GMAIL_SEND_EMAIL"}' | tools-inbox guard`
- **They should see:** `"permissionDecision": "deny"`.
- **Check:** the same command with `GMAIL_CREATE_EMAIL_DRAFT` prints nothing (drafts are allowed).

## Step 3: Practise on the sample brief
- **Do:** make and check the fictional brief.
- **Command:** `tools-inbox sample ~/Inbox-practice`, then `tools-inbox check ~/Inbox-practice/inbox-brief_practice_v1.md`
- **They should see:** `PASS: 2 need action, 1 waiting, 1 FYI. Nothing was sent.`
- **Check:** exit code 0.

## Step 4: Connect their Gmail
- **Do:** the member makes a Composio account, connects Gmail, creates the MCP URL and adds it (README step 3).
- **Command:** Claude Code: `claude mcp list`
- **They should see:** `composio-gmail` with a connected status.
- **Check:** in a new session, the Gmail tools appear.

## Step 5: The first real triage
- **Do:** run prompt 2 from prompts.md.
- **They should see:** a brief with the three piles and a `PASS` from the check.
- **Check:** they find two of the emails in Gmail by the sender and date shown. Nothing new in Sent.

## Step 6: A reminder to themselves (optional)
- **Do:** add the Composio API key (plugin settings or shell), then send one reminder.
- **Command:** `tools-inbox doctor`, then `tools-inbox remind --subject "Test" --body "Reminder from my AIOS" --yes`
- **They should see:** `Sent the reminder to your own address, ...`.
- **Check:** it arrives in their own inbox. `tools-inbox schedule ...` prints the cron line for a recurring one.

## Recap
Guard first, practise, connect your own Gmail, triage, draft. Nothing is ever sent for you.
