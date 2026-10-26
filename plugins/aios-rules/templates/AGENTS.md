# {{BUSINESS}}: rules for every agent

Claude Code, Codex and Cursor all read this file. Keep it under 150 lines.
Put a step-by-step procedure in a skill, and a rule for one folder in `.claude/rules/`.

## Who this is for
- {{OWNER}} runs {{BUSINESS}}. {{ONE_LINE_WHAT_THE_BUSINESS_DOES}}
- Customers: {{WHO_BUYS}}.
- Write in British English, in plain words. No emojis in anything a customer reads.

## The folders
One line per folder: what goes in it. File new work in the right folder first time.

| Folder | What goes in it |
|---|---|
| `00_inbox/` | Anything not filed yet: downloads, voice notes, rough ideas. Empty it weekly. |
| `10_clients/` | One folder per client, named `client-name/`. Notes, proposals and delivery work. |
| `20_offers/` | What you sell: packages, prices, the proposal template. |
| `30_finance/` | Invoices, receipts and contracts. Never bank logins or card numbers. |
| `40_content/` | Posts, scripts, newsletters and their images. |
| `50_projects/` | Internal builds, tools and experiments. |
| `80_aios/` | This AIOS itself: audits, decisions, prompts that worked. |
| `90_archive/` | Finished work you keep but no longer change. |

## Naming
- Dates first: `2026-10-26_acme-proposal_v1.md`.
- Version finished files `_v1`, `_v2`. Never overwrite a version someone has seen.

## Rules that never break
- No passwords, API keys or tokens in this folder. Keys live in the harness settings or the system keychain.
- Ask before you delete, move or rename anything you did not create in this session.
- Ask before you send an email, post, payment or anything else that leaves this machine.
- If you are unsure which folder a file belongs in, put it in `00_inbox/` and say so.

## How to work
- Before you start a job, say the check you will run to prove it is done. Run it before you say done.
- If the check fails, fix that one thing and run it again. Report what failed if you cannot fix it.
- One session, no sub-agents, unless I ask for them.
- Keep answers short: the result first, then the one thing I need to decide.

## Checks this folder can run
- Rules budget: `aios-rules check` (lines and approximate tokens of everything always loaded).
- {{ADD_YOUR_OWN_CHECK_HERE, for example: the build passes, the totals match the sheet}}

## Gotchas
Add a line here only when an agent gets something wrong twice. Delete it when the cause is fixed.
- {{EXAMPLE: the client list lives in 10_clients/README.md, not in a spreadsheet}}
