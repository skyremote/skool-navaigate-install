---
type: llm
---

PASS if the response warns that uncapped full text can blow up the context and caps it (--max-chars) or starts with highlights.
FAIL if it plans to pull 30 uncapped full pages.
