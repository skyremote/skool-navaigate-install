"""shelf-invoices command line: draft, issue (numbers it), credit, list, verify."""
import argparse
import datetime
import json
import sys
from pathlib import Path

from . import books as bk
from . import money, pdf, sample

VERSION = '2.0.0'


class Stop(ValueError):
    pass


def client_record(books, a):
    if a.client:
        saved = bk.clients(books)
        key = bk.slug(a.client)
        if key not in saved:
            raise Stop('No saved client "%s". Saved: %s. Add one with: shelf-invoices client add' % (
                a.client, ', '.join(sorted(saved)) or 'none'))
        return dict(saved[key], key=key)
    if not a.to_name:
        raise Stop('Say who the invoice is for: --client <saved name>, or --to-name and --to-address.')
    return {'key': bk.slug(a.to_name), 'name': a.to_name, 'address': [x.strip() for x in (a.to_address or '').split(';') if x.strip()],
            'vat_id': a.to_vat_id or '', 'email': '', 'country': ''}


def cmd_init(a):
    books = bk.init(a.folder, make_default=not a.not_default)
    print('Books folder: %s%s' % (books, '' if a.not_default else ' (now your default)'))
    print('Next: fill in your company details, for example:')
    print('  shelf-invoices company set name="Acme Studio Ltd"')
    print('  shelf-invoices company set address="1 Example Street;Bristol;BS1 1AA;United Kingdom"')
    print('  shelf-invoices company set vat_id=GB123456789')
    print('Then: shelf-invoices company check')


def cmd_company(a):
    books = bk.resolve_books(a.books)
    if a.action == 'set':
        if not a.pair or '=' not in a.pair:
            raise Stop('Use: shelf-invoices company set name="Acme Studio Ltd"')
        key, value = a.pair.split('=', 1)
        bk.set_company(books, key.strip(), value.strip())
    c = bk.company(books)
    print(json.dumps(c, indent=2))
    missing = bk.check_company(c)
    if a.action == 'check' or missing:
        print('Missing for a complete invoice: ' + ', '.join(missing) if missing else 'Company details complete.')
    return 1 if (a.action == 'check' and missing) else 0


def cmd_client(a):
    books = bk.resolve_books(a.books)
    if a.action == 'add':
        if not a.name:
            raise Stop('Use: shelf-invoices client add --name "Northwind Bakery" --address "line;line" [--vat-id ...]')
        key = bk.add_client(books, a.key or a.name, {
            'name': a.name, 'address': [x.strip() for x in (a.address or '').split(';') if x.strip()],
            'vat_id': a.vat_id or '', 'email': a.email or '', 'country': a.country or '',
            'currency': a.currency or '', 'vat_mode': a.vat_mode or ''})
        print('Saved client "%s"' % key)
    for key, c in sorted(bk.clients(books).items()):
        print('%-24s %s%s' % (key, c['name'], ('  (%s ID %s)' % ('VAT', c['vat_id'])) if c.get('vat_id') else ''))


def build_doc(books, c, a, kind='invoice'):
    client = client_record(books, a)
    date = bk.parse_date(a.date) if a.date else bk.today()
    terms = a.due_days if a.due_days is not None else c['payment_terms_days']
    mode = a.vat_mode or client.get('vat_mode') or ('standard' if c['vat_registered'] else 'not-registered')
    if not c['vat_registered']:
        mode = 'not-registered'
    if mode == 'reverse-charge' and not client.get('vat_id'):
        raise Stop('Reverse charge needs the client\'s VAT ID on the invoice. Add --to-vat-id or save it on the client.')
    if not a.item:
        raise Stop('Add at least one line: --item "Website design | 1 | 2400"')
    items = [money.parse_item(i, c['vat_rate']) for i in a.item]
    currency = (a.currency or client.get('currency') or c['currency']).upper()
    doc = {'kind': kind, 'date': date.isoformat(), 'due': (date + datetime.timedelta(days=terms)).isoformat(),
           'currency': currency, 'client': {k: client.get(k, '') for k in ('key', 'name', 'address', 'vat_id', 'email')},
           'items': items, 'vat_mode': mode, 'vat_note': money.VAT_MODES[mode], 'po': a.po or '',
           'service_date': a.service_date or '', 'notes': a.notes or ''}
    doc['totals'] = money.totals(items, mode)
    return doc


