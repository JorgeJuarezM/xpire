"""
Test class for Bus.
"""

import unittest
import unittest.mock

from faker import Faker

from xpire.devices.bus import Bus, Device
from xpire.exceptions import InvalidReadPort, InvalidWritePort

fake = Faker()


class MockDevice:
    """Mock device for testing."""


class TestBus(unittest.TestCase):

    def setUp(self) -> None:
        self.bus = Bus()
        self.bus.devices[Bus.Addresss.DUMMY_DEVICE] = Device()

    def test_add_device(self) -> None:
        self.bus.add_device(Bus.Addresss.SHIFTER, MockDevice())
        self.assertEqual(len(self.bus.devices), 2)
        self.assertIsInstance(self.bus.devices[Bus.Addresss.SHIFTER], MockDevice)

    @unittest.mock.patch.object(Device, "read")
    def test_read(self, mock_read) -> None:
        read_value = fake.random_int(min=0, max=255)
        port_to_read = 0xFF  # Dummy device

        mock_read.return_value = read_value
        self.bus.read_mapping[port_to_read] = Bus.Addresss.DUMMY_DEVICE

        result = self.bus.read(port_to_read)

        self.assertEqual(result, read_value)
        mock_read.assert_called_once()

    def test_write(self) -> None:
        port_to_write = 0x03  # Dummy device
        value_to_write = fake.random_int(min=0, max=255)

        self.bus.write(port_to_write, value_to_write)
        self.assertEqual(
            self.bus.devices[Bus.Addresss.DUMMY_DEVICE]._value,
            value_to_write,
        )

    def test_read_invalid_port(self):
        with self.assertRaises(InvalidReadPort):
            self.bus.read(0xFF)

    def test_write_invalid_port(self):
        with self.assertRaises(InvalidWritePort):
            self.bus.write(0xFF, 0xFF)
