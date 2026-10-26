# shelf-invoices (AIOS 2.0, module 12: the shelf)

The invoice NavAIgate sends, with your company in place of ours. Same house design (logo slot, Poppins, the
INVOICE kicker and big title, Bill to and Invoice details, the scope table, the total band, the VAT, bank and tax
rows, the legal footer), same workflow, same checks:

- **Your identity in settings.** `company.json` in your own books folder holds your name, address, VAT ID, bank
  details, legal footer and logo. The template ships with `{{placeholders}}` only.
- **Numbered from your books.** The next number is the highest one already used + 1, with your prefix.
- **Never overwritten.** Drafts are `_v1`, `_v2`. A filed invoice is never changed.
- **Checked.** Every field filled, no other currency's sign, one page, then you look at the PDF.
- **Filed by year and month.** `<books>/2026/10/ACME-002.pdf` is the file you send.
- **Local.** No account, no API, no upload.

## Install

Install the start plugin `aios` first.

Claude Code: type `/aios install shelf-invoices` (it runs `aios-guide --harness claude install shelf-invoices`),
then `/reload-plugins`. Or install it directly:
```
/plugin install shelf-invoices@navaigate-aios
```

Codex and Cursor, from your checkout of this repository:
```
./install.sh shelf-invoices
./install.sh shelf-invoices --check
```

Then the tools, once:
- `python3 -m pip install --user lxml` (on Homebrew Python, use a virtual environment: `python3 -m venv ~/.venvs/aios && ~/.venvs/aios/bin/python -m pip install lxml`).
- LibreOffice for the PDF: https://www.libreoffice.org (macOS: `brew install --cask libreoffice`). Without it you
  still get the .docx.
- The fonts Poppins and Fraunces from https://fonts.google.com (free, SIL Open Font Licence), so the PDF matches
  the design.

Works on macOS and Linux with Python 3.9+ (on Windows, use WSL).

## Use

```
shelf-invoices sample ~/Invoices-practice               # practice books for the fictional Acme Studio Ltd
shelf-invoices next-number --books ~/Invoices-practice  # ACME-002  (highest used: ACME-001)
shelf-invoices make ~/Invoices-practice/examples/contoso-workshop.json --books ~/Invoices-practice
shelf-invoices file ACME-002 --books ~/Invoices-practice

shelf-invoices init ~/Documents/Invoices                # your own books, once
shelf-invoices company check                            # until it says: Company details complete.
```

Or just ask Claude: see [prompts.md](prompts.md). Settings: [settings](skills/shelf-invoices/references/settings.md).
One invoice: [spec](skills/shelf-invoices/references/spec.md).

The plugin setting `books_folder` (optional) points Claude Code at your books folder; otherwise the folder `init`
remembers is used.

This pack is not tax advice. What an invoice must show, and which VAT treatment applies, differ by country:
check with your accountant and put their wording in `vat_wording`.

## Licence

MIT. Dependencies you install yourself: lxml (BSD), LibreOffice (MPL 2.0), Poppins and Fraunces (SIL OFL 1.1).
