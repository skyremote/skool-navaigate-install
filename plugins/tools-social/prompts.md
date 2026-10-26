# Prompts: tools-social

Paste one into Claude Code, Codex or Cursor.

## 1. See the gate before you connect anything

```text
Use tools-social. Make the practice post pack in ~/Social-practice, check it, then show me what happens if you try to post it without a release time.
```

**What it does:** writes a fictional Northwind Bakery pack, checks it, and shows the gate refusing to post.
**How you know it worked:** the check says `PASS`, and the gate answers with "When should this go live?".

## 2. One video, every platform, scheduled

```text
Use tools-social. Turn this transcript into a LinkedIn post and an X post, show me both, and schedule them for Tuesday 9am London time only after I say publish: <paste transcript or file path>
```

**What it does:** writes and checks the two posts, then waits for your words before scheduling through Blotato.
**How you know it worked:** you see both posts and a `PASS`; after you confirm, it shows the scheduled time in local
and UTC, and Blotato's receipt for each.

## 3. Copy approved, timing not yet

```text
Use tools-social. I love these posts, get them ready for Blotato.
```

**What it does:** prepares everything (accounts matched, copy checked) and stops.
**How you know it worked:** it asks for the date, time and timezone, or "publish now", and nothing is posted.
