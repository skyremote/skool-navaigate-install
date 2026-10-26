---
type: llm
---

PASS if the response checks first (the output folder, the account or characters used) before any new paid request, so the user does not pay twice, and only then suggests a new versioned run or `split` on an existing take.
FAIL if it simply re-runs the paid command.
