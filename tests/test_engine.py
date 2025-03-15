"""
Test class for Bus.
"""

import unittest
import unittest.mock

import pygame
from faker import Faker

from xpire.engine import GameManager

fake = Faker()


class MockScene:
    def __init__(self, surface):
        self.surface = surface

    def update(self):
        return self.surface


class TestEngine(unittest.TestCase):

    @unittest.mock.patch("pygame.init")
    @unittest.mock.patch("pygame.display.set_mode")
    def setUp(self, mock_set_mode, mock_init) -> None:
        self.surface = pygame.Surface((800, 600))

        mock_set_mode.return_value = self.surface
        mock_init.return_value = None

        self.engine = GameManager(scene=MockScene(surface=self.surface))

    @unittest.mock.patch("pygame.event.get")
    @unittest.mock.patch("pygame.display.update")
    def test_start(self, mock_update, mock_get):
        mock_update.return_value = None
        mock_get.return_value = []

        self.engine.scene.is_finished = unittest.mock.Mock()
        self.engine.scene.is_finished.return_value = True

        self.engine.start()

        mock_update.assert_called_once()
        mock_get.assert_called_once()
