# 12 · The shelf: invoices
pack: shelf-invoices
cmd: shelf-invoices

## 12i.1 · Practise on sample books
what: Makes practice books for the fictional Acme Studio, drafts and issues a practice invoice, verifies the PDF, and cancels it with a credit note.
check: `shelf-invoices verify ACME-2026-0001` says PASS, and the ledger shows both the invoice and its credit note.
~~~
Set up the invoices pack from the shelf and practise on sample books. These are practice books for a fictional company, not mine.

<<INSTALL>>

1. Check the tools: `python3 -c "import reportlab, pypdf; print('ok')"`. If it fails, run `python3 -m pip install --user reportlab pypdf` and check again.
2. Make the practice books in this folder: `shelf-invoices sample 30_finance/invoices-practice`. Then `shelf-invoices client list --books 30_finance/invoices-practice` should show `northwind` and `contoso-de`.
3. Draft a practice invoice: `shelf-invoices draft --books 30_finance/invoices-practice --client northwind --item "Booking page redesign | 1 | 2400"`. Show the totals and the preview path.
4. Issue it (practice books only): `shelf-invoices issue northwind_draft_v1 --books 30_finance/invoices-practice --yes`. Show the number it gets.
5. Verify it: `shelf-invoices verify <the number> --books 30_finance/invoices-practice`. It must say PASS.
6. Show the right way to fix a mistake: `shelf-invoices credit <the number> --books 30_finance/invoices-practice --reason "Practice: wrong amount" --yes`. Then show the last lines of `ledger.csv` in the practice books.

<<RULES>>

<<FINISH m12-invoices-practice>>
~~~

## 12i.2 · Set up your own invoice books
what: Creates your real books folder and fills in your company details from your own lines. It leaves out anything you did not give, such as a VAT number or bank details, and lists what is still missing. It issues nothing.
check: `shelf-invoices company check` shows what is complete and names each missing detail. No invoice is issued.
~~~
My company details (edit these lines before you send; leave a line empty if you do not want to give it now):
- Company name: Acme Studio Ltd
- Address: 1 Mill Lane; Leeds; LS1 4AB; United Kingdom
- VAT registered: no
- Invoice number prefix: ACME
- Currency: GBP
- Bank IBAN:

Set up my own invoice books with the shelf invoices pack.

<<INSTALL>>

1. Create my books: `shelf-invoices init 30_finance/invoices`. Show that `company.json`, `clients.json` and `ledger.json` exist.
2. Set each detail I gave above with `shelf-invoices company set key=value` (for example `name=...`, `address=...`, `vat_registered=false`, `prefix=...`, `currency=...`). Never guess a VAT number, an address or a bank detail. Skip every line I left empty.
3. Run `shelf-invoices company check` and show me what is complete and what is missing.
4. Do not draft or issue an invoice. Give me the two commands I run next: one to add my first client (`shelf-invoices client add --name "..." --address "..."`) and one to draft an invoice.
5. Tell me that an issued invoice is never edited or deleted; a credit note cancels it.

<<RULES>>

<<FINISH m12-invoices-own>>
~~~
