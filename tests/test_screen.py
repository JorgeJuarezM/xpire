"""
Test class for the Intel8080 CPU.
"""

import math
import unittest

from xpire.cpus.cpu import CPU
from xpire.screen import Screen

WHITE_COLOR = (255, 255, 255, 255)


class TestScreen(unittest.TestCase):
    """
    Test class for the Intel8080 CPU.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        self.cpu = CPU()

    def test_screen(self):
        """
        Test the screen rendering.
        """

        for i in range(0x2400, 0x4000):
            self.cpu.memory[i] = 0xFF if i % 2 == 0 else 0x00

        screen = Screen(width=224, height=256, title="Xpire", scale=3)
        screen.color_table = [WHITE_COLOR]
        screen.render(self.cpu)

        assert screen._screen.get_size() == (224, 256)

        counter = 0
        for x in range(0, screen._screen.get_width()):
            for y in range(0, screen._screen.get_height()):
                byte_index = math.floor(counter / 8)
                if byte_index % 2 == 1:
                    assert screen._screen.get_at((x, y)) == WHITE_COLOR
                counter += 1
