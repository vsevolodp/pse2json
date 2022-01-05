import unittest

import fitz

from unittest import mock

from pse2json import pdf_text_block_reader as ptbr
from pse2json import text_block


class PdfTextBlockReaderTests(unittest.TestCase):
    def setup_mock(self, fitz_open_mock: mock.Mock, blocks: list[tuple]) -> tuple:
        doc_mock = fitz_open_mock().__enter__()
        page_mock = doc_mock.load_page()
        page_mock.get_text.return_value = blocks
        return (doc_mock, page_mock)

    @mock.patch('fitz.open')
    def test_read_text_blocks(self, fitz_open_mock):

        file_name = 'file.pdf'
        page_index = 1

        doc_mock, page_mock = self.setup_mock(
            fitz_open_mock,
            [(1, 2, 3, 4, 'text', 5, 6)]
        )

        blocks = ptbr.read_text_blocks(file_name, page_index)

        fitz_open_mock.assert_called_with(file_name)
        doc_mock.load_page.assert_called_with(page_index)
        page_mock.get_text.assert_called_with('blocks')

        self.assertEqual(1, len(blocks))
        self.assertIsInstance(blocks[0], text_block.TextBlock)
        self.assertEqual(text_block.Rectangle(1, 2, 3, 4), blocks[0].rect)
        self.assertEqual('text', blocks[0].text)

    @mock.patch('fitz.open')
    def test_inverted_x(self, fitz_open_mock):
        doc_mock, page_mock = self.setup_mock(
            fitz_open_mock,
            [(3, 2, 1, 4, 'text', 5, 6)]
        )

        blocks = ptbr.read_text_blocks('file.pdf', 0)

        self.assertEqual(1, len(blocks))
        self.assertEqual(text_block.Rectangle(1, 2, 3, 4), blocks[0].rect)

    @mock.patch('fitz.open')
    def test_inverted_y(self, fitz_open_mock):
        doc_mock, page_mock = self.setup_mock(
            fitz_open_mock,
            [(1, 4, 3, 2, 'text', 5, 6)]
        )

        blocks = ptbr.read_text_blocks('file.pdf', 0)

        self.assertEqual(1, len(blocks))
        self.assertEqual(text_block.Rectangle(1, 2, 3, 4), blocks[0].rect)


if __name__ == '__main__':
    unittest.main()