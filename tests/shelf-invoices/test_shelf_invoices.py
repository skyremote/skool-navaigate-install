"""Tests for the shelf-invoices pack. Run: python3 -m unittest discover -s tests/shelf-invoices"""
import io
import json
import os
import stat
import sys
import tempfile
import threading
import unittest
from contextlib import redirect_stderr, redirect_stdout
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'plugins/shelf-invoices'))
from shelf_invoices import books as bk  # noqa: E402
from shelf_invoices import money, pdf, sample  # noqa: E402
from shelf_invoices.cli import main  # noqa: E402

try:
    import reportlab  # noqa: F401
    HAVE_REPORTLAB = True
except ImportError:
    HAVE_REPORTLAB = False


class MoneyTests(unittest.TestCase):
    def test_parse_item(self):
        item = money.parse_item('Design | 2 | 1,200.50', '20')
        self.assertEqual(item, {'description': 'Design', 'quantity': '2', 'unit_price': '1200.50', 'vat_rate': '20'})
        self.assertEqual(money.parse_item('Hosting | 1 | 25 | 0%', '20')['vat_rate'], '0')

    def test_parse_item_errors(self):
        for bad in ('no pipes', 'X | two | 3', 'X | 0 | 3', 'X | 1 | 3 | 120', ' | 1 | 3'):
            with self.assertRaises(money.MoneyError, msg=bad):
                money.parse_item(bad, '20')

    def test_totals_group_vat_by_rate(self):
        items = [money.parse_item('A | 1 | 2400', '20'), money.parse_item('B | 1 | 650', '20'),
                 money.parse_item('C | 3 | 10 | 5', '20')]
        t = money.totals(items, 'standard')
        self.assertEqual((t['net'], t['vat'], t['total']), ('3080.00', '611.50', '3691.50'))
        self.assertEqual([r['rate'] for r in t['vat_rows']], ['20', '5'])

    def test_rounding_half_up_per_line(self):
        t = money.totals([money.parse_item('A | 3 | 0.335', '20')], 'standard')
        self.assertEqual(t['lines'][0]['amount'], '1.01')   # 1.005 rounds up
        self.assertEqual(t['vat'], '0.20')

    def test_non_standard_modes_charge_no_vat(self):
        items = [money.parse_item('A | 1 | 100', '20')]
        for mode in ('reverse-charge', 'zero-rated', 'exempt', 'outside-scope', 'not-registered'):
            t = money.totals(items, mode)
            self.assertEqual((t['vat'], t['total']), ('0.00', '100.00'), mode)
            self.assertTrue(money.VAT_MODES[mode])

    def test_format(self):
        self.assertEqual(money.fmt('3690', 'GBP'), '£3,690.00')
        self.assertEqual(money.fmt('-1800', 'EUR'), '-€1,800.00')
        self.assertEqual(money.fmt('12.5', 'PLN'), '12.50 PLN')
        self.assertEqual(money.fmt_rate('20'), '20%')
        self.assertEqual(money.fmt_rate('5.50'), '5.5%')
        self.assertEqual(money.fmt_qty('10'), '10')
        self.assertEqual(money.fmt_qty('-1'), '-1')

    def test_bad_mode(self):
        with self.assertRaises(money.MoneyError):
            money.totals([], 'sometimes')


class Books(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='shelf-invoices-test-')
        self.dir = Path(self.tmp.name)
        self.env = patch.dict(os.environ, {'AIOS_CONFIG_DIR': str(self.dir / 'config'), 'HOME': str(self.dir)})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main([str(a) for a in args])
        return code, out.getvalue(), err.getvalue()

    def sample_books(self):
        return sample.make(self.dir / 'books')


