"""The member's books folder: company details, clients, drafts, the numbered ledger and the filed PDFs.

    <books>/company.json     your company details (the settings the invoices are made from)
    <books>/clients.json     saved clients
    <books>/drafts/          drafts, never numbered
    <books>/ledger.json      every number ever issued, in order, with the PDF's SHA-256
    <books>/ledger.csv       the same, for your accountant
    <books>/<year>/          issued invoices and credit notes: PDF plus the JSON it was made from

~/.config/aios/shelf-invoices.json remembers which books folder is yours (AIOS_CONFIG_DIR moves it).
"""
import contextlib
import copy
import csv
import datetime
import fcntl
import hashlib
import json
import os
import re
from pathlib import Path

COMPANY = {
    'name': '',
    'address': [],
    'email': '',
    'phone': '',
    'website': '',
    'country': '',
    'vat_registered': True,
    'vat_id': '',
    'tax_label': 'VAT',
    'tax_number': '',
    'company_number': '',
    'legal_lines': [],
    'bank': {'account_name': '', 'bank_name': '', 'iban': '', 'bic': '', 'sort_code': '', 'account_number': ''},
    'payment_terms_days': 30,
    'currency': 'GBP',
    'vat_rate': '20',
    'number_format': '{prefix}-{year}-{seq:04d}',
    'prefix': 'INV',
    'credit_prefix': 'CN',
    'number_reset': 'yearly',
    'logo': '',
    'accent': '#2B5D8A',
    'font_file': '',
    'font_bold_file': '',
    'footer_note': '',
}
LIST_KEYS = ('address', 'legal_lines')


class BooksError(ValueError):
    pass


def config_file():
    override = os.environ.get('AIOS_CONFIG_DIR', '').strip()
    base = Path(override) if override else Path.home() / '.config' / 'aios'
    return base / 'shelf-invoices.json'


def default_books():
    f = config_file()
    if f.exists():
        value = json.loads(f.read_text()).get('books', '')
        if value:
            return Path(os.path.expanduser(value))
    return None


def remember(books):
    f = config_file()
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps({'books': str(Path(books).resolve())}, indent=2) + '\n')


def resolve_books(explicit):
    books = Path(os.path.expanduser(explicit)).resolve() if explicit else default_books()
    if not books:
        raise BooksError('No books folder yet. Run: shelf-invoices init ~/Documents/Invoices')
    if not (books / 'company.json').exists():
        raise BooksError('No company.json in %s. Run: shelf-invoices init "%s"' % (books, books))
    return books


