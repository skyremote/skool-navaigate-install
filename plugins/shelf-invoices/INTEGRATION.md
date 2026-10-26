# shelf-invoices 2.0.1: integration notes for the chief of staff

2.0.1 replaces 2.0.0 (a ReportLab rebuild Daniel rejected on 26 October 2026). It is a port of the invoice skill
NavAIgate really uses, de-identified: the same template, the same generator logic and the same checks, with the
member's identity in `company.json`.

## What came from where

| Shipped file | Source | Licence | What changed |
|---|---|---|---|
| `assets/template_v1.docx` | `navaigate-invoice/assets/template_kg_v2.docx` (Daniel's private skill) | Daniel's own work, released here under the repo's MIT licence | Built by `scripts/make_clean_template.py`: all 37 variable runs became `{{placeholders}}` (company, address, contact and web lines, client block, PO, item row, totals, VAT row, bank, tax, payment terms, closing, signatory, footer line, legal footer). The logo is a neutral "YOUR LOGO" PNG drawn for this pack. `docProps/thumbnail.jpeg` and `customXml/` were removed with their references in `[Content_Types].xml`, `_rels/.rels` and `word/_rels/document.xml.rels`. Title, author and description in `docProps/core.xml` are empty. Layout, fonts, colours and spacing are untouched. |
| `scripts/generate_invoice.py` | `navaigate-invoice/scripts/generate_invoice_kg.py` | as above | Same method (open the .docx zip, replace run text with lxml, clone the item row per line, write a new zip, convert with LibreOffice). Now fills `{{fields}}` from `company.json` + `spec.json` instead of matching one past invoice's strings; swaps the logo at render time keeping its proportions; VAT modes renamed and generalised (`standard` at the member's rate, `reverse_charge_eu`, `outside_scope`, `outside_eu`, `domestic_reverse_charge`, `not_registered`) with neutral English wording from settings; finds LibreOffice with `shutil.which("soffice")` plus the macOS app path and says "install LibreOffice for the PDF" when absent; checks unfilled fields, stray currency signs and page count. |
| `bin/shelf-invoices` | new | MIT | The command: `init`, `company check/show`, `next-number`, `make`, `file`, `sample`. Encodes the real skill's rules: never overwrite (drafts `_vN`), number = highest used + 1, refuse an already-filed number, file finals under `<year>/<month>/`. |
| `scripts/make_clean_template.py` | new | MIT | Repeatable clean-up. Replaces runs by position, checks the fixed labels as anchors, holds no source text of its own, and refuses to write if any word from the replaced runs survives in any part. Run it on the private template outside the repo; only its output is committed. |
| `skills/shelf-invoices/SKILL.md` | the real SKILL.md's workflow | as above | Kept: ask for the variable details, currency follows the PO, VAT treatment by the client's legal entity, quote the PO and service date, check the highest number, never overwrite, render and look at the PDF (one page, logo, no stray currency sign), member approves, file by year/month. |
| `assets/placeholder_logo.png`, `assets/sample/acme-studio-logo.png` | drawn for this pack with Pillow and Poppins | MIT (Poppins: SIL OFL, used only to draw the PNG) | Neutral and fictional. |
| `assets/sample/` | new | MIT | Fictional Acme Studio Ltd: every ID and bank detail marked SAMPLE (`GB000000000 (SAMPLE)`, `XX00 SAMPLE 0000 0000 00`), Ofcom drama-range phone number, `.example` domain. |

## Checked and not used: skyremote/invoice-builder

`skyremote/invoice-builder` (public, MIT, last updated 16 April 2026) is a skill that scaffolds other skills: it
asks for a branded .docx/.pptx, the locked elements and the placeholder strings, and writes a `SKILL.md`,
`scripts/generate.py` (from `templates/generate_script.py.template`) and `assets/template.docx`. Files read:
`README.md`, `SKILL.md`, `scripts/scaffold_skill.py`, `templates/*`. The real invoice skill does not call it,
import it or reference it (grep of the whole skill folder: no match). It shares the method (copy a branded
template, replace strings in the XML, re-zip), which this pack already has from the real generator. Nothing was
ported from it.

## Left out, and why

| Left out | Why |
|---|---|
| Every NavAIgate and client detail: company and register names and numbers, addresses, phone, email, bank, tax numbers, the managing-director line, client names, PO and supplier numbers, the invoice numbering series | Private and legal data. The template holds placeholders; the member's own `company.json` fills them. |
| German statutory wording in code (UStG paragraphs, "Leistungsdatum") | Country-specific. Neutral English defaults; the member's accountant's wording goes in `vat_wording`. |
| The supplier-portal submission step and the "Upload_Files" copy | Specific to one client's accounts-payable process. The SKILL says sending is the member's step. |
| The real SKILL.md's history section and the retired pin-logo template and script | History, and retired. |
| The real filing path (an accountant-named folder) | Replaced by `<books>/<year>/<month>/`. |
| Credit notes, a ledger and e-invoicing formats (2.0.0 features) | Not part of the real skill. Left out to keep the port faithful. |

## Shared-file changes needed (I did not edit these)

1. **`.claude-plugin/marketplace.json`**: replace the `shelf-invoices` entry with `plugins/shelf-invoices/MARKETPLACE_ENTRY.json` (version 2.0.1).
2. **`README.md` and `ROADMAP.md`**: module 12 line: "shelf-invoices: the invoice NavAIgate sends, in our house
   design, from your own company settings: numbered, checked as a PDF, filed."
3. **Tests in CI**: `python3 -m unittest discover -s tests/shelf-invoices` (needs `lxml`; the PDF test needs
   LibreOffice and skips without it).
4. **Installer**: nothing new. `bin/shelf-invoices` is linked like other packs' `bin/` commands.

## Kept out of the repo

Course content and build evidence live on the NAS (`150_Navbot_Classroom/aios-2/`), never in Git:
`lessons_v2/12-shelf-invoices/`, `tutorials_v2/12-shelf-invoices/`, `build-proof/shelf-invoices/`. The source
template and every real invoice stay in Daniel's private skill.
