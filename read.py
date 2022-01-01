#!/usr/bin/env python3

# Install PyMuPDF
# > pip3 install PyMuPDF

import sys

import electricity_bill as eb
import pdf_text_block_reader as ptbr
import rows_reader
import table_reader


PAGE_INDEX = 1
FROM_TEXT = 'Your Electric Charge Details'
TO_TEXT = 'Current Electric Charges'


def read_table(file_name: str) -> eb.ElectricityBill:
    
    blocks = ptbr.read_text_blocks(file_name, PAGE_INDEX)
    rows = table_reader.read_table_rows(blocks, FROM_TEXT, TO_TEXT)

    # for row in rows:
    #     print('------')
    #     print(row)

    bill: eb.ElectricityBill = rows_reader.read_electricity_bill(rows)
    return bill


def main() -> int:
    for file_name in sys.argv[1:]:
        bill = read_table(file_name)
        print(bill)


if __name__ == '__main__':
    sys.exit(main())