# 12 · The shelf: invoices
pack: shelf-invoices
cmd: shelf-invoices

## 12i.1 · Practise on sample books
what: Makes practice books for the fictional Acme Studio, makes a practice invoice to Contoso from the example spec, checks the PDF with you, and files it. A filed invoice is never changed.
check: The report shows invoice ACME-002, total €3,600.00 on one page, and the filed path. Filing it again says it is already filed.
~~~
Set up the invoices pack from the shelf and practise on sample books. These are practice books for a fictional company, not mine.

<<INSTALL>>

1. Check the command: `shelf-invoices --version` should print `shelf-invoices 2.0.1` or later.
2. Check the tools: `python3 -c "import lxml; print('ok')"` and `soffice --version`. If lxml is missing, install it with `python3 -m pip install --user lxml` and check again. If LibreOffice is missing, tell me to install it from libreoffice.org: until then only the Word file is made.
3. Make the practice books in this folder: `shelf-invoices sample 30_finance/invoices-practice`. Then `shelf-invoices next-number --books 30_finance/invoices-practice` should print `ACME-002`.
4. Make the practice invoice from the example: `shelf-invoices make 30_finance/invoices-practice/examples/contoso-workshop.json --books 30_finance/invoices-practice`. Show the number, the total, the file paths and the checks line.
5. Check the PDF with me in the report: the Acme logo, Contoso's VAT ID under its address, PO-7781, the service date, € everywhere, the reverse-charge line and the SAMPLE bank details. Say what you checked.
6. File it, as I would after approving it: `shelf-invoices file ACME-002 --books 30_finance/invoices-practice`. Then run the same command again: it should say it is already filed.

<<RULES>>

<<FINISH m12-invoices-practice>>
~~~

## 12i.2 · Set up your own invoice books
what: Creates your real books folder and fills in your company details from your own lines. It leaves out anything you did not give, such as a VAT number or bank details, and lists what is still missing. It makes and files nothing.
check: `shelf-invoices company check` shows what is complete and names each missing detail. No invoice is made or filed.
~~~
My company details (edit these lines before you send; leave a line empty if you do not want to give it now):
- Company name: Acme Studio Ltd
- Address: 1 Mill Lane, Leeds, LS1 4AB, United Kingdom
- VAT registered: no
- Invoice number prefix: ACME
- Currency: GBP
- Bank IBAN:

Set up my own invoice books with the shelf invoices pack. If the pack is not set up yet, run prompt 12i.1 first.

<<INSTALL>>

1. Create my books: `shelf-invoices init 30_finance/invoices`. It writes `company.json` with empty fields and makes this my default books folder.
2. Open `30_finance/invoices/company.json` and fill in only the details I gave above, in the fields that match them. Never guess a VAT number, an address, a company number or a bank detail. Leave every field I did not give empty.
3. Run `shelf-invoices company check` and show me what is complete and what is missing.
4. Do not make or file an invoice. Tell me the one thing I do next: give you the missing details from my own paperwork, then ask for my first invoice in plain words, for example "Make an invoice to <client> for <work> at <price> and show me the PDF".
5. Tell me that a filed invoice is never changed: a mistake gets a new invoice, and my accountant says which wording I need.

<<RULES>>

<<FINISH m12-invoices-own>>
~~~