def cmd_draft(a):
    books = bk.resolve_books(a.books)
    c = bk.company(books)
    missing = bk.check_company(c)
    if missing:
        raise Stop('Finish your company details first: ' + ', '.join(missing) + '. Run: shelf-invoices company check')
    doc = build_doc(books, c, a)
    folder = books / 'drafts'
    folder.mkdir(exist_ok=True)
    n = 1
    while (folder / ('%s_draft_v%d.json' % (doc['client']['key'], n))).exists():
        n += 1
    stem = '%s_draft_v%d' % (doc['client']['key'], n)
    bk.private_write(folder / (stem + '.json'), json.dumps(doc, indent=2) + '\n')
    pdf.render(books, c, doc, folder / (stem + '.pdf'), draft=True)
    t = doc['totals']
    print('Draft %s for %s: net %s, %s %s, total %s (%s)' % (
        stem, doc['client']['name'], money.fmt(t['net'], doc['currency']), c['tax_label'],
        money.fmt(t['vat'], doc['currency']), money.fmt(t['total'], doc['currency']), doc['vat_mode']))
    print('Preview: %s' % (folder / (stem + '.pdf')))
    print('Nothing is numbered yet. Check the preview, then the member issues it:')
    print('  shelf-invoices issue %s --yes' % stem)


def filed_path(books, doc, number):
    year = doc['date'][:4]
    return books / year / ('%s_%s.pdf' % (number, doc['client']['key']))


def issue_doc(books, c, doc, kind, extra=None):
    with bk.ledger_lock(books):
        number, seq = bk.next_number(books, c, kind, bk.parse_date(doc['date']))
        doc = dict(doc, number=number, issued_at=datetime.datetime.now().isoformat(timespec='seconds'), **(extra or {}))
        target = filed_path(books, doc, number)
        if target.exists():
            raise Stop('%s already exists. The ledger and the folder disagree; check them before issuing.' % target)
        target.parent.mkdir(parents=True, exist_ok=True)
        pdf.render(books, c, doc, target)
        bk.private_write(target.with_suffix('.json'), json.dumps(doc, indent=2) + '\n')
        t = doc['totals']
        bk.record(books, {'number': number, 'seq': seq, 'year': int(doc['date'][:4]), 'kind': kind, 'date': doc['date'],
                          'due': doc['due'] if kind == 'invoice' else '', 'client': doc['client']['name'],
                          'currency': doc['currency'], 'net': t['net'], 'vat': t['vat'], 'total': t['total'],
                          'vat_mode': doc['vat_mode'], 'status': 'issued', 'credits': doc.get('credits', ''),
                          'file': str(target.relative_to(books)), 'sha256': bk.sha(target)})
    return number, target, doc


def cmd_issue(a):
    books = bk.resolve_books(a.books)
    if not a.yes:
        raise Stop('Issuing gives the invoice its permanent number. The member types --yes after checking the draft preview. '
                   'An agent must not issue on their behalf.')
    c = bk.company(books)
    draft = books / 'drafts' / (a.draft if a.draft.endswith('.json') else a.draft + '.json')
    if not draft.exists():
        raise Stop('No draft %s. List drafts with: ls "%s"' % (draft.name, books / 'drafts'))
    doc = json.loads(draft.read_text())
    if doc.get('issued_as'):
        raise Stop('This draft was already issued as %s. Make a new draft for a new invoice.' % doc['issued_as'])
    number, target, doc = issue_doc(books, c, doc, 'invoice')
    bk.private_write(draft, json.dumps(dict(json.loads(draft.read_text()), issued_as=number), indent=2) + '\n')
    print('Issued %s: %s, total %s, due %s' % (number, doc['client']['name'], money.fmt(doc['totals']['total'], doc['currency']), doc['due']))
    print('Filed: %s' % target)
    print('Next: shelf-invoices verify %s' % number)


