#!/usr/bin/env python3

# Install PyMuPDF
# > pip3 install PyMuPDF

from collections.abc import Iterable

import math, re, sys

import fitz  # this is pymupdf

PAGE_INDEX = 1

def get_block_upper_left(block: tuple) -> tuple:
    return (block[0], block[1])

def get_block_lower_right(block: tuple) -> tuple:
    return (block[2], block[3])

def get_block_text(block: tuple) -> str:
    return block[4]

def find_table_boundary(blocks: Iterable[tuple]) -> tuple:
    min_x = 0.0
    max_x = 0.0
    min_y = 0.0
    max_y = 0.0

    for block in blocks:
        block_text = get_block_text(block)
        if (block_text.startswith('Your Electric Charge Details')):
            min_x, min_y = get_block_upper_left(block)
            max_x, _ = get_block_lower_right(block)
        if (block_text.startswith('Current Electric Charges')):
            max_y = get_block_upper_left(block)[1]

    if min_y == 0.0:
        raise ValueError('Can''t find upper boundary of the table')
    if max_y == 0.0:
        raise ValueError('Can''t find lower boundary of the table')

    return (min_x, max_x, min_y, max_y)

def transform_block_text(text: str) -> list[str]:
    parts = re.split(r'\n|[$]|\(|\)', text, flags=re.MULTILINE)
    stripped = list(map(str.strip, parts))
    filtered = list(filter(lambda x: x != '' and x != 'Electricity', stripped))
    return filtered

def read_pdf(file_name: str) -> Iterable[str]:
    blocks = []

    with fitz.open(file_name) as doc:
        page = doc.load_page(PAGE_INDEX)
        page_blocks = page.get_text('blocks')
        min_x, max_x, min_y, max_y = find_table_boundary(page_blocks)

        new_block = True
        for block in page_blocks:
            upper_left = get_block_upper_left(block)
            bottom_right = get_block_lower_right(block)
            if (min_y < upper_left[1] and upper_left[1] <= max_y
                and min_x <= upper_left[0] and bottom_right[0] <= max_x):

                text = transform_block_text(get_block_text(block))
                if new_block:
                    blocks.append(text)
                else:
                    blocks[-1].extend(text)

                new_block = math.isclose(bottom_right[0], max_x, rel_tol=0.01)

    return blocks


def main() -> int:
    for file_name in sys.argv[1:]:
        blocks = read_pdf(file_name)
        for block in blocks:
            print('------')
            print(block)


if __name__ == '__main__':
    sys.exit(main())