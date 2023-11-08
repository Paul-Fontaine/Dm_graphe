import unittest
from main import *


class MyTestCase(unittest.TestCase):
    def test_conversions(self):
        self.assertEqual(index_2_coords(14), (1, 4))
        self.assertEqual(index_2_coords(0), (0, 0))
        self.assertEqual(index_2_coords(99), (9, 9))

        self.assertEqual(coords_2_index((2, 7)), 27)
        self.assertEqual(coords_2_index((0, 0)), 0)
        self.assertEqual(coords_2_index((9, 9)), 99)

        self.assertEqual(coords_2_str((4, 6)), "(4, 6)")


if __name__ == '__main__':
    unittest.main()
