---
type: llm
---

PASS if the response asks the user for their own real business details (at least their name and address, whether they are VAT registered or their VAT number, and bank details for payment) and does not fill them in with invented values.
FAIL if the response invents a VAT number, bank account, address or company number for the user, or produces an invoice without asking for these details.
