# shelf-invoices guide

## Install the tools once

```sh
python3 -m pip install --user reportlab pypdf
```

ReportLab draws the PDF (BSD licence). pypdf reads it back for `verify` (BSD licence). Without pypdf, verify uses
`pdftotext` if it is installed, or checks the file's fingerprint and totals only.

## Commands

```sh
shelf-invoices init ~/Documents/Invoices                    # your books folder, now your default
shelf-invoices company check                                # what is still missing
shelf-invoices company set name="Acme Studio Ltd"           # one value at a time
shelf-invoices client add --name "Northwind Bakery Ltd" --address "22 Harbour Road;Bristol;BS8 4RU"
shelf-invoices client list
shelf-invoices draft --client northwind-bakery-ltd --item "Booking page redesign | 1 | 2400" --po NW-0042
shelf-invoices issue northwind-bakery-ltd_draft_v1 --yes    # the member's decision
shelf-invoices verify ACME-2026-0001
shelf-invoices list --year 2026
shelf-invoices credit ACME-2026-0001 --reason "Workshop cancelled" --yes
shelf-invoices sample ~/Invoices-practice                   # fictional books, not your default
```

Every command takes `--books <folder>` to use books other than your default.

## Company details (`company.json` in your books folder)

| Key | Example | Notes |
|---|---|---|
| `name` | `Acme Studio Ltd` | Your legal name, as registered |
| `address` | `1 Example Street;Bristol;BS1 1AA;United Kingdom` | Lines separated by `;` |
| `email`, `phone`, `website` | | Shown under your address |
| `vat_registered` | `true` | `false` means no VAT is charged and the invoice says so |
| `vat_id` | `GB123456789` | Required when VAT registered |
| `tax_label` | `VAT` | Change to `GST`, `IVA`, `MwSt` if your country uses another word |
| `tax_number`, `company_number` | | Shown if set |
| `legal_lines` | `Registered in England and Wales, number 01234567` | Footer lines, separated by `;` |
| `bank.account_name`, `bank.bank_name`, `bank.iban`, `bank.bic`, `bank.sort_code`, `bank.account_number` | | Shown under "How to pay" |
| `currency` | `GBP` | Default currency. Any three-letter code works |
| `vat_rate` | `20` | Default rate for a line that does not give one |
| `payment_terms_days` | `30` | Due date = invoice date + this |
| `prefix`, `credit_prefix` | `ACME`, `CN` | |
| `number_format` | `{prefix}-{year}-{seq:04d}` | May use `{prefix}`, `{year}`, `{month}`, `{seq}` |
| `number_reset` | `yearly` | `yearly` starts at 0001 each year, `never` keeps counting |
| `logo` | `~/Brand/logo.png` | PNG or JPG |
| `accent` | `#2B5D8A` | The title and table colour |
| `font_file`, `font_bold_file` | `~/Fonts/Brand.ttf` | Optional TTF fonts, embedded in the PDF |
| `footer_note` | `Thank you for your business.` | Optional last line |

`company.json`, `clients.json` and the ledger are written with private permissions (only you can read them),
because they hold bank details. Do not put the books folder in a public repository.

## Lines and VAT

Each `--item` is `"Description | quantity | unit price"` with an optional `| VAT %` on the end. The VAT is worked
out per rate, rounded half up to the cent, and shown as one row per rate.

| `--vat-mode` | VAT charged | Note printed |
|---|---|---|
| `standard` (default) | each line's rate | none |
| `reverse-charge` | 0 | "Reverse charge: the customer must account for the VAT on this supply." Needs the client's VAT ID |
| `zero-rated` | 0 | "Zero-rated supply." |
| `exempt` | 0 | "Exempt from VAT." |
| `outside-scope` | 0 | "Outside the scope of VAT." |
| `not-registered` | 0 | "Not registered for VAT, so no VAT is charged." Used automatically when `vat_registered=false` |

Rules differ by country. If you are not sure which mode applies, ask your accountant before you issue.

## Files

```
~/Documents/Invoices/
  company.json  clients.json  ledger.json  ledger.csv
  drafts/northwind-bakery-ltd_draft_v1.json|.pdf   (DRAFT watermark, no number)
  2026/ACME-2026-0001_northwind-bakery-ltd.pdf      (issued, never edited)
  2026/ACME-2026-0001_northwind-bakery-ltd.json     (what it was made from)
```

## Common problems

| Message | Fix |
|---|---|
| "No books folder yet" | `shelf-invoices init <folder>` |
| "Finish your company details first" | `shelf-invoices company check`, then set each missing value |
| "Reverse charge needs the client's VAT ID" | Add `--to-vat-id`, or `client add` again with `--vat-id` |
| "does not fit on one page" | Combine small lines or shorten descriptions |
| "This draft was already issued" | Make a new draft. Each draft issues once |
| "The PDF changed after it was issued" | Restore the file from your backup. Never edit an issued PDF |
| A wrong amount on an issued invoice | `shelf-invoices credit <number> --reason "..." --yes`, then draft and issue the right one |
