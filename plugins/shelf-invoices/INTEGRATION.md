# shelf-invoices: integration notes for the chief of staff

## Where the pack came from, and what it ships

| Source | Owner and licence | What this pack took |
|---|---|---|
| `navaigate-invoice` (Daniel's local skills) | Daniel, private, no licence file | The method only: currency per invoice, VAT treatment chosen by the client's situation (standard, reverse charge with the client's VAT ID, outside scope), always quote the PO and the service date, check the highest number before choosing the next, never overwrite, look at the PDF before sending, file finals by year. Rewritten from scratch. |
| ReportLab | BSD | Not bundled. pip install command given. |
| pypdf | BSD | Not bundled. Used only by `verify`. |

## Left out, and why

| Left out | Why |
|---|---|
| The KG house design: `template_kg_v2.docx`, the N logo, Poppins, the KG legal footer | NavAIgate brand and Daniel's German company template. The brief says leave it out. |
| Every NavAIgate detail: the company names, register numbers, addresses, phone, email, bank, VAT and tax numbers | Daniel's private and legal details. The pack ships no company at all; the member fills in theirs. |
| The Autodesk supplier ID, PO rules, AP portal steps and the `NAVAI-ADSK-NNN` numbering | A client relationship, private. |
| The retired pin-logo template and script | Retired, and NavAIgate-branded. |
| German-specific rules (§ 3a UStG wording, Leistungsdatum label, the "Tax Lady" filing path) | Specific to Daniel's company and accountant. Members choose a VAT mode; the note wording is generic and editable in their own `footer_note`/`notes`. |
| DOCX output | The member pack makes PDF only, which is what clients and accountants want. |
| Multi-page invoices | Refused with a clear message instead. Planned for a later version. |
| E-invoicing formats (ZUGFeRD, XRechnung, Peppol UBL) | Country-specific and need validation tooling. Planned for a later version. |

## Shared-file changes needed (I did not edit these)

1. **`.claude-plugin/marketplace.json`**: add the object in `plugins/shelf-invoices/MARKETPLACE_ENTRY.json`.
2. **`scripts/install_pack.py`**: covered by `plugins/shelf-video/install_pack.diff`. Apply it once for all three.
3. **`README.md` and `ROADMAP.md`**: list `shelf-invoices` under module 12: "Invoices and credit notes as PDF from
   your own company details, numbered, filed and verified."
4. **Tests in CI**: `python3 -m unittest discover -s tests/shelf-invoices` (21 tests; the flow tests need ReportLab
   and skip without it).

## Known limits

- The ledger lock uses `fcntl`, so the pack runs on macOS and Linux. On Windows, use WSL.
- Rules about what an invoice must show differ by country. The pack covers the usual fields and says it is not
  tax advice.

## Kept out of the repo (Daniel's ruling, 26 October 2026)

The repo holds the pack, its README and install steps, tests and evals. Course content and build evidence live
in the classroom folder on the NAS (local mirror `~/NAS_Local/150_Navbot_Classroom/aios-2/`), never in Git:

| Kept out | Where it lives |
|---|---|
| `lessons/` (lesson Markdown and paste-ready HTML) | `lessons_v2/12-shelf-invoices/` |
| `video/` (tutorial scripts, shot lists, SRTs, clips) | `tutorials_v2/12-shelf-invoices/`; films in the NavMotion project's `deliver/` |
| `plugins/*/proof/` (sandbox install proof, eval results) | `build-proof/shelf-invoices/` |
