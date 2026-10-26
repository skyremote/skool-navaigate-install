# company.json: your identity on every invoice

`shelf-invoices init <folder>` writes this file with every field empty. Fill it from your own paperwork.
`shelf-invoices company check` tells you what is still missing. Nothing in it is secret: it is what every
client sees on your invoice. Keep the folder somewhere you back up.

| Field | Example | Where it shows |
|---|---|---|
| `company_name` | `"Acme Studio Ltd"` | sender block, footer |
| `address` | `["Unit 4, 10 Example Lane", "Bristol BS1 0AA", "United Kingdom"]` | sender block and footer, joined with ` · ` |
| `country` | `"the UK"` | the `{country}` field in VAT wording |
| `phone`, `email`, `website` | `"+44 117 496 0000"` | sender block (`T` is added before the phone) |
| `vat_id`, `vat_id_label` | `"GB000000000"`, `"VAT ID"` | sender block and the tax row |
| `tax_number`, `tax_number_label` | `"12345 67890"`, `"UTR"` | tax row (leave empty if you have none) |
| `legal_footer` | a list of lines: company number, registered office, directors | small print at the bottom |
| `bank` | `bank_name`, `account_name`, `iban`, `bic`, `sort_code`, `account_number` | bank row |
| `bank_line` | `"Sample Bank · Sort code 00-00-00 · Account 00000000"` | replaces the bank row built from `bank` |
| `invoice_prefix`, `number_digits` | `"ACME-"`, `3` | numbers: `ACME-001`, or `ACME-NW-001` with `--code NW` |
| `currency` | `"GBP"` | default when the spec gives none |
| `payment_days` | `14` | "Payment terms: net 14 days" |
| `footer_note` | `"Thank you for your business."` | added after the payment terms |
| `signatory`, `closing` | `"Alex Morgan"`, `"Best,"` | sender name and sign-off |
| `logo` | `"logo.png"` | top left; a PNG, relative to the books folder |
| `vat_mode`, `vat_rate` | `"standard"`, `20` | default VAT treatment and rate |
| `vat_wording` | see below | the VAT row's label and text, per mode |
| `service_date_label` | `"Service date"` | "Service date: 20–22 October 2026." |
| `client_vat_id_label` | `"VAT ID"` | under the client's address |
| `date_short_format` | `"%d.%m.%Y"` | the footer reference date |

## VAT wording

The command ships neutral English wording for each mode. Your country may require set words (for example a
legal reference for reverse charge). Put your accountant's wording in `vat_wording`; anything you leave out keeps
the default. Fields you can use: `{rate}`, `{net}`, `{client_vat_id}`, `{country}`.

```json
"vat_wording": {
  "reverse_charge_eu": {"label": "EU business customer: ",
                        "text": "reverse charge, no VAT charged; the customer accounts for the VAT"},
  "outside_scope": {"label": "Customer outside {country}: ",
                    "text": "no VAT charged (place of supply outside {country})"}
}
```

| Mode | Use when | VAT row shows |
|---|---|---|
| `standard` | you charge VAT at `vat_rate` | the VAT amount; the total includes VAT |
| `reverse_charge_eu` | you are in the EU and the customer is a business in another EU country (needs `client_vat_id`) | the total |
| `outside_scope` | a business customer abroad, when you are outside the EU (a UK company billing a German one, for example) | the total |
| `outside_eu` | the customer is outside the EU | the total |
| `domestic_reverse_charge` | a domestic reverse-charge sector (construction, for example) | the total |
| `not_registered` | you are not registered for VAT | the total |

Which mode applies depends on the customer's legal entity and where it is established, not on where you did the
work. Your accountant decides. This pack is not tax advice.

## Fonts

The design uses Poppins and Fraunces (both free, SIL Open Font Licence, from fonts.google.com). Install them so the
PDF matches the design; without them LibreOffice substitutes similar fonts.
