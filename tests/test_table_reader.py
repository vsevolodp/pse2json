import unittest

from pse2json import table_reader
from pse2json.text_block import Rectangle, TextBlock


class TableReaderTests(unittest.TestCase):
    def test_no_upper_boundary(self):
        blocks: list(TextBlock) = []
        
        with self.assertRaises(ValueError) as context:
            table_reader.read_table_rows(blocks, '', '')
        exception = context.exception
        self.assertEqual(str(exception), 'Can\'t find upper boundary of the table')

    def test_no_lower_boundary(self):
        blocks: list(TextBlock) = [
            TextBlock(Rectangle(10, 10, 100, 20), 'Begin')
        ]
        
        with self.assertRaises(ValueError) as context:
            table_reader.read_table_rows(blocks, 'Begin', 'End')
        exception = context.exception
        self.assertEqual(str(exception), 'Can\'t find lower boundary of the table')

    def test_both_boundaries(self):
        blocks: list(TextBlock) = [
            TextBlock(Rectangle(10, 10, 100, 20), 'Begin'),
            TextBlock(Rectangle(10, 20, 100, 30), 'End')
        ]
        
        rows = table_reader.read_table_rows(blocks, 'Begin', 'End')
        self.assertEqual(2, len(rows))
        self.assertEqual('Begin', rows[0])
        self.assertEqual('End', rows[1])
    
    def test_compound_row(self):
        blocks: list(TextBlock) = [
            TextBlock(Rectangle(10, 10, 100, 20), 'Begin'),
            TextBlock(Rectangle(10, 20, 40, 30), 'Row 1\nbegins here'),
            TextBlock(Rectangle(40, 60, 100, 30), 'and ends here'),
            TextBlock(Rectangle(10, 30, 100, 40), 'End')
        ]
        
        rows = table_reader.read_table_rows(blocks, 'Begin', 'End')
        self.assertEqual(3, len(rows))
        self.assertEqual('Begin', rows[0])
        self.assertEqual('Row 1 begins here and ends here', rows[1])
        self.assertEqual('End', rows[2])
    
    def test_short_row(self):
        blocks: list(TextBlock) = [
            TextBlock(Rectangle(10, 10, 100, 20), 'Begin'),
            TextBlock(Rectangle(10, 20, 40, 30), 'Row 1\nbegins here'),
            TextBlock(Rectangle(10, 30, 100, 40), 'End')
        ]
        
        rows = table_reader.read_table_rows(blocks, 'Begin', 'End')
        self.assertEqual(3, len(rows))
        self.assertEqual('Begin', rows[0])
        self.assertEqual('Row 1 begins here', rows[1])
        self.assertEqual('End', rows[2])

    def test_basic_charge_row(self):
        blocks: list(TextBlock) = [
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
        blocks: list(TextBlock) = [
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
        blocks: list(TextBlock) = [
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
        blocks: list(TextBlock) = [
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

if __name__ == '__main__':
    unittest.main()