"""Sandbox steps for tools-inbox, run by tests/tools-packs/sandbox_proof.py tools-inbox."""
import json


def run(r, home, work):
    practice = work / 'Inbox-practice'
    r.run(['tools-inbox', '--version'])
    r.run(['tools-inbox', 'doctor'], expect=2, note='A new member has no Composio key; the guard is on anyway.')
    r.run(['tools-inbox', 'guard'], stdin=json.dumps({'tool_name': 'mcp__composio-gmail__GMAIL_SEND_EMAIL'}),
          note='The never-send guard denies a sending tool.')
    r.run(['tools-inbox', 'guard'], stdin=json.dumps({'tool_name': 'mcp__composio-gmail__GMAIL_CREATE_EMAIL_DRAFT'}),
          note='Drafts pass: no output means allowed.')
    r.run(['tools-inbox', 'sample', practice])
    r.run(['tools-inbox', 'check', practice / 'inbox-brief_practice_v1.md'])
    r.run(['tools-inbox', 'new', practice / 'inbox-brief_v2.md', '--date', '2026-10-26'])
    r.run(['tools-inbox', 'check', practice / 'inbox-brief_v2.md'], expect=1, note='An unfilled brief fails.')
    r.run(['tools-inbox', 'remind', '--subject', 'Invoices day', '--body', 'Send the invoices'], expect=1,
          note='A reminder needs --yes.')
    r.run(['tools-inbox', 'remind', '--subject', 'Invoices day', '--body', 'Send the invoices', '--yes'], expect=2,
          note='With --yes but no key, it says how to add the member\'s own Composio key.')
    r.run(['tools-inbox', 'schedule', '--cron', '0 8 * * 1', '--subject', 'Invoices day', '--body', 'Send the invoices'])
    r.run(['cat', home / '.cursor/hooks.json'], note='Cursor gets the guard as a hook.')
    r.run(['grep', '-A6', 'tools-inbox', home / '.codex/AGENTS.md'], note='Codex gets the never-send rule as written guidance.')
