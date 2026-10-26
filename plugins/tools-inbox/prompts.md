# Prompts: tools-inbox

Paste one into Claude Code, Codex or Cursor. Nothing here sends email.

## 1. Practise on a sample brief (no account needed)

```text
Use tools-inbox. Make the practice brief in ~/Inbox-practice, explain the three piles to me, then run the check.
```

**What it does:** writes a brief for a fictional Acme Studio inbox and walks you through Action needed, Waiting on
and FYI.
**How you know it worked:** the check prints `PASS: 2 need action, 1 waiting, 1 FYI. Nothing was sent.`

## 2. What needs a reply today

```text
Use tools-inbox. Read my inbox from the last two days and list what needs a reply today, with a one-line draft for each. Do not send anything.
```

**What it does:** reads your Gmail through your own Composio connection, sorts it into the three piles and writes a
checked brief.
**How you know it worked:** every item shows the sender, the date and the subject, so you can find it in Gmail, and
the check says `PASS`. Your Sent folder has nothing new.

## 3. A full reply, left in your Drafts

```text
Use tools-inbox. Write a full reply to the most recent email from Northwind and save it as a draft in my Gmail. Do not send it.
```

**What it does:** fetches the email, writes the reply and saves it with the create-draft tool.
**How you know it worked:** the reply is in your Gmail Drafts folder, and nothing new is in Sent. If the agent tries
to send, the guard blocks it and says why.
