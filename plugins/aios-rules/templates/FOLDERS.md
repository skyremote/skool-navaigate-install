# Folder map template

Copy this map, rename the folders to fit your business, then copy the table into AGENTS.md.
Numbers keep the order fixed on every machine. Leave gaps so you can add a folder later.

| Folder | What goes in it | Path-scoped rule? |
|---|---|---|
| `00_inbox/` | Anything not filed yet. Empty it weekly. | No |
| `10_clients/` | One folder per client: notes, proposals, delivery. | Yes: `.claude/rules/clients.md` |
| `20_offers/` | Packages, prices, the proposal template. | No |
| `30_finance/` | Invoices, receipts, contracts. No logins or card numbers. | Yes: `.claude/rules/finance.md` |
| `40_content/` | Posts, scripts, newsletters and their images. | Yes: `.claude/rules/content.md` |
| `50_projects/` | Internal builds, tools and experiments. | No |
| `80_aios/` | The AIOS itself: audits, decisions, prompts that worked. | No |
| `90_archive/` | Finished work you keep but no longer change. | No |

## Three questions before you add a folder
1. Will more than five files go in it this month? If not, use an existing folder.
2. Does it need its own rule? If yes, add one file in `.claude/rules/` with `paths:` for that folder.
3. Can you say what goes in it in one line? If not, it is two folders, or none.

## Example: Acme Studio (fictional)
Acme Studio is a two-person design studio. It renamed `20_offers/` to `20_packages/`, added
`60_templates/` for brand kits, and kept the rest. Its AGENTS.md folder table is nine lines long.
