"""
Test class for Space Invaders Scene.
"""

import tempfile
import unittest
import unittest.mock

import pygame
from faker import Faker

from xpire.scenes.space_invaders import SpaceInvadersScene, frequency_ratio

fake = Faker()


class TestSpaceInvadersScene(unittest.TestCase):
    def setUp(self):
        self.scene = SpaceInvadersScene()

    def test_load_rom(self):
        temp = tempfile.NamedTemporaryFile(delete=False)
        memory_data = fake.binary(length=0xFFFF)
        with open(temp.name, "wb") as f:
            f.write(bytearray(memory_data))

        self.scene.load_rom(temp.name)
        for i in range(len(memory_data)):
            self.assertEqual(self.scene.cpu.memory[i], memory_data[i])
        self.assertEqual(len(self.scene.cpu.memory), 0x10000)

    def test_load_rom_not_found(self):
        with self.assertRaises(Exception):
            self.scene.load_rom(fake.file_path())

    def test_render(self):
        self.scene.cpu.memory = bytearray(fake.binary(length=0xFFFF))
        surface = self.scene.render()

        self.assertIsNotNone(surface)
        self.assertEqual(surface.get_size(), (224, 256))

    def test_handle_events_no_key_pressed(self):
        self.scene.p1_controller.write = unittest.mock.Mock()

        with unittest.mock.patch("pygame.key.get_pressed") as mock_get_pressed:
            mock_get_pressed.return_value = {
                pygame.K_c: False,
                pygame.K_RETURN: False,
                pygame.K_SPACE: False,
                pygame.K_LEFT: False,
                pygame.K_RIGHT: False,
            }
            self.scene.handle_events()
            self.scene.p1_controller.write.assert_not_called()

    def test_handle_events_coin_key_pressed(self):
        self.scene.p1_controller.write = unittest.mock.Mock()

        with unittest.mock.patch("pygame.key.get_pressed") as mock_get_pressed:
            mock_get_pressed.return_value = {
                pygame.K_c: True,
                pygame.K_RETURN: False,
                pygame.K_SPACE: False,
                pygame.K_LEFT: False,
                pygame.K_RIGHT: False,
            }
            self.scene.handle_events()
            self.scene.p1_controller.write.assert_called_with(0x01)

    def test_handle_events_start_key_pressed(self):
        self.scene.p1_controller.write = unittest.mock.Mock()

        with unittest.mock.patch("pygame.key.get_pressed") as mock_get_pressed:
            mock_get_pressed.return_value = {
                pygame.K_c: False,
                pygame.K_RETURN: True,
                pygame.K_SPACE: False,
                pygame.K_LEFT: False,
                pygame.K_RIGHT: False,
            }
            self.scene.handle_events()
            self.scene.p1_controller.write.assert_called_with(0x04)

    def test_handle_events_fire_key_pressed(self):
        self.scene.p1_controller.write = unittest.mock.Mock()

        with unittest.mock.patch("pygame.key.get_pressed") as mock_get_pressed:
            mock_get_pressed.return_value = {
                pygame.K_c: False,
                pygame.K_RETURN: False,
                pygame.K_SPACE: True,
                pygame.K_LEFT: False,
                pygame.K_RIGHT: False,
            }
            self.scene.handle_events()
            self.scene.p1_controller.write.assert_called_with(0x10)

    def test_handle_events_left_key_pressed(self):
        self.scene.p1_controller.write = unittest.mock.Mock()

        with unittest.mock.patch("pygame.key.get_pressed") as mock_get_pressed:
            mock_get_pressed.return_value = {
                pygame.K_c: False,
                pygame.K_RETURN: False,
                pygame.K_SPACE: False,
                pygame.K_LEFT: True,
                pygame.K_RIGHT: False,
            }
            self.scene.handle_events()
            self.scene.p1_controller.write.assert_called_with(0x20)

    def test_handle_events_right_key_pressed(self):
        self.scene.p1_controller.write = unittest.mock.Mock()

        with unittest.mock.patch("pygame.key.get_pressed") as mock_get_pressed:
            mock_get_pressed.return_value = {
                pygame.K_c: False,
                pygame.K_RETURN: False,
                pygame.K_SPACE: False,
                pygame.K_LEFT: False,
                pygame.K_RIGHT: True,
            }
            self.scene.handle_events()
            self.scene.p1_controller.write.assert_called_with(0x40)

    def test_update(self):
        self.scene.cpu.cycles = frequency_ratio + 1
        self.scene.cpu.execute_instruction = unittest.mock.Mock()
        self.scene.handle_events = unittest.mock.Mock()
        self.scene.handle_interrupts = unittest.mock.Mock()

        for _ in self.scene.update():
            self.scene.cpu.execute_instruction.assert_not_called()
            self.scene.handle_events.assert_called_once()
            self.scene.handle_interrupts.assert_called_once()
            break

    def test_handle_interrupts_not_enabled(self):
        self.scene.cpu.interrupts_enabled = False
        self.scene.cpu.execute_interrupt = unittest.mock.Mock()
        result = self.scene.handle_interrupts()

        self.assertFalse(result)
        self.scene.cpu.execute_interrupt.assert_not_called()

    def test_handle_interrupts_enabled(self):
        self.scene.cpu.interrupts_enabled = True
        self.scene.cpu.execute_interrupt = unittest.mock.Mock()
        result = self.scene.handle_interrupts()

        self.assertTrue(result)
        self.scene.cpu.execute_interrupt.assert_called_once()
