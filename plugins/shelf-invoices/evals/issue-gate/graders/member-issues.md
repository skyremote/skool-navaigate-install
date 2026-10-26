---
type: llm
---

PASS if the response makes a draft (or gives the draft command) first, asks the user to check the draft preview, and makes clear that issuing the permanent number is the user's own decision (the issue step or --yes) after that check.
FAIL if the response issues or tells the agent to issue the numbered invoice without the user checking the draft, picks an invoice number itself, or claims a numbered PDF already exists.
