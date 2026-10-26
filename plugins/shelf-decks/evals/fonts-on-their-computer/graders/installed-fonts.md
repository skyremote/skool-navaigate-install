---
type: llm
---

PASS if the response explains that the fonts are not installed on the client's computer, so PowerPoint substitutes another font, and recommends sending a PDF (for example made with `shelf-decks export --pdf`) or having the client install the font.
FAIL if it blames the export as broken, or suggests turning the slides into pictures as the main fix without mentioning the PDF.
