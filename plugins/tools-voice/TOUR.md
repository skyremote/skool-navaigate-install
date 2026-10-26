# Tour: module 12, tools: voice

`/aios learn 12 tools-voice` follows these steps, one at a time. Show the real output, then check it.
Use only the member's own words. Keep their transcripts out of any shared or public folder.

## Step 1: Find the command
- **Command:** `tools-voice --version`
- **They should see:** `tools-voice 2.0.0`.
- **Check:** exit code 0. If missing, `export PATH="$HOME/.local/bin:$PATH"` or `/aios install tools-voice`.

## Step 2: Install the public tool
- **Command:** `tools-voice doctor`, then the `git clone` line it prints, then `tools-voice doctor` again.
- **They should see:** `voice-skill-builder: found at ...`.
- **Check:** exit code 0.

## Step 3: See a draft fail
- **Command:** `tools-voice sample ~/Voice-practice`, then `tools-voice check ~/Voice-practice/draft-bad_v1.md`
- **They should see:** `FAIL` with banned words and a fragment chain. Then `draft-good_v1.md` passes.

## Step 4: Make their voice skill
- **Command:** `tools-voice new "<their first name>"`
- **They should see:** `Made your voice skill: ~/.claude/skills/<name>-voice`.
- **Check:** the folder has SKILL.md, PROFILE.md and EXAMPLES.md.

## Step 5: Their evidence
- **Do:** they put three or more of their own transcripts or sent emails in a private folder.
- **Command:** `tools-voice evidence <folder> --speaker "<their label>" --out <private folder>/VOICE_EVIDENCE.md`
- **They should see:** `Wrote ... from N file(s)`.
- **Check:** the digest lists their openers and quotes. Then the agent fills in PROFILE.md, a quote per rule.

## Step 6: Correct three test pieces
- **Do:** the agent writes an email, a post and a teaching paragraph. The member edits lines.
- **Command:** `tools-voice calibrate --profile ... --before "..." --after "..." --lesson "..."` per edit.
- **Check:** the Calibration log has at least one entry, and approved pieces are in EXAMPLES.md.

## Recap
Install the public tool, see the check, make the skill, pull your evidence, correct three pieces. Every draft is checked.
