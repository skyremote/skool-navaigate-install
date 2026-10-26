# Tour: module 12, the shelf: invoices

`/aios learn 12 invoices` follows these steps in the member's own folder, one at a time.
Run each command for the member, or have them type it. Show the real output, then check it before the next step.
Never file an invoice for the member without their yes. If a check fails, stop, fix that one thing, check again.

## Step 1: Find the command
- **Do:** check that the pack's command runs.
- **Command:** `shelf-invoices --version` (Claude Code: `"${CLAUDE_PLUGIN_ROOT}/bin/shelf-invoices" --version`).
- **They should see:** `shelf-invoices 2.0.1`.
- **Check:** exit code 0. If the command is missing, run `export PATH="$HOME/.local/bin:$PATH"` (Codex and Cursor),
  or `/aios install shelf-invoices`, then `/reload-plugins`.

## Step 2: Check the tools
- **Do:** confirm lxml (fills the template) and LibreOffice (makes the PDF).
- **Command:** `python3 -c "import lxml; print('ok')"` and `soffice --version`
- **They should see:** `ok` and a LibreOffice version.
- **Check:** if lxml is missing, `python3 -m pip install --user lxml` (Homebrew Python: a virtual environment, see the
  README). If LibreOffice is missing, install it from libreoffice.org; until then only the .docx is made.

## Step 3: Practise on sample books
- **Do:** make books for the fictional Acme Studio Ltd. They are not the member's default.
- **Command:** `shelf-invoices sample ~/Invoices-practice`
- **They should see:** `Sample books for the fictional Acme Studio Ltd` and `ACME-001, an earlier invoice already filed`.
- **Check:** `shelf-invoices next-number --books ~/Invoices-practice` prints `ACME-002  (highest used: ACME-001)`.

## Step 4: Make a practice invoice and look at it
- **Do:** make the Contoso workshop invoice, then open the PDF together.
- **Command:** `shelf-invoices make ~/Invoices-practice/examples/contoso-workshop.json --books ~/Invoices-practice`
- **They should see:** `Invoice ACME-002`, `total €3,600.00`, the docx, pdf and preview paths, `(1 page)` and
  `Checks: every field filled, no other currency's sign, one page.`
- **Check:** in the PDF: the Acme logo top left, Contoso's VAT ID under its address, PO-7781, the service date,
  € everywhere, the reverse-charge line, the SAMPLE bank details.

## Step 5: File the practice invoice
- **Do:** file it, as the member would after approving it.
- **Command:** `shelf-invoices file ACME-002 --books ~/Invoices-practice`
- **They should see:** `Filed ACME-002 ... in .../2026/10` and the file to send.
- **Check:** running the same command again says `already filed`. A filed invoice is never changed.

## Step 6: Make their own books
- **Do:** create the real books folder in a place they back up.
- **Command:** `shelf-invoices init ~/Documents/Invoices`
- **They should see:** `Wrote .../company.json with empty fields.` and `This is now your default books folder.`
- **Check:** `ls ~/Documents/Invoices` shows `company.json` and `drafts`.

## Step 7: Their company details
- **Do:** fill `company.json` with them, one field at a time, from their own paperwork. Never guess a VAT ID,
  company number or bank detail. Their logo goes in as `logo.png`.
- **Command:** `shelf-invoices company check`
- **They should see:** `Company details complete.`
- **Check:** if they are unsure what their country requires on an invoice, or which VAT wording to use, they ask
  their accountant and put the wording in `vat_wording`.

## Step 8: Their first real invoice
- **Do:** ask Claude in plain words (prompt 2 in `prompts.md`), with their client's real details.
- **Command:** `shelf-invoices next-number`, then Claude writes the spec and runs `shelf-invoices make <spec>`.
- **They should see:** the number, the totals and the PDF.
- **Check:** they read every line of the PDF. Changes go into the spec and a new `make` (`_v2`).

## Step 9: The member approves and files
- **Do:** wait until they say yes.
- **Command:** `shelf-invoices file <number>`
- **They should see:** the filed path under `<year>/<month>/`.
- **Check:** that PDF is the one they send.

## Recap
Books once, company details, check. Then for each invoice: next number, spec, make, look at the PDF, approve, file.
