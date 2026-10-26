# Prompts: tools-whatsapp

Paste one into Claude Code, Codex or Cursor.

## 1. Practise on a sample chat

```text
Use tools-whatsapp. Make the practice chat in ~/WhatsApp-practice and list every date and price the builder mentioned, with the message each came from.
```

**What it does:** makes a fictional chat with a builder in whatscribe's format and pulls out the amounts and dates.
**How you know it worked:** you see £350 and £1,240, Thursday 8am and 24th October, each with its date and sender,
and the voice-note ones are marked.

## 2. This week with someone

```text
Use tools-whatsapp. Sync my WhatsApp, then summarise my chat with the builder from this week: what we agreed, what is still open, and every date and price, quoted.
```

**What it does:** runs `whatscribe sync`, narrows to this week, extracts and summarises.
**How you know it worked:** each figure has the date and a short quote, and anything from a voice note says so.

## 3. What did they say in the voice notes?

```text
Use tools-whatsapp. Read only the voice notes from my chat with Mum since Monday and tell me what she asked me to do.
```

**What it does:** filters to voice notes since Monday and reads their transcripts.
**How you know it worked:** the answer lists each request with the time of the voice note it came from.
