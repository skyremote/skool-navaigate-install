"""Sandbox steps for shelf-invoices, run by tests/shelf-video/sandbox_proof.py shelf-invoices."""


def run(r, home, work):
    work.mkdir(parents=True, exist_ok=True)
    practice = work / 'Invoices-practice'
    mine = work / 'Invoices'
    r.run(['python3', '-m', 'pip', 'install', '--user', '--disable-pip-version-check', 'reportlab', 'pypdf'],
          note='The tools step from the README. Already present for this Python, so pip only confirms them.')
    r.run(['shelf-invoices', '--version'])
    r.run(['shelf-invoices', 'list'], expect=1, note='A new member has no books yet.')
    r.run(['shelf-invoices', 'sample', practice])
    r.run(['shelf-invoices', 'client', 'list', '--books', practice])
    r.run(['shelf-invoices', 'draft', '--books', practice, '--client', 'northwind', '--date', '2026-10-26',
           '--item', 'Booking page redesign | 1 | 2400', '--item', 'Menu photography, half day | 1 | 650',
           '--item', 'Hosting, October | 1 | 25 | 0', '--po', 'NW-0042', '--service-date', 'October 2026'])
    r.run(['shelf-invoices', 'issue', 'northwind_draft_v1', '--books', practice], expect=1,
          note='Issuing refuses without the member\'s --yes.')
    r.run(['shelf-invoices', 'issue', 'northwind_draft_v1', '--books', practice, '--yes'],
          note='The sandbox member has checked the draft preview and issues it.')
    r.run(['shelf-invoices', 'verify', 'ACME-2026-0001', '--books', practice])
    r.run(['shelf-invoices', 'draft', '--books', practice, '--client', 'contoso-de', '--date', '2026-10-26',
           '--item', 'Workshop, one day | 1 | 1800'])
    r.run(['shelf-invoices', 'issue', 'contoso-de_draft_v1', '--books', practice, '--yes'])
    r.run(['shelf-invoices', 'verify', 'ACME-2026-0002', '--books', practice])
    r.run(['shelf-invoices', 'credit', 'ACME-2026-0002', '--books', practice, '--reason', 'Workshop moved to November',
           '--date', '2026-10-27', '--yes'])
    r.run(['shelf-invoices', 'list', '--books', practice])
    r.run(['cat', practice / 'ledger.csv'])
    r.run(['ls', '-go', practice / '2026'])
    r.run(['shelf-invoices', 'init', mine], note='Now the member\'s own books, which become the default.')
    r.run(['shelf-invoices', 'company', 'check'], expect=1, note='Empty company details are refused before any draft.')
    r.run(['shelf-invoices', 'draft', '--to-name', 'Test', '--item', 'X | 1 | 1'], expect=1)
