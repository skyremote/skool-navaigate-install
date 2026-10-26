# Module 12 · The shelf: invoices: prompts

Paste one prompt at a time into a new Claude chat in bb, opened on your AIOS folder. Run them in order. If a prompt has lines marked "edit", change them to your own details first. Each prompt sets something up, checks it, and shows you the result.

These prompts are instructions to Claude. They also work in Claude Code in a terminal, opened in the same folder.

## Prompt 12i.1 · Practise on sample books

**What it does:** Makes practice books for the fictional Acme Studio, drafts and issues a practice invoice, verifies the PDF, and cancels it with a credit note.

**How you know it worked:** `shelf-invoices verify ACME-2026-0001` says PASS, and the ledger shows both the invoice and its credit note.

~~~text
Set up the invoices pack from the shelf and practise on sample books. These are practice books for a fictional company, not mine.

Step 0, get the pack. Run `claude plugin marketplace list`. If `navaigate-aios` is not listed, run `claude plugin marketplace add skyremote/skool-navaigate-install`. Then run `claude plugin install shelf-invoices@navaigate-aios` ("already installed" is fine; it also brings the start pack `aios`). Until I restart Claude, call the pack's command by its full path: `"$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/navaigate-aios/shelf-invoices/*/bin | tail -1)/shelf-invoices"`. Below, `shelf-invoices` means that full path.

1. Check the tools: `python3 -c "import reportlab, pypdf; print('ok')"`. If it fails, run `python3 -m pip install --user reportlab pypdf` and check again.
2. Make the practice books in this folder: `shelf-invoices sample 30_finance/invoices-practice`. Then `shelf-invoices client list --books 30_finance/invoices-practice` should show `northwind` and `contoso-de`.
3. Draft a practice invoice: `shelf-invoices draft --books 30_finance/invoices-practice --client northwind --item "Booking page redesign | 1 | 2400"`. Show the totals and the preview path.
4. Issue it (practice books only): `shelf-invoices issue northwind_draft_v1 --books 30_finance/invoices-practice --yes`. Show the number it gets.
5. Verify it: `shelf-invoices verify <the number> --books 30_finance/invoices-practice`. It must say PASS.
6. Show the right way to fix a mistake: `shelf-invoices credit <the number> --books 30_finance/invoices-practice --reason "Practice: wrong amount" --yes`. Then show the last lines of `ledger.csv` in the practice books.

Ground rules: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m12-invoices-practice_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m12-invoices-practice_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~

## Prompt 12i.2 · Set up your own invoice books

**What it does:** Creates your real books folder and fills in your company details from your own lines. It leaves out anything you did not give, such as a VAT number or bank details, and lists what is still missing. It issues nothing.

**How you know it worked:** `shelf-invoices company check` shows what is complete and names each missing detail. No invoice is issued.

~~~text
My company details (edit these lines before you send; leave a line empty if you do not want to give it now):
- Company name: Acme Studio Ltd
- Address: 1 Mill Lane; Leeds; LS1 4AB; United Kingdom
- VAT registered: no
- Invoice number prefix: ACME
- Currency: GBP
- Bank IBAN:

Set up my own invoice books with the shelf invoices pack.

Step 0, get the pack. Run `claude plugin marketplace list`. If `navaigate-aios` is not listed, run `claude plugin marketplace add skyremote/skool-navaigate-install`. Then run `claude plugin install shelf-invoices@navaigate-aios` ("already installed" is fine; it also brings the start pack `aios`). Until I restart Claude, call the pack's command by its full path: `"$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/navaigate-aios/shelf-invoices/*/bin | tail -1)/shelf-invoices"`. Below, `shelf-invoices` means that full path.

1. Create my books: `shelf-invoices init 30_finance/invoices`. Show that `company.json`, `clients.json` and `ledger.json` exist.
2. Set each detail I gave above with `shelf-invoices company set key=value` (for example `name=...`, `address=...`, `vat_registered=false`, `prefix=...`, `currency=...`). Never guess a VAT number, an address or a bank detail. Skip every line I left empty.
3. Run `shelf-invoices company check` and show me what is complete and what is missing.
4. Do not draft or issue an invoice. Give me the two commands I run next: one to add my first client (`shelf-invoices client add --name "..." --address "..."`) and one to draft an invoice.
5. Tell me that an issued invoice is never edited or deleted; a credit note cancels it.

Ground rules: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m12-invoices-own_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m12-invoices-own_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~
