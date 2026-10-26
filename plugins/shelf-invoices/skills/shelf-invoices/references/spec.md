# spec.json: one invoice

Write one spec per invoice in `<books>/drafts/`, then run `shelf-invoices make <spec.json>`.
`make` saves a copy beside the draft as `<number>_vN.spec.json`, so you can see later what each invoice was made from.

```json
{
  "date": "2026-10-26",
  "title": "AI workshop delivery",
  "subtitle": "Berlin · 20–22 October 2026",
  "client_name": "Contoso GmbH",
  "client_address": "Musterstraße 1, 10115 Berlin, Germany",
  "client_vat_id": "DE000000000",
  "requester": "Jana Weber",
  "po_number": "PO-7781",
  "currency": "EUR",
  "intro": "Our invoice for the three-day AI workshop for your team.",
  "items": [
    {"title": "Workshop delivery", "description": "Three days on site: preparation, delivery, handover",
     "quantity": 3, "unit": "days", "unit_price": 1200}
  ],
  "service_date": "20–22 October 2026",
  "vat": "reverse_charge_eu",
  "payment_days": 14
}
```

| Field | Notes |
|---|---|
| `invoice_number` | Leave it out: `make` takes the highest number used + 1. Set it only to make a new version of a draft. |
| `client_code` | Optional: numbers this invoice in its own series, `PREFIX-CODE-NNN`. |
| `date` | `YYYY-MM-DD`. Today if left out. Also decides the `<year>/<month>/` folder it is filed in. |
| `title`, `subtitle` | The big heading and the line under it. An empty subtitle drops the line. |
| `client_name`, `client_address` | The legal entity on the PO. The address is a string or a list of lines. |
| `client_vat_id` | Shown under the address. Needed for `reverse_charge_eu`. |
| `requester`, `client_extra` | Optional lines under the address (a cost centre, a requisition number). |
| `po_number`, `po_extra` | Quote the PO whenever there is one. `po_extra` follows it, e.g. `"Supplier ID 1234"`. |
| `currency` | Follows the PO. `GBP`, `EUR` and `USD` get £, € and $; other codes are written out (`CHF 1,200.00`). |
| `greeting`, `intro` | Default: "Dear <requester's first name>," and "Our invoice for the work below." |
| `items` | Each: `title`, optional `description`, and `amount`, or `quantity` + `unit_price` (+ `unit`). One row each. |
| `total_note` | Small text after "Total due", e.g. `"(all-in, including travel)"`. |
| `service_date` | The date or period of the work. Most tax rules want it. |
| `vat`, `vat_rate` | The mode (see settings.md) and, for `standard`, the rate. Defaults from company.json. |
| `vat_label`, `vat_text` | One-off wording for this invoice only. |
| `payment_days` or `payment_terms` | Days for the standard sentence, or the whole sentence word for word. |

## What `make` checks

- No `{{field}}` is left unfilled in any part of the .docx.
- No other currency's sign is on the invoice (no € left on a GBP invoice).
- The PDF is one page (when LibreOffice is installed).
- The number is not already filed, and no file is ever overwritten.

Then you look at the PDF yourself. The command cannot see whether the logo looks right or a line wraps badly.