def private_write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name('.' + path.name + '.tmp')
    fd = os.open(str(tmp), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w') as stream:
        stream.write(text)
    os.replace(tmp, path)


def init(books, make_default=True):
    books = Path(os.path.expanduser(books)).resolve()
    books.mkdir(parents=True, exist_ok=True)
    os.chmod(books, 0o700)
    if not (books / 'company.json').exists():
        private_write(books / 'company.json', json.dumps(COMPANY, indent=2) + '\n')
    if not (books / 'clients.json').exists():
        private_write(books / 'clients.json', '{}\n')
    if not (books / 'ledger.json').exists():
        private_write(books / 'ledger.json', json.dumps({'documents': []}, indent=2) + '\n')
    if make_default:
        remember(books)
    return books


def _merge(base, extra):
    out = copy.deepcopy(base)
    for k, v in (extra or {}).items():
        out[k] = _merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def company(books):
    return _merge(COMPANY, json.loads((books / 'company.json').read_text()))


def resolve_path(books, value):
    if not value:
        return ''
    p = Path(os.path.expanduser(value))
    return str(p if p.is_absolute() else books / p)


def set_company(books, dotted, value):
    data = json.loads((books / 'company.json').read_text())
    parts = dotted.split('.')
    node, defaults = data, COMPANY
    for part in parts[:-1]:
        if part not in defaults or not isinstance(defaults[part], dict):
            raise BooksError('Unknown company setting: ' + dotted)
        node = node.setdefault(part, {})
        defaults = defaults[part]
    leaf = parts[-1]
    if leaf not in defaults or isinstance(defaults[leaf], dict):
        raise BooksError('Unknown company setting: ' + dotted)
    old = defaults[leaf]
    if isinstance(old, bool):
        value = value.strip().lower() in ('true', 'yes', '1', 'on')
    elif isinstance(old, int):
        value = int(value)
    elif isinstance(old, list):
        value = [x.strip() for x in value.split(';') if x.strip()]
    if leaf in ('logo', 'font_file', 'font_bold_file') and value and not Path(resolve_path(books, value)).exists():
        raise BooksError('File not found: ' + value)
    if leaf == 'number_format':
        try:
            value.format(prefix='X', year=2026, month=1, seq=1)
        except (KeyError, ValueError, IndexError):
            raise BooksError('number_format may use {prefix}, {year}, {month} and {seq}, such as {prefix}-{year}-{seq:04d}')
        if '{seq' not in value:
            raise BooksError('number_format must include {seq} so every number is different.')
    if leaf == 'number_reset' and value not in ('yearly', 'never'):
        raise BooksError('number_reset is yearly or never.')
    node[leaf] = value
    private_write(books / 'company.json', json.dumps(data, indent=2) + '\n')
    return company(books)


def check_company(c):
    """What an invoice must carry. Rules differ by country: this is a minimum, not tax advice."""
    missing = []
    if not c['name']:
        missing.append('name')
    if not c['address']:
        missing.append('address (use ; between lines)')
    if c['vat_registered'] and not c['vat_id']:
        missing.append('vat_id (or set vat_registered=false)')
    bank = c['bank']
    if not (bank['iban'] or bank['account_number']):
        missing.append('bank.iban or bank.account_number (so the client can pay you)')
    return missing


def clients(books):
    return json.loads((books / 'clients.json').read_text())


def slug(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')[:40] or 'client'


def add_client(books, key, record):
    data = clients(books)
    key = slug(key)
    data[key] = record
    private_write(books / 'clients.json', json.dumps(data, indent=2) + '\n')
    return key


@contextlib.contextmanager
def ledger_lock(books):
    with open(books / '.ledger.lock', 'w') as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def ledger(books):
    return json.loads((books / 'ledger.json').read_text())


def next_number(books, c, kind, date):
    """The next number in the series. Call inside ledger_lock."""
    docs = [d for d in ledger(books)['documents'] if d['kind'] == kind]
    year = date.year
    if c['number_reset'] == 'yearly':
        docs = [d for d in docs if d['year'] == year]
    seq = max([d['seq'] for d in docs] or [0]) + 1
    prefix = c['prefix'] if kind == 'invoice' else c['credit_prefix']
    number = c['number_format'].format(prefix=prefix, year=year, month='%02d' % date.month, seq=seq)
    if any(d['number'] == number for d in ledger(books)['documents']):
        raise BooksError('Number %s is already used. Check number_format and number_reset.' % number)
    return number, seq


def record(books, entry):
    data = ledger(books)
    data['documents'].append(entry)
    private_write(books / 'ledger.json', json.dumps(data, indent=2) + '\n')
    write_csv(books, data)


def write_csv(books, data):
    fields = ['number', 'kind', 'date', 'due', 'client', 'currency', 'net', 'vat', 'total', 'vat_mode', 'status',
              'credits', 'file', 'sha256']
    lines = [fields] + [[d.get(f, '') for f in fields] for d in data['documents']]
    tmp = books / '.ledger.csv.tmp'
    with open(tmp, 'w', newline='') as stream:
        csv.writer(stream).writerows(lines)
    os.replace(tmp, books / 'ledger.csv')


def mark(books, number, **changes):
    data = ledger(books)
    for d in data['documents']:
        if d['number'] == number:
            d.update(changes)
    private_write(books / 'ledger.json', json.dumps(data, indent=2) + '\n')
    write_csv(books, data)


def find(books, number):
    for d in ledger(books)['documents']:
        if d['number'] == number:
            return d
    raise BooksError('No invoice or credit note numbered %s in this ledger.' % number)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def today():
    return datetime.date.today()


def parse_date(value):
    try:
        return datetime.date.fromisoformat(value)
    except ValueError:
        raise BooksError('Dates are YYYY-MM-DD, such as 2026-10-26: %r' % value)
