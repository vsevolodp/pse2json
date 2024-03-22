#!/usr/bin/env python3

# Install PyMuPDF
# > pip3 install PyMuPDF

import sys

from pse2json import electricity_bill as eb
from pse2json import pdf_text_block_reader as ptbr
from pse2json import rows_reader
from pse2json import table_reader


PAGE_INDEX = 1
FROM_TEXT = 'Your Electric Charge Details'
TO_TEXT = 'Current Electric Charges'


def read_table(file_name: str) -> eb.ElectricityBill:
    
    blocks = ptbr.read_text_blocks(file_name, PAGE_INDEX)
    rows = table_reader.read_table_rows(blocks, FROM_TEXT, TO_TEXT)
    return rows_reader.read_electricity_bill(rows)


def main() -> int:
    bills: list[eb.ElectricityBill] = []
    for file_name in sys.argv[1:]:
        bills.append(read_table(file_name))

    match len(bills):
        case 0:
            pass
        case 1:
            bill_json = bills[0].to_json(indent=2)
            print(bill_json)
        case _:
            bills_list = eb.ElectricityBillList(bills=bills)
            bills_json = bills_list.to_json(indent=2)
            print(bills_json)

    return 0


if __name__ == '__main__':
    sys.exit(main())