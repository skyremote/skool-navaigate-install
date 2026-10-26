---
type: llm
---

PASS if the response keeps the HTML-first method: it proposes or asks to agree the slide titles (one point per slide), and says it will render the HTML deck and look at every slide (screenshots or a visual review) before handing over the PowerPoint, even though the user asked to skip it, giving a short reason (for example that crowding and errors show up only when you look).
FAIL if the response writes or exports the PowerPoint directly with no HTML render and no slide-by-slide review step, or builds slides by hand in python-pptx or raw HTML instead of a deck spec.
