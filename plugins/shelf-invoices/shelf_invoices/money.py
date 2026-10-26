"""Invoice arithmetic in Decimal: line totals, VAT grouped by rate, rounding half up to the cent."""
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

CENT = Decimal('0.01')
SYMBOLS = {'GBP': '£', 'EUR': '€', 'USD': '$', 'AUD': 'A$', 'CAD': 'C$', 'NZD': 'NZ$', 'CHF': 'CHF ',
           'SEK': 'SEK ', 'NOK': 'NOK ', 'DKK': 'DKK ', 'JPY': '¥', 'INR': '₹'}

VAT_MODES = {
    'standard': '',
    'reverse-charge': 'Reverse charge: the customer must account for the VAT on this supply.',
    'zero-rated': 'Zero-rated supply.',
    'exempt': 'Exempt from VAT.',
    'outside-scope': 'Outside the scope of VAT.',
    'not-registered': 'Not registered for VAT, so no VAT is charged.',
}


class MoneyError(ValueError):
    pass


def dec(value, what='amount'):
    try:
        d = Decimal(str(value).replace(',', '').strip())
    except (InvalidOperation, AttributeError):
        raise MoneyError('Not a number for %s: %r' % (what, value))
    if not d.is_finite():
        raise MoneyError('Not a number for %s: %r' % (what, value))
    return d


def cents(d):
    return d.quantize(CENT, rounding=ROUND_HALF_UP)


def parse_item(text, default_rate):
    """'Description | qty | unit price [| VAT rate %]'"""
    parts = [p.strip() for p in text.split('|')]
    if len(parts) not in (3, 4) or not parts[0]:
        raise MoneyError('Write each line as "Description | quantity | unit price" with an optional "| VAT %%": %r' % text)
    rate = dec(parts[3].rstrip('%'), 'VAT rate') if len(parts) == 4 and parts[3] != '' else dec(default_rate, 'VAT rate')
    qty = dec(parts[1], 'quantity')
    price = dec(parts[2], 'unit price')
    if qty == 0:
        raise MoneyError('Quantity cannot be zero: %r' % text)
    if not Decimal(0) <= rate <= Decimal(100):
        raise MoneyError('VAT rate must be between 0 and 100: %r' % text)
    return {'description': parts[0], 'quantity': str(qty), 'unit_price': str(price), 'vat_rate': str(rate)}


def totals(items, vat_mode):
    """Return computed lines and totals. Non-standard modes charge 0% on every line."""
    if vat_mode not in VAT_MODES:
        raise MoneyError('VAT mode must be one of: ' + ', '.join(VAT_MODES))
    lines, by_rate = [], {}
    net = Decimal(0)
    for item in items:
        qty, price = dec(item['quantity']), dec(item['unit_price'])
        rate = dec(item['vat_rate']) if vat_mode == 'standard' else Decimal(0)
        amount = cents(qty * price)
        net += amount
        by_rate[rate] = by_rate.get(rate, Decimal(0)) + amount
        lines.append(dict(item, vat_rate=str(rate), amount=str(amount)))
    vat_rows = []
    vat = Decimal(0)
    for rate in sorted(by_rate, reverse=True):
        tax = cents(by_rate[rate] * rate / Decimal(100))
        vat += tax
        vat_rows.append({'rate': plain(rate),
                         'net': str(by_rate[rate]), 'vat': str(tax)})
    return {'lines': lines, 'net': str(cents(net)), 'vat_rows': vat_rows, 'vat': str(cents(vat)),
            'total': str(cents(net + vat))}


def fmt(amount, currency):
    d = cents(dec(amount))
    sign = '-' if d < 0 else ''
    body = '{:,.2f}'.format(abs(d))
    symbol = SYMBOLS.get(currency.upper())
    return sign + (symbol + body if symbol else body + ' ' + currency.upper())


def plain(d):
    """20 stays 20, 2.50 becomes 2.5, never 2E+1."""
    text = format(dec(d).normalize(), 'f')
    return text if text != '-0' else '0'


def fmt_qty(value):
    return plain(value)


def fmt_rate(value):
    return plain(value) + '%'
