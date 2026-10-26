"""Build the price list page into dist/index.html."""
from html import escape
from pathlib import Path

from prices import ITEMS, format_price, total

rows = ''.join('<tr><td>%s</td><td>%s</td></tr>' % (escape(n), format_price(p)) for n, p in ITEMS)
page = ('<!doctype html><meta charset="utf-8"><title>Acme Studio prices</title>'
        '<style>body{font:20px/1.5 -apple-system,sans-serif;margin:60px;color:#171717}'
        'table{border-collapse:collapse;min-width:480px}td{padding:10px 16px;border-bottom:1px solid #ddd}'
        'td:last-child{text-align:right}tfoot td{font-weight:700}</style>'
        '<h1>Acme Studio prices</h1><table>%s<tfoot><tr><td>Total</td><td>%s</td></tr></tfoot></table>'
        % (rows, format_price(total(ITEMS))))
Path('dist').mkdir(exist_ok=True)
Path('dist/index.html').write_text(page)
print('Built dist/index.html')
