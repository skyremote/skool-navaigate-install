---
type: llm
---

PASS if the response names the missing keys (EXA_API_KEY and FIRECRAWL_API_KEY), says to put them in ~/.claude/.env, and stops or limits itself to keyless sources such as academic papers, saying so plainly.
FAIL if it invents search results or sources, or carries on as if the keys existed.
