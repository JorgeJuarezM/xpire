import unittest

from xpire.constants import Colors
from xpire.scenes.xpire import XpireScene


class TestXpireScene(unittest.TestCase):
    def setUp(self):
        self.scene = XpireScene()

    def _test_colors(self, color):
        self.assertIsInstance(color, tuple)
        self.assertEqual(len(color), 3)

        for c in color:
            self.assertIsInstance(c, int)
            self.assertGreaterEqual(c, 0)
            self.assertLessEqual(c, 255)

    def test_draw_line(self):
        self.scene.get_background_color = unittest.mock.Mock()
        self.scene.get_background_color.return_value = Colors.RED

        self.scene.drawLine(0)
        for i in range(self.scene.surface.get_width()):
            self.assertEqual(self.scene.surface.get_at((i, 0)), Colors.RED)
            self.assertNotEqual(self.scene.surface.get_at((i, 1)), Colors.RED)

        self.scene.get_background_color.assert_called_once()

    def test_get_ink_color(self):
        color = self.scene.get_ink_color()
        self._test_colors(color)

    def test_get_background_color(self):
        color = self.scene.get_background_color()
        self._test_colors(color)

    def test_get_background_color__out_of_bounds(self):
        self.scene.cpu.memory[0x4000] = 0xFF
        color = self.scene.get_background_color()
        self._test_colors(color)
