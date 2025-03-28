import unittest

from tests.base.base import ColorBaseTest
from xpire.constants import Colors
from xpire.scenes.xpire import XpireScene


class TestXpireScene(ColorBaseTest):
    def setUp(self):
        self.scene = XpireScene()

    def test_draw_line(self):
        self.scene.get_background_color = unittest.mock.Mock()
        self.scene.get_background_color.return_value = Colors.RED

        self.scene.draw_line(0)
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
