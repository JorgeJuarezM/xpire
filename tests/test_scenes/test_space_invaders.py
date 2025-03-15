"""
Test class for Spàce Invaders Scene.
"""

import tempfile
import unittest
import unittest.mock

from faker import Faker

from xpire.scenes.space_invaders import SpaceInvadersScene

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
