#!/usr/bin/env python3

# Install PyMuPDF
# > pip3 install PyMuPDF

import json, sys

from pse2json import electricity_bill as eb
from pse2json import json_util
from pse2json import pdf_text_block_reader as ptbr
from pse2json import rows_reader
from pse2json import table_reader


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
    bills: list[eb.ElectricityBill] = []
    for file_name in sys.argv[1:]:
        bills.append(read_table(file_name))

    match len(bills):
        case 0:
            pass
        case 1:
            bill_json = json.dumps(bills[0], indent=2, cls=json_util.JSONEncoder)
            print(bill_json)
        case _:
            bills_json = json.dumps({ 'bills': bills }, indent=2, cls=json_util.JSONEncoder)
            print(bills_json)


if __name__ == '__main__':
    sys.exit(main())