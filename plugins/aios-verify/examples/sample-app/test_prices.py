import unittest

from prices import ITEMS, format_price, total


class PriceTests(unittest.TestCase):
    def test_format_price(self):
        self.assertEqual(format_price(1234), '£12.34')
        self.assertEqual(format_price(5), '£0.05')
        self.assertEqual(format_price(120000), '£1,200.00')

    def test_negative(self):
        self.assertEqual(format_price(-250), '-£2.50')

    def test_total(self):
        self.assertEqual(total(ITEMS), 173999)


if __name__ == '__main__':
    unittest.main()
