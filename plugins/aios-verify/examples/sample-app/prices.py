"""Acme Studio price list (fictional sample app for module 8)."""


def format_price(pence):
    """Format a whole number of pence as pounds, for example 1234 -> '£12.34'."""
    if pence < 0:
        return '-' + format_price(-pence)
    return '£{:,}.{:02d}'.format(pence // 100, pence % 100)


def total(items):
    """Sum a list of (name, pence) pairs."""
    return sum(pence for _, pence in items)


ITEMS = [('Logo design', 45000), ('Brand guide', 120000), ('Business cards', 8999)]
