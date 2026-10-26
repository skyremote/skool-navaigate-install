"""Sample books for a fictional company. Every name, number and bank detail is made up.

The VAT ID uses the GB format but is not a real registration. The IBAN is the documented
example IBAN from the UK banking standard, which no real account uses.
"""
import json
from pathlib import Path

from . import books as bk

COMPANY = {
    'name': 'Acme Studio Ltd',
    'address': ['1 Example Street', 'Bristol', 'BS1 1AA', 'United Kingdom'],
    'email': 'accounts@acme-studio.example',
    'phone': '+44 117 000 0000',
    'website': 'acme-studio.example',
    'country': 'GB',
    'vat_registered': True,
    'vat_id': 'GB000000000',
    'company_number': '00000000',
    'legal_lines': ['Acme Studio Ltd, registered in England and Wales, company number 00000000 (sample company)',
                    'Registered office: 1 Example Street, Bristol BS1 1AA'],
    'bank': {'account_name': 'Acme Studio Ltd', 'bank_name': 'Example Bank', 'iban': 'GB82 WEST 1234 5698 7654 32',
             'bic': 'EXMPGB2L', 'sort_code': '00-00-00', 'account_number': '00000000'},
    'payment_terms_days': 30,
    'currency': 'GBP',
    'vat_rate': '20',
    'prefix': 'ACME',
    'accent': '#C2410C',
    'logo': 'acme-logo.png',
    'footer_note': 'Sample invoice made with shelf-invoices. Not a real company.',
}

CLIENTS = {
    'northwind': {'name': 'Northwind Bakery Ltd', 'address': ['22 Harbour Road', 'Bristol', 'BS8 4RU', 'United Kingdom'],
                  'vat_id': '', 'email': 'owner@northwind-bakery.example', 'country': 'GB', 'currency': '', 'vat_mode': ''},
    'contoso-de': {'name': 'Contoso GmbH', 'address': ['Beispielstrasse 5', '10115 Berlin', 'Germany'],
                   'vat_id': 'DE000000000', 'email': 'ap@contoso.example', 'country': 'DE', 'currency': 'EUR',
                   'vat_mode': 'reverse-charge'},
}


def make(folder):
    folder = Path(folder).expanduser().resolve()
    if (folder / 'company.json').exists():
        raise ValueError('Books already exist in %s. Choose an empty folder.' % folder)
    bk.init(folder, make_default=False)
    data = json.loads(json.dumps(bk.COMPANY))
    data.update(COMPANY)
    bk.private_write(folder / 'company.json', json.dumps(data, indent=2) + '\n')
    bk.private_write(folder / 'clients.json', json.dumps(CLIENTS, indent=2) + '\n')
    try:
        from PIL import Image, ImageDraw
        im = Image.new('RGBA', (600, 200), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([0, 25, 150, 175], radius=30, fill=(194, 65, 12, 255))
        d.polygon([(42, 145), (75, 55), (108, 145)], fill=(255, 255, 255, 255))
        im.save(folder / 'acme-logo.png')
    except ImportError:
        data['logo'] = ''
        bk.private_write(folder / 'company.json', json.dumps(data, indent=2) + '\n')
    return folder
