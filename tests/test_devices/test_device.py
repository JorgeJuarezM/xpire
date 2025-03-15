"""
Test class for Devices.
"""

import tempfile
import unittest
import unittest.mock

import pygame
from faker import Faker

from xpire.devices.device import Device

fake = Faker()


class TestSpaceInvadersScene(unittest.TestCase):
    def setUp(self):
        self.device = Device()


    def test_write(self):
        expected_value = 0x01
        self.device.write(expected_value)
        self.device._value = expected_value

    def test_read(self):
        expected_value = 0x01
        self.device._value = expected_value
        self.assertEqual(self.device.read(), expected_value)