def cmd_credit(a):
    books = bk.resolve_books(a.books)
    if not a.yes:
        raise Stop('A credit note is permanent too. The member types --yes after deciding to cancel or reduce the invoice.')
    c = bk.company(books)
    original = bk.find(books, a.number)
    if original['kind'] != 'invoice':
        raise Stop('%s is not an invoice.' % a.number)
    if original['status'] == 'credited':
        raise Stop('%s has already been credited in full.' % a.number)
    src = json.loads((books / original['file']).with_suffix('.json').read_text())
    items = [dict(i, quantity=str(-money.dec(i['quantity']))) for i in src['items']]
    doc = dict(src, kind='credit', items=items, date=(bk.parse_date(a.date) if a.date else bk.today()).isoformat(),
               notes='Credit note for invoice %s. Reason: %s' % (a.number, a.reason))
    doc.pop('number', None)
    doc['totals'] = money.totals(items, doc['vat_mode'])
    number, target, doc = issue_doc(books, c, doc, 'credit', {'credits': a.number})
    bk.mark(books, a.number, status='credited', credited_by=number)
    print('Issued credit note %s for %s (%s). %s is now marked credited.' % (
        number, doc['client']['name'], money.fmt(doc['totals']['total'], doc['currency']), a.number))
    print('Filed: %s' % target)


def cmd_list(a):
    books = bk.resolve_books(a.books)
    docs = bk.ledger(books)['documents']
    if a.year:
        docs = [d for d in docs if d['year'] == a.year]
    if not docs:
        print('No invoices issued yet.')
    for d in docs:
        print('%-18s %-7s %s  %-28s %12s  %s' % (d['number'], d['kind'], d['date'], d['client'][:28],
                                                money.fmt(d['total'], d['currency']), d['status']))
    print('Ledger for your accountant: %s' % (books / 'ledger.csv'))


def cmd_verify(a):
    books = bk.resolve_books(a.books)
    entry = bk.find(books, a.number)
    target = books / entry['file']
    problems = []
    if not target.exists():
        problems.append('The PDF is missing: %s' % target)
    else:
        if bk.sha(target) != entry['sha256']:
            problems.append('The PDF changed after it was issued. Issued documents must not be edited.')
        doc = json.loads(target.with_suffix('.json').read_text())
        again = money.totals(doc['items'], doc['vat_mode'])
        if again['total'] != entry['total'] or again['vat'] != entry['vat']:
            problems.append('The totals do not add up again: %s vs %s.' % (again['total'], entry['total']))
        text = pdf.text_of(target)
        if text is None:
            print('Note: install pypdf to check the PDF text (python3 -m pip install --user pypdf).')
        else:
            c = bk.company(books)
            flat = ' '.join(text.split())
            for label, needle in (('number', entry['number']), ('total', money.fmt(entry['total'], entry['currency'])),
                                  ('client', doc['client']['name']), ('your name', c['name'])):
                if needle not in flat:
                    problems.append('The PDF text is missing the %s: %s' % (label, needle))
            if c['vat_registered'] and c['vat_id'] and c['vat_id'] not in flat:
                problems.append('The PDF does not show your %s ID.' % c['tax_label'])
            if doc['vat_mode'] == 'reverse-charge' and doc['client'].get('vat_id') not in flat:
                problems.append('Reverse charge: the client\'s VAT ID is not on the PDF.')
    print(('PASS' if not problems else 'FAIL') + ': %s %s, %s, total %s, status %s' % (
        entry['kind'], entry['number'], entry['client'], money.fmt(entry['total'], entry['currency']), entry['status']))
    for p in problems:
        print('Problem: ' + p)
    return 1 if problems else 0


