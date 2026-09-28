import unittest

from src.arithmetic import add


class ArithmeticTests(unittest.TestCase):
    def test_adds_positive_values(self):
        self.assertEqual(add(2, 3), 5)

    def test_adds_negative_values(self):
        self.assertEqual(add(-2, -3), -5)

    def test_zero_is_identity(self):
        self.assertEqual(add(7, 0), 7)


if __name__ == '__main__':
    unittest.main()
