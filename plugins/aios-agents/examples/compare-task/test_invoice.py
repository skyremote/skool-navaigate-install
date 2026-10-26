import unittest

from invoice import invoice_total, line_total


class InvoiceTests(unittest.TestCase):
    def test_line_total(self):
        self.assertEqual(line_total(3, 10.0), 30.0)

    def test_invoice_total_adds_vat(self):
        self.assertEqual(invoice_total([(2, 50.0), (1, 25.0)]), 150.0)

    def test_empty_invoice(self):
        self.assertEqual(invoice_total([]), 0.0)


if __name__ == '__main__':
    unittest.main()
