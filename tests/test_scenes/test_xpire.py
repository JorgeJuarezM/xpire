import unittest

from xpire.scenes.xpire import XpireScene
from xpire.constants import Colors


class TestXpireScene(unittest.TestCase):
    def setUp(self):
        self.scene = XpireScene()

    def test_draw_line(self):
        self.scene.get_background_color = unittest.mock.Mock()
        self.scene.get_background_color.return_value = Colors.RED

        self.scene.drawLine(0)
        for i in range(self.scene.surface.get_width()):
            self.assertEqual(self.scene.surface.get_at((i, 0)), Colors.RED)
            self.assertNotEqual(self.scene.surface.get_at((i, 1)), Colors.RED)

        self.scene.get_background_color.assert_called_once()
