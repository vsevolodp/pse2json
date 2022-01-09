import unittest

from pse2json import table_reader
from pse2json.text_block import Rectangle, TextBlock


class TableReaderTests(unittest.TestCase):
    def test_no_upper_boundary(self):
        blocks: list[TextBlock] = []
        
        with self.assertRaises(ValueError) as context:
            table_reader.read_table_rows(blocks, '', '')
        exception = context.exception
        self.assertEqual(str(exception), 'Can\'t find upper boundary of the table')

    def test_no_lower_boundary(self):
        blocks = [
            TextBlock(Rectangle(10, 10, 100, 20), 'Begin')
        ]
        
        with self.assertRaises(ValueError) as context:
            table_reader.read_table_rows(blocks, 'Begin', 'End')
        exception = context.exception
        self.assertEqual(str(exception), 'Can\'t find lower boundary of the table')

    def test_both_boundaries(self):
        blocks = [
            TextBlock(Rectangle(10, 10, 100, 20), 'Begin'),
            TextBlock(Rectangle(10, 20, 100, 30), 'End')
        ]
        
        rows = table_reader.read_table_rows(blocks, 'Begin', 'End')
        self.assertEqual(2, len(rows))
        self.assertEqual('Begin', rows[0])
        self.assertEqual('End', rows[1])
    
    def test_compound_row(self):
        blocks = [
            TextBlock(Rectangle(10, 10, 100, 20), 'Begin'),
            TextBlock(Rectangle(10, 20, 40, 30), 'Row 1\nbegins here'),
            TextBlock(Rectangle(40, 20, 100, 30), 'and ends here'),
            TextBlock(Rectangle(10, 30, 100, 40), 'End')
        ]
        
        rows = table_reader.read_table_rows(blocks, 'Begin', 'End')
        self.assertEqual(3, len(rows))
        self.assertEqual('Begin', rows[0])
        self.assertEqual('Row 1 begins here and ends here', rows[1])
        self.assertEqual('End', rows[2])
    
    def test_short_row(self):
        blocks = [
            TextBlock(Rectangle(10, 10, 100, 20), 'Begin'),
            TextBlock(Rectangle(10, 20, 100, 30), 'Row 1\nbegins here'),
            TextBlock(Rectangle(10, 30, 60, 40), 'End')
        ]
        
        rows = table_reader.read_table_rows(blocks, 'Begin', 'End')
        self.assertEqual(3, len(rows))
        self.assertEqual('Begin', rows[0])
        self.assertEqual('Row 1 begins here', rows[1])
        self.assertEqual('End', rows[2])

    def test_basic_charge_row(self):
        blocks = [
            TextBlock(
                Rectangle(left=22.0, top=105.26678466796875, right=374.03521728515625, bottom=114.20428466796875),
                'Your Electric Charge Details (31 days)\nRate x Unit\n= \nCharge\n'),
            TextBlock(
                Rectangle(left=22.0, top=118.466064453125, right=374.03521728515625, bottom=137.45330810546875),
                '1,383 kWh used for service 11/7/2019 - 12/7/2019\nBasic Charge\n $7.49\nper month \n$ \n7.49\n'),
            TextBlock(
                Rectangle(left=22.0, top=232.10882568359375, right=374.0321960449219, bottom=241.04632568359375),
                'Current Electric Charges\n$ \n139.09\n')
        ]
        
        rows = table_reader.read_table_rows(blocks, 'Your Electric Charge Details', 'Current Electric Charges')
        self.assertEqual(4, len(rows))
        self.assertEqual('1,383 kWh used for service 11/7/2019 - 12/7/2019', rows[1])
        self.assertEqual('Basic Charge $7.49 per month 7.49', rows[2])

    def test_shorter_tax_row(self):
        blocks = [
            TextBlock(
                Rectangle(left=22.0, top=105.26678466796875, right=374.03521728515625, bottom=114.20428466796875),
                'Your Electric Charge Details (31 days)\nRate x Unit\n= \nCharge\n'),
            TextBlock(
                Rectangle(left=22.0, top=209.7108154296875, right=321.7586669921875, bottom=229.8472900390625),
                'Taxes\n \nState Utility Tax ($5.39 included in above charges)\n 3.873%\n \n \n'),
            TextBlock(
                Rectangle(left=22.0, top=232.10882568359375, right=374.0321960449219, bottom=241.04632568359375),
                'Current Electric Charges\n$ \n139.09\n')
        ]
        
        rows = table_reader.read_table_rows(blocks, 'Your Electric Charge Details', 'Current Electric Charges')
        self.assertEqual(3, len(rows))
        self.assertEqual('Taxes State Utility Tax ($5.39 included in above charges) 3.873%', rows[1])
        self.assertEqual('Current Electric Charges $ 139.09', rows[2])

    def test_replace_unicode_minus_sign(self):
        blocks = [
            TextBlock(
                Rectangle(left=22.0, top=105.26678466796875, right=374.03521728515625, bottom=114.20428466796875),
                'Your Electric Charge Details (31 days)\nRate x Unit\n= \nCharge\n'),
            TextBlock(
                Rectangle(left=22.0, top=173.31280517578125, right=374.0342102050781, bottom=182.25030517578125),
                'Energy Exchange Credit\n \u22120.007386\n1,383 kWh \n \n\u221210.21\n'),
            TextBlock(
                Rectangle(left=22.0, top=232.10882568359375, right=374.0321960449219, bottom=241.04632568359375),
                'Current Electric Charges\n$ \n139.09\n')
        ]
        
        rows = table_reader.read_table_rows(blocks, 'Your Electric Charge Details', 'Current Electric Charges')
        self.assertEqual(3, len(rows))
        self.assertEqual('Energy Exchange Credit -0.007386 1,383 kWh -10.21', rows[1])

    def test_remove_electricity_leading_word(self):
        blocks = [
            TextBlock(
                Rectangle(left=22.0, top=105.26678466796875, right=374.03521728515625, bottom=114.20428466796875),
                'Your Electric Charge Details (31 days)\nRate x Unit\n= \nCharge\n'),
            TextBlock(
                Rectangle(left=22.0, top=139.71478271484375, right=374.033203125, bottom=159.851318359375),
                'Electricity\n \nTier 1 (First 600 kWh Used)\n 0.090982\n600 kWh \n \n54.59\n'),
            TextBlock(
                Rectangle(left=22.0, top=232.10882568359375, right=374.0321960449219, bottom=241.04632568359375),
                'Current Electric Charges\n$ \n139.09\n')
        ]
        
        rows = table_reader.read_table_rows(blocks, 'Your Electric Charge Details', 'Current Electric Charges')
        self.assertEqual(3, len(rows))
        self.assertEqual('Tier 1 (First 600 kWh Used) 0.090982 600 kWh 54.59', rows[1])

    def test_complex_table(self):
        blocks = [
            TextBlock(
                Rectangle(left=22.0, top=105.26678466796875, right=374.03521728515625, bottom=114.20428466796875),
                'Your Electric Charge Details (30 days)\nRate x Unit\n= \nCharge\n'),
            TextBlock(
                Rectangle(left=22.0, top=118.466064453125, right=374.03521728515625, bottom=137.45330810546875),
                '1,629 kWh used for service 12/9/2020 - 1/7/2021\nBasic Charge\n $7.49\nper month \n$ \n7.49\n'),
            TextBlock(
                Rectangle(left=22.0, top=139.71478271484375, right=131.46466064453125, bottom=159.851318359375),
                'Electricity\n \nTier 1 (First 460 kWh Used) \n'),
            TextBlock(
                Rectangle(left=22.0, top=160.11279296875, right=110.0660629272461, bottom=169.05029296875),
                '(12/9/2020 - 12/31/2020)\n'),
            TextBlock(
                Rectangle(left=209.2100067138672, top=150.913818359375, right=374.033203125, bottom=159.851318359375),
                ' 0.094437\n460 kWh \n \n43.44\n'),
            TextBlock(
                Rectangle(left=22.0, top=171.31280517578125, right=138.59765625, bottom=180.25030517578125),
                ' \nTier 2 (Above 460 kWh Used) \n'),
            TextBlock(
                Rectangle(left=22.0, top=180.5118408203125, right=110.0660629272461, bottom=189.4493408203125),
                '(12/9/2020 - 12/31/2020)\n'),
            TextBlock(
                Rectangle(left=209.2100067138672, top=171.31280517578125, right=374.033203125, bottom=180.25030517578125),
                ' 0.114643\n788.9 kWh \n \n90.44\n'),
            TextBlock(
                Rectangle(left=22.0, top=191.7108154296875, right=374.033203125, bottom=200.6483154296875),
                ' \nTier 1 (First 140 kWh Used) (1/1/2021 - 1/7/2021)  0.093697\n140 kWh \n \n13.12\n'),
            TextBlock(
                Rectangle(left=22.0, top=202.9097900390625, right=138.59765625, bottom=211.8472900390625),
                ' \nTier 2 (Above 140 kWh Used) \n'),
            TextBlock(
                Rectangle(left=22.0, top=212.10882568359375, right=96.71906280517578, bottom=221.04632568359375),
                '(1/1/2021 - 1/7/2021)\n'),
            TextBlock(
                Rectangle(left=209.2100067138672, top=202.9097900390625, right=374.033203125, bottom=211.8472900390625),
                ' 0.113903\n240.1 kWh \n \n27.35\n'),
            TextBlock(
                Rectangle(left=22.0, top=223.308837890625, right=374.0342102050781, bottom=232.246337890625),
                'Energy Exchange Credit\n \u22120.007386\n1,629 kWh \n \n\u221212.03\n'),
            TextBlock(
                Rectangle(left=22.0, top=234.5078125, right=120.25765991210938, bottom=252.644287109375),
                'Federal Wind Power Credit \n(12/9/2020 - 12/31/2020)\n'),
            TextBlock(
                Rectangle(left=204.53799438476562, top=234.5078125, right=374.03521728515625, bottom=243.4453125),
                ' \u22120.001893\n1,248.9 kWh \n \n\u22122.36\n'),
            TextBlock(
                Rectangle(left=22.0, top=254.90582275390625, right=374.03521728515625, bottom=263.84332275390625),
                'Federal Wind Power Credit (1/1/2021 - 1/7/2021)\n \u22120.001440\n380.1 kWh \n \n\u22120.55\n'),
            TextBlock(
                Rectangle(left=22.0, top=266.10479736328125, right=374.03521728515625, bottom=275.04229736328125),
                'Renewable Energy Credit (12/9/2020 - 12/31/2020) \u22120.000082\n1,248.9 kWh \n \n\u22120.10\n'),
            TextBlock(
                Rectangle(left=22.0, top=277.3048095703125, right=374.03521728515625, bottom=286.2423095703125),
                'Renewable Energy Credit (1/1/2021 - 1/7/2021)\n \u22120.000043\n380.1 kWh \n \n\u22120.02\n'),
            TextBlock(
                Rectangle(left=22.0, top=288.5038146972656, right=374.033203125, bottom=297.4413146972656),
                'Other Electric Charges & Credits\n 0.006794\n1,629 kWh \n \n11.07\n'),
            TextBlock(
                Rectangle(left=22.0, top=299.70281982421875, right=374.0321960449219, bottom=308.64031982421875),
                'Subtotal\n \n \n \n177.85\n'),
            TextBlock(
                Rectangle(left=22.0, top=313.70281982421875, right=321.7586669921875, bottom=333.8393249511719),
                'Taxes\n \nState Utility Tax ($6.89 included in above charges)\n 3.873%\n \n \n'),
            TextBlock(
                Rectangle(left=22.0, top=336.101806640625, right=374.0321960449219, bottom=345.039306640625),
                'Current Electric Charges\n$ \n177.85\n')
        ]

        rows = table_reader.read_table_rows(blocks, 'Your Electric Charge Details', 'Current Electric Charges')

        self.assertEqual(16, len(rows))
        self.assertEqual('1,629 kWh used for service 12/9/2020 - 1/7/2021', rows[1])
        self.assertEqual('Basic Charge $7.49 per month 7.49', rows[2])
        self.assertEqual('Tier 1 (First 460 kWh Used) (12/9/2020 - 12/31/2020) 0.094437 460 kWh 43.44', rows[3])
        self.assertEqual('Tier 2 (Above 460 kWh Used) (12/9/2020 - 12/31/2020) 0.114643 788.9 kWh 90.44', rows[4])
        self.assertEqual('Tier 1 (First 140 kWh Used) (1/1/2021 - 1/7/2021) 0.093697 140 kWh 13.12', rows[5])
        self.assertEqual('Tier 2 (Above 140 kWh Used) (1/1/2021 - 1/7/2021) 0.113903 240.1 kWh 27.35', rows[6])
        self.assertEqual('Energy Exchange Credit -0.007386 1,629 kWh -12.03', rows[7])
        self.assertEqual('Federal Wind Power Credit (12/9/2020 - 12/31/2020) -0.001893 1,248.9 kWh -2.36', rows[8])
        self.assertEqual('Federal Wind Power Credit (1/1/2021 - 1/7/2021) -0.001440 380.1 kWh -0.55', rows[9])
        self.assertEqual('Renewable Energy Credit (12/9/2020 - 12/31/2020) -0.000082 1,248.9 kWh -0.10', rows[10])
        self.assertEqual('Renewable Energy Credit (1/1/2021 - 1/7/2021) -0.000043 380.1 kWh -0.02', rows[11])
        self.assertEqual('Other Electric Charges & Credits 0.006794 1,629 kWh 11.07', rows[12])
        self.assertEqual('Subtotal 177.85', rows[13])
        self.assertEqual('Taxes State Utility Tax ($6.89 included in above charges) 3.873%', rows[14])
        self.assertEqual('Current Electric Charges $ 177.85', rows[15])


if __name__ == '__main__':
    unittest.main()