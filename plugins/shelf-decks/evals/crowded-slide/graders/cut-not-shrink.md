---
type: llm
---

PASS if the response fixes the crowding by cutting words from the labels or splitting the slide into two (or moving detail into the talk notes), explains that shrinking the type is not the fix, and says the next render is a new version (for example `_v2`) rather than overwriting the file that was sent, then looks at the slide again before export.
FAIL if the response makes the font smaller, edits a font size, or overwrites the existing PowerPoint.
