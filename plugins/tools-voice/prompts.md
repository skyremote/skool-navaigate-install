# Prompts: tools-voice

Paste one into Claude Code, Codex or Cursor.

## 1. See what "sounds like AI" means (no setup)

```text
Use tools-voice. Make the practice files in ~/Voice-practice, check both drafts, and explain why one fails and one passes.
```

**What it does:** makes a fictional transcript and two drafts, and runs the check on both.
**How you know it worked:** the bad draft prints `FAIL` with words like "seamless" and a fragment chain, and the good
one prints `PASS`.

## 2. Build your voice from your own calls

```text
Use tools-voice. Build my writing voice from the transcripts in ~/Private/my-calls. My name in them is "Sam". Make the skill, fill in the profile from the evidence with a quote behind each rule, then write me a short email, a LinkedIn post and a teaching paragraph to correct.
```

**What it does:** runs voice-skill-builder on your words, makes `sam-voice/` in your skills folder, and writes three
test pieces.
**How you know it worked:** every rule in PROFILE.md has a quote from your own calls, and you get three drafts to edit.

## 3. Rewrite an email so it sounds like you

```text
Use tools-voice and my voice skill. Rewrite this email so it sounds like me, run the check against my profile, and show me what you changed: <paste the email>
```

**What it does:** rewrites with your profile and checks the result.
**How you know it worked:** the check says `PASS`, and when you read it aloud you could say it on a call. If you change
a line, ask it to record your correction with `calibrate`.
