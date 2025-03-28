"""
Test class for Space Invaders Scene.
"""

import tempfile
import unittest
import unittest.mock

import pygame
from faker import Faker

from tests.base.base import ColorBaseTest
from xpire.constants import Colors
from xpire.scenes.space_invaders import SpaceInvadersScene

fake = Faker()


class TestSpaceInvadersScene(ColorBaseTest):

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

    @unittest.mock.patch("xpire.scenes.space_invaders.CYCLES_PER_LINE", 1)
    @unittest.mock.patch("xpire.scenes.space_invaders.SCREEN_HEIGHT", 1)
    def test_update(self):
        def mock_execute_instruction():
            self.scene.cpu.cycles += 1

        self.scene.cpu.execute_instruction = mock_execute_instruction
        self.scene.handle_events = unittest.mock.Mock()
        self.scene.handle_interrupts = unittest.mock.Mock()
        self.scene.draw_line = unittest.mock.Mock()

        self.scene.update()
        self.scene.handle_events.assert_called_once()
        self.scene.handle_interrupts.assert_called_once()
        self.scene.draw_line.assert_called_once()

    def test_handle_interrupts(self):
        self.scene.cpu.execute_interrupt = unittest.mock.Mock()

        self.scene.handle_interrupts(line_number=95)  # Interrupt on line 96
        self.scene.cpu.execute_interrupt.assert_called_once_with(0xCF)

        self.scene.handle_interrupts(line_number=223)  # Interrupt on line 224
        self.scene.cpu.execute_interrupt.assert_called_with(0xD7)

    def test_draw_line(self):
        self.scene.get_ink_color = unittest.mock.Mock()
        self.scene.get_ink_color.return_value = Colors.RED

        self.scene.cpu.memory[0x2400:0x2420] = [0xFF] * 0x20
        self.scene.draw_line(0)
        for i in range(self.scene.surface.get_width()):
            self.assertEqual(self.scene.surface.get_at((i, 0)), Colors.RED)
            self.assertNotEqual(self.scene.surface.get_at((i, 1)), Colors.RED)

    def test_get_ink_color(self):
        color = self.scene.get_ink_color()
        self._test_colors(color)
