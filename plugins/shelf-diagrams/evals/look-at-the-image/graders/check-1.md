---
type: llm
---

PASS if the response writes or plans D2 source (diagrams/<slug>.d2), renders it to PNG, and says it will look at the picture and fix overlaps before handing it over; it may ask what the diagram is for first.
FAIL if it uses Mermaid, Excalidraw or a canvas tool instead of D2, or hands over the first render unseen.