class BooksTests(Books):
    def test_init_is_private_and_default(self):
        b = bk.init(self.dir / 'mine')
        self.assertEqual(bk.resolve_books(None), b.resolve())
        self.assertEqual(stat.S_IMODE((b / 'company.json').stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(b.stat().st_mode), 0o700)

    def test_no_books_message(self):
        with self.assertRaises(bk.BooksError) as cm:
            bk.resolve_books(None)
        self.assertIn('shelf-invoices init', str(cm.exception))

    def test_company_set_types_and_checks(self):
        b = bk.init(self.dir / 'mine')
        self.assertIn('name', bk.check_company(bk.company(b)))
        bk.set_company(b, 'address', '1 Road;Town;AB1 2CD')
        bk.set_company(b, 'payment_terms_days', '14')
        bk.set_company(b, 'vat_registered', 'false')
        c = bk.company(b)
        self.assertEqual((c['address'], c['payment_terms_days'], c['vat_registered']), (['1 Road', 'Town', 'AB1 2CD'], 14, False))
        for key, value in (('colour', 'x'), ('number_format', '{prefix}-{year}'), ('number_reset', 'monthly'),
                           ('logo', 'missing.png')):
            with self.assertRaises(bk.BooksError, msg=key):
                bk.set_company(b, key, value)

    def test_numbering_yearly_and_never(self):
        b = self.sample_books()
        c = bk.company(b)
        n1, _ = bk.next_number(b, c, 'invoice', bk.parse_date('2026-03-01'))
        self.assertEqual(n1, 'ACME-2026-0001')
        bk.record(b, {'number': n1, 'seq': 1, 'year': 2026, 'kind': 'invoice', 'total': '1', 'status': 'issued'})
        self.assertEqual(bk.next_number(b, c, 'invoice', bk.parse_date('2026-04-01'))[0], 'ACME-2026-0002')
        self.assertEqual(bk.next_number(b, c, 'invoice', bk.parse_date('2027-01-02'))[0], 'ACME-2027-0001')
        self.assertEqual(bk.next_number(b, c, 'credit', bk.parse_date('2026-04-01'))[0], 'CN-2026-0001')
        c['number_reset'] = 'never'
        self.assertEqual(bk.next_number(b, c, 'invoice', bk.parse_date('2027-01-02'))[0], 'ACME-2027-0002')


@unittest.skipUnless(HAVE_REPORTLAB, 'ReportLab not installed')
class FlowTests(Books):
    def draft(self, b, *extra):
        return self.cli('draft', '--books', b, '--date', '2026-10-26', *extra)

    def test_full_flow(self):
        b = self.sample_books()
        code, out, err = self.draft(b, '--client', 'northwind', '--item', 'Design | 1 | 2400', '--item', 'Hosting | 1 | 25 | 0',
                                    '--po', 'NW-1')
        self.assertEqual(code, 0, err)
        self.assertIn('£2,905.00', out)
        self.assertTrue((b / 'drafts/northwind_draft_v1.pdf').exists())
        self.assertEqual(bk.ledger(b)['documents'], [], 'a draft is never numbered')
        code, _, err = self.cli('issue', 'northwind_draft_v1', '--books', b)
        self.assertEqual(code, 1)
        self.assertIn('must not issue', err)
        self.assertEqual(self.cli('issue', 'northwind_draft_v1', '--books', b, '--yes')[0], 0)
        filed = b / '2026/ACME-2026-0001_northwind.pdf'
        self.assertTrue(filed.exists())
        self.assertTrue(filed.with_suffix('.json').exists())
        code, out, _ = self.cli('verify', 'ACME-2026-0001', '--books', b)
        self.assertEqual(code, 0, out)
        code, _, err = self.cli('issue', 'northwind_draft_v1', '--books', b, '--yes')
        self.assertEqual(code, 1)
        self.assertIn('already issued', err)
        csv_text = (b / 'ledger.csv').read_text()
        self.assertIn('ACME-2026-0001,invoice,2026-10-26,2026-11-25,Northwind Bakery Ltd,GBP,2425.00,480.00,2905.00', csv_text)

    def test_pdf_text_has_the_essentials(self):
        b = self.sample_books()
        self.draft(b, '--client', 'contoso-de', '--item', 'Workshop | 1 | 1800')
        self.cli('issue', 'contoso-de_draft_v1', '--books', b, '--yes')
        text = pdf.text_of(b / '2026/ACME-2026-0001_contoso-de.pdf')
        if text is None:
            self.skipTest('No PDF text extractor')
        flat = ' '.join(text.split())
        for needle in ('ACME-2026-0001', 'Contoso GmbH', 'DE000000000', 'GB000000000', 'Reverse charge',
                       '€1,800.00', 'GB82 WEST 1234 5698 7654 32'):
            self.assertIn(needle, flat)

    def test_reverse_charge_needs_client_vat_id(self):
        b = self.sample_books()
        code, _, err = self.draft(b, '--to-name', 'Someone GmbH', '--to-address', 'Berlin', '--vat-mode', 'reverse-charge',
                                  '--item', 'X | 1 | 10')
        self.assertEqual(code, 1)
        self.assertIn('VAT ID', err)

    def test_not_registered_forces_no_vat(self):
        b = self.sample_books()
        bk.set_company(b, 'vat_registered', 'false')
        code, out, _ = self.draft(b, '--client', 'northwind', '--item', 'X | 1 | 100')
        self.assertEqual(code, 0)
        self.assertIn('total £100.00 (not-registered)', out)

    def test_incomplete_company_refused(self):
        b = bk.init(self.dir / 'empty')
        code, _, err = self.draft(b, '--to-name', 'X', '--item', 'X | 1 | 1')
        self.assertEqual(code, 1)
        self.assertIn('Finish your company details', err)

    def test_credit_note_cancels_and_marks(self):
        b = self.sample_books()
        self.draft(b, '--client', 'northwind', '--item', 'Design | 1 | 100')
        self.cli('issue', 'northwind_draft_v1', '--books', b, '--yes')
        self.assertEqual(self.cli('credit', 'ACME-2026-0001', '--books', b, '--reason', 'Duplicate')[0], 1)
        self.assertEqual(self.cli('credit', 'ACME-2026-0001', '--books', b, '--reason', 'Duplicate', '--yes')[0], 0)
        docs = {d['number']: d for d in bk.ledger(b)['documents']}
        self.assertEqual(docs['ACME-2026-0001']['status'], 'credited')
        self.assertEqual(docs['CN-2026-0001']['total'], '-120.00')
        self.assertIn('credited', (b / 'ledger.csv').read_text())
        self.assertEqual(self.cli('credit', 'ACME-2026-0001', '--books', b, '--reason', 'Again', '--yes')[0], 1)

    def test_tampered_pdf_fails_verify(self):
        b = self.sample_books()
        self.draft(b, '--client', 'northwind', '--item', 'Design | 1 | 100')
        self.cli('issue', 'northwind_draft_v1', '--books', b, '--yes')
        f = b / '2026/ACME-2026-0001_northwind.pdf'
        f.write_bytes(f.read_bytes() + b'\n% edited\n')
        code, out, _ = self.cli('verify', 'ACME-2026-0001', '--books', b)
        self.assertEqual(code, 1)
        self.assertIn('changed after it was issued', out)

    def test_parallel_issues_never_share_a_number(self):
        b = self.sample_books()
        c = bk.company(b)
        docs = []
        for i in range(6):
            doc = {'kind': 'invoice', 'date': '2026-10-26', 'due': '2026-11-25', 'currency': 'GBP', 'vat_mode': 'standard',
                   'client': {'key': 'c%d' % i, 'name': 'Client %d' % i, 'address': ['Town']},
                   'items': [money.parse_item('X | 1 | %d' % (i + 1), '20')]}
            doc['totals'] = money.totals(doc['items'], 'standard')
            docs.append(doc)
        from shelf_invoices.cli import issue_doc
        threads = [threading.Thread(target=issue_doc, args=(b, c, d, 'invoice')) for d in docs]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        numbers = [d['number'] for d in bk.ledger(b)['documents']]
        self.assertEqual(sorted(numbers), ['ACME-2026-%04d' % n for n in range(1, 7)])

    def test_long_invoice_refused_not_cut(self):
        b = self.sample_books()
        items = []
        for i in range(40):
            items += ['--item', 'Line %d with a longer description to fill the page | 1 | 10' % i]
        code, _, err = self.draft(b, '--client', 'northwind', *items)
        self.assertEqual(code, 1)
        self.assertIn('does not fit on one page', err)

    def test_sample_uses_only_fictional_details(self):
        b = self.sample_books()
        text = (b / 'company.json').read_text() + (b / 'clients.json').read_text()
        self.assertIn('.example', text)
        self.assertNotIn('navaigate', text.lower())
        self.assertEqual(Decimal(json.loads((b / 'company.json').read_text())['vat_rate']), Decimal(20))


if __name__ == '__main__':
    unittest.main()
