# Tour: module 12, the shelf: invoices

`/aios learn 12 invoices` follows these steps in the member's own folder, one at a time.
Run each command for the member, or have them type it. Show the real output, then check it before the next step.
Never issue, credit or delete an invoice for the member. If a check fails, stop, fix that one thing, and check again.

## Step 1: Find the command
- **Do:** check that the pack's command runs.
- **Command:** `shelf-invoices --version` (Claude Code: `"${CLAUDE_PLUGIN_ROOT}/bin/shelf-invoices" --version`).
- **They should see:** `shelf-invoices 2.0.0`.
- **Check:** exit code 0. If the command is missing, run `export PATH="$HOME/.local/bin:$PATH"` (Codex and Cursor),
  or restart Claude Code after `/plugin install shelf-invoices@navaigate-aios`.

## Step 2: Check the tools
- **Do:** confirm ReportLab (draws the PDF) and pypdf (checks it).
- **Command:** `python3 -c "import reportlab, pypdf; print('ok')"`
- **They should see:** `ok`.
- **Check:** if it fails, run `python3 -m pip install --user reportlab pypdf`, then again.

## Step 3: Practise on sample books
- **Do:** make books for the fictional Acme Studio Ltd. They are not the member's default.
- **Command:** `shelf-invoices sample ~/Invoices-practice`
- **They should see:** `Sample books for the fictional Acme Studio Ltd`.
- **Check:** `shelf-invoices client list --books ~/Invoices-practice` shows `northwind` and `contoso-de`.

## Step 4: Draft and issue a practice invoice
- **Do:** draft, look at the preview together, then the member issues it. These are practice books, so no real number is used.
- **Command:** `shelf-invoices draft --books ~/Invoices-practice --client northwind --item "Booking page redesign | 1 | 2400"`
  then `shelf-invoices issue northwind_draft_v1 --books ~/Invoices-practice --yes`
- **They should see:** a draft total with VAT, a preview PDF marked DRAFT, then `Issued ACME-2026-0001`.
- **Check:** `shelf-invoices verify ACME-2026-0001 --books ~/Invoices-practice` says `PASS`.

## Step 5: Make their own books
- **Do:** create the real books folder in a place they back up.
- **Command:** `shelf-invoices init ~/Documents/Invoices`
- **They should see:** `Books folder: ... (now your default)`.
- **Check:** `ls ~/Documents/Invoices` shows `company.json`, `clients.json` and `ledger.json`.

## Step 6: Their company details
- **Do:** ask for each value from their real paperwork. Never guess a VAT number or bank detail.
- **Command:** `shelf-invoices company set name="Their Company Ltd"`, then `address="line 1;line 2;postcode;country"`,
  `vat_id=...` (or `vat_registered=false`), `bank.iban=...`, `prefix=...`, `currency=GBP`, `vat_rate=20`, `logo=<png>`
- **They should see:** the details printed after each change.
- **Check:** `shelf-invoices company check` says `Company details complete.` If they are unsure what their
  country requires on an invoice, they ask their accountant.

## Step 7: Save a client
- **Do:** save one real client.
- **Command:** `shelf-invoices client add --name "Client Ltd" --address "line 1;line 2" [--vat-id ...] [--vat-mode reverse-charge]`
- **They should see:** `Saved client "client-ltd"` and the client list.
- **Check:** reverse charge needs the client's VAT ID. The draft refuses without it.

## Step 8: Draft the first real invoice
- **Do:** one `--item` per line: description, quantity, unit price, and an optional VAT rate.
- **Command:** `shelf-invoices draft --client client-ltd --item "Description | 1 | 1200" --po <their PO, if any>`
- **They should see:** net, VAT and total, and a preview path in `drafts/`.
- **Check:** they open the preview and check every line, the VAT and their bank details. Nothing is numbered yet.

## Step 9: The member issues it
- **Do:** wait until they say yes. Issuing gives the permanent number.
- **Command:** `shelf-invoices issue client-ltd_draft_v1 --yes`
- **They should see:** `Issued <PREFIX>-<year>-0001`, the total, the due date and the filed path.
- **Check:** `shelf-invoices verify <number>` says `PASS`, and `shelf-invoices list` shows it.

## Step 10: Fix a mistake the right way
- **Do:** show that an issued invoice is never edited or deleted. A credit note cancels it.
- **Command:** `shelf-invoices credit <number> --reason "<why>" --yes` (on the practice books only, for the tour)
- **They should see:** `Issued credit note CN-...` and the invoice marked credited.
- **Check:** `ledger.csv` shows both, which is the file their accountant wants.

## Recap
Books once, company details, clients, draft, check the preview, issue (theirs), verify. Mistakes get a credit note.
