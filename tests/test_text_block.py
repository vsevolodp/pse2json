import unittest

from unittest import mock
from pse2json import text_block as tb


class RectangleTests(unittest.TestCase):

    def test_left_is_less_then_right(self):
        rect = tb.Rectangle(10, 1, 0, 2)

        self.assertLessEqual(rect.left, rect.right)

    def test_top_is_less_then_bottom(self):
        rect = tb.Rectangle(1, 10, 2, 0)

        self.assertLessEqual(rect.top, rect.bottom)

    def test_in_rectangle(self):
        inner_rect = tb.Rectangle(1, 1, 1, 1)
        outer_rect = tb.Rectangle(1, 1, 5, 5)

        result = inner_rect.in_rectangle(outer_rect)

        self.assertTrue(result)

        result = outer_rect.in_rectangle(inner_rect)

        self.assertFalse(result)

    def test_all_permutations(self):
        permutations = [
            ((1.0, 2.0), (1.0, 2.0), True),
            ((1.0, 2.0), (1.0, 3.0), True),
            ((1.0, 2.0), (2.0, 3.0), False),
            ((1.0, 2.0), (3.0, 4.0), False),
            ((1.0, 3.0), (1.0, 2.0), False),
            ((1.0, 3.0), (2.0, 3.0), False),
            ((1.0, 3.0), (2.0, 4.0), False),
            ((1.0, 4.0), (2.0, 3.0), False),
            ((2.0, 3.0), (1.0, 2.0), False),
            ((2.0, 3.0), (1.0, 3.0), True),
            ((2.0, 3.0), (1.0, 4.0), True),
            ((2.0, 4.0), (1.0, 3.0), False),
            ((3.0, 4.0), (1.0, 2.0), False),
        ]

        for x in permutations:
            for y in permutations:
                x_inner = x[0]
                y_inner = y[0]
                inner_rectangle = tb.Rectangle(x_inner[0], y_inner[0], x_inner[1], y_inner[1])

                x_outer = x[1]
                y_outer = y[1]
                outer_rectangle = tb.Rectangle(x_outer[0], y_outer[0], x_outer[1], y_outer[1])

                expected = x[2] and y[2]

                result = inner_rectangle.in_rectangle(outer_rectangle)

                self.assertEqual(result, expected)
                


class TextBlockTests(unittest.TestCase):

    def test_calls_rectangle_in_rectangle(self):
        rect1 = tb.Rectangle(1, 2, 3, 4)
        rect1.in_rectangle = mock.MagicMock(return_value = True)

        text_block = tb.TextBlock(rect1, None)

        rect2 = tb.Rectangle(2, 3, 4, 5) 

        result = text_block.in_rectangle(rect2)

        rect1.in_rectangle.assert_called_once_with(rect2)
        self.assertEqual(result, True)


if __name__ == '__main__':
    unittest.main()