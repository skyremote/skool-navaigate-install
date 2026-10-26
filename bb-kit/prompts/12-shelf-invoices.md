# Module 12 · The shelf: invoices: prompts

Paste one prompt at a time into a new Claude chat in bb, opened on your AIOS folder. Run them in order. If a prompt has lines marked "edit", change them to your own details first. Each prompt sets something up, checks it, and shows you the result.

These prompts are instructions to Claude. They also work in Claude Code in a terminal, opened in the same folder.

## Prompt 12i.1 · Practise on sample books

**What it does:** Makes practice books for the fictional Acme Studio, makes a practice invoice to Contoso from the example spec, checks the PDF with you, and files it. A filed invoice is never changed.

**How you know it worked:** The report shows invoice ACME-002, total €3,600.00 on one page, and the filed path. Filing it again says it is already filed.

~~~text
Set up the invoices pack from the shelf and practise on sample books. These are practice books for a fictional company, not mine.

Step 0, get the pack. These commands change Claude's own plugin folder in my home folder, outside this folder. I allow that for these commands only: if the sandbox blocks them, run them outside the sandbox. Run `claude plugin marketplace list`. If `navaigate-aios` is not listed, run `claude plugin marketplace add skyremote/skool-navaigate-install`. Then run `claude plugin install shelf-invoices@navaigate-aios` ("already installed" is fine; it also brings the start pack `aios`). Until I restart Claude, call the pack's command by its full path: `"$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/navaigate-aios/shelf-invoices/*/bin | tail -1)/shelf-invoices"`. Below, `shelf-invoices` means that full path.

1. Check the command: `shelf-invoices --version` should print `shelf-invoices 2.0.1` or later.
2. Check the tools: `python3 -c "import lxml; print('ok')"` and `soffice --version`. If lxml is missing, install it with `python3 -m pip install --user lxml` and check again. If LibreOffice is missing, tell me to install it from libreoffice.org: until then only the Word file is made.
3. Make the practice books in this folder: `shelf-invoices sample 30_finance/invoices-practice`. Then `shelf-invoices next-number --books 30_finance/invoices-practice` should print `ACME-002`.
4. Make the practice invoice from the example: `shelf-invoices make 30_finance/invoices-practice/examples/contoso-workshop.json --books 30_finance/invoices-practice`. Show the number, the total, the file paths and the checks line.
5. Check the PDF with me in the report: the Acme logo, Contoso's VAT ID under its address, PO-7781, the service date, € everywhere, the reverse-charge line and the SAMPLE bank details. Say what you checked.
6. File it, as I would after approving it: `shelf-invoices file ACME-002 --books 30_finance/invoices-practice`. Then run the same command again: it should say it is already filed.

For this task only: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. If a step below must write outside this folder (for example to Claude's settings, `~/.local` or a folder the step names), I allow exactly that command: if the sandbox blocks it, run it outside the sandbox. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m12-invoices-practice_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m12-invoices-practice_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~

## Prompt 12i.2 · Set up your own invoice books

**What it does:** Creates your real books folder and fills in your company details from your own lines. It leaves out anything you did not give, such as a VAT number or bank details, and lists what is still missing. It makes and files nothing.

**How you know it worked:** `shelf-invoices company check` shows what is complete and names each missing detail. No invoice is made or filed.

~~~text
My company details (edit these lines before you send; leave a line empty if you do not want to give it now):
- Company name: Acme Studio Ltd
- Address: 1 Mill Lane, Leeds, LS1 4AB, United Kingdom
- VAT registered: no
- Invoice number prefix: ACME
- Currency: GBP
- Bank IBAN:

Set up my own invoice books with the shelf invoices pack. If the pack is not set up yet, run prompt 12i.1 first.

Step 0, get the pack. These commands change Claude's own plugin folder in my home folder, outside this folder. I allow that for these commands only: if the sandbox blocks them, run them outside the sandbox. Run `claude plugin marketplace list`. If `navaigate-aios` is not listed, run `claude plugin marketplace add skyremote/skool-navaigate-install`. Then run `claude plugin install shelf-invoices@navaigate-aios` ("already installed" is fine; it also brings the start pack `aios`). Until I restart Claude, call the pack's command by its full path: `"$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/navaigate-aios/shelf-invoices/*/bin | tail -1)/shelf-invoices"`. Below, `shelf-invoices` means that full path.

1. Create my books: `shelf-invoices init 30_finance/invoices`. It writes `company.json` with empty fields and makes this my default books folder.
2. Open `30_finance/invoices/company.json` and fill in only the details I gave above, in the fields that match them. Never guess a VAT number, an address, a company number or a bank detail. Leave every field I did not give empty.
3. Run `shelf-invoices company check` and show me what is complete and what is missing.
4. Do not make or file an invoice. Tell me the one thing I do next: give you the missing details from my own paperwork, then ask for my first invoice in plain words, for example "Make an invoice to <client> for <work> at <price> and show me the PDF".
5. Tell me that a filed invoice is never changed: a mistake gets a new invoice, and my accountant says which wording I need.

For this task only: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. If a step below must write outside this folder (for example to Claude's settings, `~/.local` or a folder the step names), I allow exactly that command: if the sandbox blocks it, run it outside the sandbox. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m12-invoices-own_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m12-invoices-own_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~
