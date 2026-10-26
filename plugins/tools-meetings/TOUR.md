# Tour: module 12, tools: meetings

`/aios learn 12 tools-meetings` follows these steps in the member's own folder, one at a time.
Run each command for the member, or have them type it. Show the real output, then check it before the next step.
Never ask for the key in the chat. If a check fails, stop, fix that one thing, and check again.

## Step 1: Find the command
- **Do:** check that the pack's command runs.
- **Command:** `tools-meetings --version` (Claude Code: `"${CLAUDE_PLUGIN_ROOT}/bin/tools-meetings" --version`).
- **They should see:** `tools-meetings 2.0.0`.
- **Check:** exit code 0. If the command is missing, run `export PATH="$HOME/.local/bin:$PATH"` (Codex and Cursor),
  or `/aios install tools-meetings`, then `/reload-plugins`.

## Step 2: Practise on the sample call
- **Do:** make the fictional Northwind Bakery call and an empty record.
- **Command:** `tools-meetings sample ~/Meetings-practice`
- **They should see:** the transcript path and the record path.
- **Check:** `ls ~/Meetings-practice` shows both files.

## Step 3: See the check fail on purpose
- **Do:** run the check on the empty record.
- **Command:** `tools-meetings check ~/Meetings-practice/northwind-kickoff_record_v1.md --source ~/Meetings-practice/northwind-kickoff_transcript_v1.txt`
- **They should see:** `FAIL` and `template placeholders`.
- **Check:** exit code 1. This is the guard that stops invented owners and numbers.

## Step 4: Fill in the record and pass
- **Do:** the agent fills in the record from the transcript, using the rules in the skill.
- **Command:** the same `check` command as step 3.
- **They should see:** `PASS: every owner, number and quote is in the transcript.`
- **Check:** the record has Decisions, Actions (each with Owner and Due), Open questions and Source.

## Step 5: Connect Granola
- **Do:** the member creates their own key in Granola (Settings, Connectors, API keys) and adds it. Claude Code:
  `/plugin`, tools-meetings, Configure. Codex and Cursor: `export GRANOLA_API_KEY=...` in their shell profile.
- **Command:** `tools-meetings doctor`
- **They should see:** `Granola API key: found in your ... (not shown)`.
- **Check:** exit code 0. Exit code 2 means the key is still missing.

## Step 6: Their first real call
- **Do:** list meetings, then save one transcript.
- **Command:** `tools-meetings list 5`, then `tools-meetings transcript <id> --me "<their first name>" --out ~/Meetings/<slug>_transcript_v1.txt`
- **They should see:** five meetings with ids, then `Saved the transcript to ...`.
- **Check:** the file opens and their own lines carry their name.

## Step 7: The real record
- **Do:** `new`, fill in, `check`, as in steps 3 and 4.
- **They should see:** `PASS`.
- **Check:** they read every action and agree with each owner.

## Recap
Sample, fail on purpose, pass, connect your key, one real call, one checked record. Nothing is ever sent for you.
