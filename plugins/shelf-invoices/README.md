# shelf-invoices (AIOS 2.0, module 12: the shelf)

Create, number and file invoices as PDF from your own company details. VAT is worked out per line, reverse charge
and other VAT notes are built in, and a ledger keeps every number in order for your accountant.

- **Your company, your books.** Your details live in your own books folder. No company template is included.
- **Drafts first.** A draft has a preview and no number. Issuing gives the permanent number, and only you issue.
- **Never edited.** Issued PDFs are fingerprinted. A mistake gets a credit note, never a deletion.
- **Local.** No account, no API, no upload.

## Install

Install the start plugin `aios` first.

Claude Code:
```
/plugin marketplace add skyremote/skool-navaigate-install
/plugin install shelf-invoices@navaigate-aios
```

Codex and Cursor, from your checkout of this repository:
```
./install.sh aios
./install.sh shelf-invoices
```

Then the tools, once: `python3 -m pip install --user reportlab pypdf`. Works on macOS and Linux (WSL on Windows).

## Use

```
shelf-invoices init ~/Documents/Invoices
shelf-invoices company set name="Acme Studio Ltd"
shelf-invoices company check
shelf-invoices client add --name "Northwind Bakery Ltd" --address "22 Harbour Road;Bristol;BS8 4RU"
shelf-invoices draft --client northwind-bakery-ltd --item "Booking page redesign | 1 | 2400"
shelf-invoices issue northwind-bakery-ltd_draft_v1 --yes
shelf-invoices verify ACME-2026-0001
```

`shelf-invoices sample ~/Invoices-practice` makes practice books for the fictional Acme Studio Ltd.

Every setting, VAT mode and fix: [skills/shelf-invoices/references/invoices.md](skills/shelf-invoices/references/invoices.md).

This pack is not tax advice. Rules about what an invoice must show differ by country: check with your accountant.

## Licence

MIT. Dependencies are installed by you: ReportLab (BSD), pypdf (BSD).