def cmd_sample(a):
    folder = sample.make(a.folder)
    print('Sample books for the fictional Acme Studio Ltd: %s' % folder)
    print('It is not your default. Use --books "%s" with each command, for example:' % folder)
    print('  shelf-invoices draft --books "%s" --client northwind --item "Booking page redesign | 1 | 2400"' % folder)


def parser():
    p = argparse.ArgumentParser(prog='shelf-invoices', description='Create, number and file invoices as PDF.')
    p.add_argument('--version', action='version', version='shelf-invoices ' + VERSION)
    sub = p.add_subparsers(dest='command', required=True)

    def books_arg(s):
        s.add_argument('--books', help='Books folder (default: the one you set with init)')

    s = sub.add_parser('init', help='Create your books folder')
    s.add_argument('folder')
    s.add_argument('--not-default', action='store_true')
    s.set_defaults(func=cmd_init)
    s = sub.add_parser('company', help='Show, set or check your company details')
    s.add_argument('action', nargs='?', choices=['show', 'set', 'check'], default='show')
    s.add_argument('pair', nargs='?')
    books_arg(s)
    s.set_defaults(func=cmd_company)
    s = sub.add_parser('client', help='List or save clients')
    s.add_argument('action', nargs='?', choices=['list', 'add'], default='list')
    for flag in ('--key', '--name', '--address', '--vat-id', '--email', '--country', '--currency'):
        s.add_argument(flag)
    s.add_argument('--vat-mode', choices=list(money.VAT_MODES))
    books_arg(s)
    s.set_defaults(func=cmd_client)
    s = sub.add_parser('draft', help='Make an unnumbered draft and a preview PDF')
    books_arg(s)
    s.add_argument('--client', help='A saved client')
    s.add_argument('--to-name')
    s.add_argument('--to-address', help='Lines separated by ;')
    s.add_argument('--to-vat-id')
    s.add_argument('--item', action='append', help='"Description | quantity | unit price [| VAT %]" (repeat)')
    s.add_argument('--vat-mode', choices=list(money.VAT_MODES))
    s.add_argument('--currency')
    s.add_argument('--date', help='YYYY-MM-DD (default today)')
    s.add_argument('--due-days', type=int)
    s.add_argument('--po', help="The client's purchase order number")
    s.add_argument('--service-date', help='When the work was done')
    s.add_argument('--notes')
    s.set_defaults(func=cmd_draft)
    s = sub.add_parser('issue', help='Number and file a draft (the member confirms with --yes)')
    s.add_argument('draft')
    s.add_argument('--yes', action='store_true')
    books_arg(s)
    s.set_defaults(func=cmd_issue)
    s = sub.add_parser('credit', help='Issue a credit note that cancels an invoice')
    s.add_argument('number')
    s.add_argument('--reason', required=True)
    s.add_argument('--date')
    s.add_argument('--yes', action='store_true')
    books_arg(s)
    s.set_defaults(func=cmd_credit)
    s = sub.add_parser('list', help='Everything issued')
    s.add_argument('--year', type=int)
    books_arg(s)
    s.set_defaults(func=cmd_list)
    s = sub.add_parser('verify', help='Check an issued PDF against the ledger')
    s.add_argument('number')
    books_arg(s)
    s.set_defaults(func=cmd_verify)
    s = sub.add_parser('sample', help='Make sample books for the fictional Acme Studio Ltd')
    s.add_argument('folder')
    s.set_defaults(func=cmd_sample)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        return args.func(args) or 0
    except (Stop, bk.BooksError, money.MoneyError, pdf.PdfMissing, ValueError) as exc:
        print('Stopped: ' + str(exc), file=sys.stderr)
        return 1
