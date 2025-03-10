"""
Test class for Bus.
"""

import unittest
import unittest.mock

from faker import Faker

from xpire.devices.bus import Bus

fake = Faker()


class MockDevice:
    """Mock device for testing."""


class TestBus(unittest.TestCase):

    def setUp(self) -> None:
        self.bus = Bus()
        self.bus.devices[Bus.Addresss.DUMMY_DEVICE] = MockDevice()

    def test_add_device(self) -> None:
        self.bus.add_device(Bus.Addresss.SHIFTER, MockDevice())
        self.assertEqual(len(self.bus.devices), 2)
        self.assertIsInstance(self.bus.devices[Bus.Addresss.SHIFTER], MockDevice)

    @unittest.mock.patch.object(Bus, "_read_device")
    @unittest.mock.patch.object(Bus, "_get_read_port_addresss")
    def test_read(
        self,
        mocked_get_read_port_addresss: unittest.mock.Mock,
        mocked_read: unittest.mock.Mock,
    ) -> None:
        read_value = fake.random_int(min=0, max=255)
        expected_address = fake.random_int(min=0, max=255)
        expected_port = fake.random_int(min=0, max=255)

        mocked_get_read_port_addresss.return_value = expected_address
        mocked_read.return_value = read_value

        result = self.bus.read(expected_port)

        self.assertEqual(result, read_value)
        mocked_read.assert_called_once_with(expected_address)
        mocked_get_read_port_addresss.assert_called_once_with(expected_port)

    @unittest.mock.patch.object(Bus, "_write_device")
    @unittest.mock.patch.object(Bus, "_get_write_port_addresss")
    def test_write(
        self,
        mocked_get_write_port_addresss: unittest.mock.Mock,
        mocked_write: unittest.mock.Mock,
    ) -> None:
        write_value = fake.random_int(min=0, max=255)
        expected_port = fake.random_int(min=0, max=255)
        expected_address = fake.random_int(min=0, max=255)

        mocked_get_write_port_addresss.return_value = expected_address
        mocked_write.return_value = None

        self.bus.write(expected_port, write_value)

        mocked_write.assert_called_once_with(
            expected_address,
            write_value,
            expected_port,
        )
        mocked_get_write_port_addresss.assert_called_once_with(expected_port)
