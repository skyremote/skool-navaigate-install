"""Acme Studio invoice totals (fictional sample for the module 7 comparison)."""

VAT_RATE = 0.20


def line_total(quantity, unit_price):
    """Price of one invoice line before VAT, in pounds."""
    return quantity * unit_price


def invoice_total(lines):
    """Total of all lines including VAT, rounded to pence.

    lines is a list of (quantity, unit_price) pairs.
    """
    net = sum(line_total(q, p) for q, p in lines)
    return round(net * (1 + VAT_RATE), 2)
