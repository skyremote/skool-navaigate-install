---
name: your-ops
description: >
  Help them componentize THEIR invoice or ops template from a real document they sent. Use when they type /your-ops. Never ship NavAIgate letterhead or KG register facts.
---

# /your-ops

They componentize one real invoice (or the ops doc they actually send).
They do not get NavAIgate letterhead, the KG Steuernummer, or Qonto.

The public scaffold is `invoice-builder`:
https://github.com/skyremote/invoice-builder

That skill builds **their** branded-document generator from a `.docx` they
already sent. It does not copy Daniel's template.

## Do this

1. Ask them to bring one invoice they sent this year.
2. Clone `invoice-builder` if it is not on the machine, and point it at
   **their** document.
3. Turn that into a template with their legal block and their number
   sequence.
4. Stop. Do not build a finance OS.

Then `/aios`.
