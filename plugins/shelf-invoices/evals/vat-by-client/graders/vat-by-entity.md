---
type: llm
---

PASS if the response explains that the VAT treatment follows the customer's legal situation (a VAT-registered business established in Germany) rather than where the workshop took place, proposes a no-VAT treatment for this business customer abroad (`outside_scope` or `reverse_charge_eu`, saying reverse charge applies) instead of adding 20% UK VAT, and suggests the user confirms with their accountant, keeps the currency as EUR, and puts the PO number PO-7781, the client VAT ID and a service date of 20 October 2026 in the spec.
FAIL if the response simply adds 20% UK VAT because the work happened in London, changes the currency to GBP, or leaves out the PO number.
