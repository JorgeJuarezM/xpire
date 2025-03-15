"""
Test class for Devices.
"""

import unittest
import unittest.mock

from faker import Faker

from xpire.devices.device import Device, P1Controls, Shifter

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

    def test_p1_controller(self):
        write_value = 0x01
        expected_value = write_value | 0x08
        p1_controller = P1Controls()
        p1_controller.write(expected_value)
        self.assertEqual(p1_controller.read(), expected_value)

    def test_shifter(self):
        write_value = fake.pyint(min_value=0, max_value=255)
        write_offset = fake.pyint(min_value=0, max_value=7)
        expected_value = (write_value << write_offset) & 0xFF
        shifter = Shifter()

        shifter.write(write_offset, 0x02)  # write to offset
        shifter.write(write_value, 0x04)  # write to value
        self.assertEqual(shifter.read(), expected_value)

    def test_shifter_invalid_port(self):
        shifter = Shifter()
        with self.assertRaises(Exception):
            shifter.write(0x01, 0x05)
