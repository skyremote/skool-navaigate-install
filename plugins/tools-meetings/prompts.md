# Prompts: tools-meetings

Paste one into Claude Code, Codex or Cursor. Change the names to your own.

## 1. Practise on the sample call (no account needed)

```text
Use tools-meetings. Make the practice call in ~/Meetings-practice, fill in the decision record from the transcript, then run the check and show me the result.
```

**What it does:** makes a fictional call between Acme Studio and Northwind Bakery, then writes the decisions, the
actions with owners and the open questions from it.
**How you know it worked:** the last line of the check says `PASS: every owner, number and quote is in the transcript.`

## 2. Your last real call, as decisions and owners

```text
Use tools-meetings. Find my most recent Granola meeting, save the transcript, and give me the decisions, every action with its owner and due date, and the open questions. Run the check before you show me.
```

**What it does:** reads your newest Granola meeting with your own key and writes a checked decision record next to
the saved transcript.
**How you know it worked:** you see two new files ending `_transcript_v1.txt` and `_record_v1.md`, and the check says
`PASS`. Any owner it could not find in the call says `not stated`.

## 3. The follow-up email, drafted, not sent

```text
Use tools-meetings. From my call with Northwind this week, draft a short follow-up email with what we agreed and who does what next. Do not send anything.
```

**What it does:** finds the call by its title, builds the record, then drafts the email from the record only.
**How you know it worked:** every action in the email also appears in the record, with the same owner, and nothing
was sent.
