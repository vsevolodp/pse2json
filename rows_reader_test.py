import unittest
import rows_reader as rr


class RowReaderTests(unittest.TestCase):

    def test_basic_charge(self):
        rows = [
            "Basic Charge $10.01 per month 10.01",
            "Subtotal 10.01",
            "Current Electric Charges $ 10.01"]
        result = rr.read_electricity_bill(rows)
        self.assertEqual(1000, result.basic_charge_cents)


if __name__ == '__main__':
    unittest.main()