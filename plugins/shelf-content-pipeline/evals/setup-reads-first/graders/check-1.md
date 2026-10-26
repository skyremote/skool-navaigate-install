---
type: llm
---

PASS if the response checks for the member's CLAUDE.md first, runs or lists the foundation commands (db.py, generate_pipeline.py), asks the strategy questions two or three at a time and gets a yes on each document before the next.
FAIL if it asks twenty questions at once or skips the foundation.
