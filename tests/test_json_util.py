import datetime
import unittest
import json

from pse2json import electricity_bill as eb
from pse2json import json_util

class JsonUtilTests(unittest.TestCase):

    def test_json_encoder(self):
        encoder = json_util.JSONEncoder()

        dataclass = eb.Charge(1.0, 2, 3)
        r1 = encoder.default(dataclass)
        self.assertEqual({ 'rate_usd_per_kwh': 1.0, 'consumed_kwh': 2, 'charge_cents': 3}, r1)

        date = datetime.date(2022, 1, 2)
        r2 = encoder.default(date)
        self.assertEqual('2022-01-02', r2)

        
        dict1 = 'val'
        self.assertRaises(TypeError, encoder.default, dict1)
    
    def test_dataclass_from_dict(self):
        charge_dict = { 'rate_usd_per_kwh': 1.0, 'consumed_kwh': 2.0, 'charge_cents': 3}
        charge = json_util.dataclass_from_dict(eb.Charge, charge_dict)
        self.assertIsInstance(charge, eb.Charge)
        self.assertEqual(1.0, charge.rate_usd_per_kwh)
        self.assertEqual(2.0, charge.consumed_kwh)
        self.assertEqual(3, charge.charge_cents)
        

if __name__ == '__main__':
    unittest.main()