# Prompts for shelf-invoices

Paste one into Claude Code (or Codex, or Cursor) once the pack is installed. Claude runs the `shelf-invoices`
command for you, shows you the PDF, and files nothing until you say yes.
To practise first, run `shelf-invoices sample ~/Invoices-practice` and add "Use my practice books in
~/Invoices-practice." to the prompt.

## 1. Set up your invoices (once)

```text
Set up my invoices with shelf-invoices. Make my books folder at ~/Documents/Invoices, then ask me for my company details one at a time from my own paperwork and fill in company.json. Don't guess anything. When we're done, run the company check and tell me what's still missing.
```

## 2. Make an invoice and show me the PDF

```text
Make an invoice to Contoso GmbH, Musterstraße 1, 10115 Berlin, Germany (VAT ID DE000000000, requester Jana Weber, PO PO-7781) for 3 days of workshop delivery on 20–22 October 2026 at EUR 1,200 a day, net 14 days, and show me the PDF.
```

## 3. Check it and file it

```text
Look at my latest invoice draft with shelf-invoices: check it is one page, the PO and service date are on it, the currency sign is right everywhere and the total adds up. Tell me what you checked. If it's all right, file it and tell me which file to send.
```
