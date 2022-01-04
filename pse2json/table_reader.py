import math, re

from collections.abc import Iterable

from pse2json.text_block import Rectangle, TextBlock

_BASIC_CHARGE = ' Basic Charge '
_BASIC_CHARGE_OFFSET = 1

_RE_SPACES = re.compile(r'\s+')
_RE_ELECTRICITY = re.compile(r'^electricity ', flags=re.IGNORECASE)

def _find_table_rect(blocks: Iterable[TextBlock], from_text: str, to_text: str) -> Rectangle:
    left = 0.0
    right = 0.0
    top = 0.0
    bottom = 0.0

    for block in blocks:
        if (block.text.startswith(from_text)):
            left = block.rect.left
            top = block.rect.top
            right = block.rect.right
        if (block.text.startswith(to_text)):
            bottom = block.rect.bottom

    if top == 0.0:
        raise ValueError('Can''t find upper boundary of the table')
    if bottom == 0.0:
        raise ValueError('Can''t find lower boundary of the table')

    return Rectangle(left, top, right, bottom)

def _transform_row(text: str) -> str:
    new_text = _RE_SPACES.sub(' ', text)

    # replace UNICODE MINUS with ASCII minus
    new_text = new_text.replace('−', '-')

    # First 'Tier 1' row contains 'Electricity' in the beginning of the row
    new_text = _RE_ELECTRICITY.sub('', new_text)

    return new_text



def read_table_rows(blocks: Iterable[TextBlock], from_text: str, to_text: str) -> list[str]:
    rows: list[str] = []

    table_rect = _find_table_rect(blocks, from_text, to_text)

    new_block = True
    text = ''
    for block in blocks:
        if block.in_rectangle(table_rect):
            block_text = block.text.replace('\n', ' ').strip()

            # split 'Basic charge' into it's own row
            basic_charge_index = block_text.find(_BASIC_CHARGE)
            if basic_charge_index >= 0:
                rows.append(_transform_row(block_text[:basic_charge_index]))
                block_text = block_text[basic_charge_index + _BASIC_CHARGE_OFFSET:].replace(' $ ', ' ')

            if new_block:
                text = block_text
            else:
                text += ' '
                text += block_text

            new_block = (math.isclose(block.rect.right, table_rect.right, rel_tol=0.01)
                or 'Taxes' in text)
            if new_block:
                rows.append(_transform_row(text))
                text = ''

    if text:
        rows.append(_transform_row(text))

    return rows
