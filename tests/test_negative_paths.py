import unittest

from src.arithmetic import add


class NegativePathTests(unittest.TestCase):
    def test_opposite_values_cancel(self):
        self.assertEqual(add(-7, 7), 0)

    def test_negative_operand_is_not_dropped(self):
        self.assertEqual(add(2, -3), -1)
