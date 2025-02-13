"""
Test class for the Intel8080 CPU.
"""

import unittest

from xpire.cpus.cpu import CPU
from xpire.memory import Memory
from xpire.screen import Screen

WHITE_COLOR = (255, 255, 255)


class TestIntel8080(unittest.TestCase):
    """
    Test class for the Intel8080 CPU.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        self.memory = Memory()
        self.cpu = CPU(memory=self.memory)

    def test_screen(self):
        """
        Test the screen rendering.
        """

        for i in range(0x2400, 0x4000):
            self.memory[i] = 0xFF

        screen = Screen(width=224, height=256, title="Xpire", scale=3)
        screen.color_table = [WHITE_COLOR]
        screen.render(self.cpu)

        assert screen._screen.get_size() == (224, 256)
        for i in range(0, 256):
            assert screen._screen.get_at((10, i)) == WHITE_COLOR
