from pse2json.text_block import Rectangle, TextBlock

# import PyMuPDF - python binding for MyPDF
import fitz


def read_text_blocks(file_name: str, page_index: int) -> list[TextBlock]:
    blocks: list(TextBlock) = []

    with fitz.open(file_name) as doc:
        page = doc.load_page(page_index)
        page_blocks = page.get_text('blocks')

        for page_block in page_blocks:
            left, top, right, bottom, text, *_ = page_block

            if top > bottom:
                top, bottom = bottom, top

            if left > right:
                left, right = right, left

            rect = Rectangle(left, top, right, bottom)
            block = TextBlock(rect, text)
            blocks.append(block)

    return blocks