import unittest


class ColorBaseTest(unittest.TestCase):

    def _test_colors(self, color):
        self.assertIsInstance(color, tuple)
        self.assertEqual(len(color), 3)

        for c in color:
            self.assertIsInstance(c, int)
            self.assertGreaterEqual(c, 0)
            self.assertLessEqual(c, 255)
