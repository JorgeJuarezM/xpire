from typing import Callable

from xpire.exceptions import InvalidReadPort, InvalidWritePort


class Bus:

    class DeviceTypes:
        READ = 0
        WRITE = 1

    def __init__(self):
        self.readers = {}
        self.writers = {}

    # class Addresss:
    #     SHIFTER = 0x00
    #     P1_CONTROLLER = 0x01
    #     P2_CONTROLLER = 0x02
    #     DUMMY_DEVICE = 0xFF

    # def __init__(self):
    #     self.devices: Dict[int, Device] = {}
    #     self.read_mapping = {
    #         0x01: self.Addresss.P1_CONTROLLER,
    #         0x02: self.Addresss.P2_CONTROLLER,
    #         0x03: self.Addresss.SHIFTER,
    #     }

    #     self.write_mapping = {
    #         0x02: self.Addresss.SHIFTER,
    #         0x03: self.Addresss.DUMMY_DEVICE,
    #         0x04: self.Addresss.SHIFTER,
    #         0x05: self.Addresss.DUMMY_DEVICE,
    #         0x06: self.Addresss.DUMMY_DEVICE,
    #     }

    # def _read_device(self, address: int) -> int:
    #     if not address in self.devices:
    #         raise InvalidReadAddress(address)

    #     return self.devices[address].read()

    # def _write_device(self, address: int, value: int, port: int):
    #     if not address in self.devices:
    #         raise InvalidWriteAddress(address)

    #     self.devices[address].write(value, port)

    # def _get_read_port_address(self, port: int) -> int:
    #     if port not in self.read_mapping:
    #         raise InvalidReadPort(port)

    #     return self.read_mapping[port]

    # def _get_write_port_addresss(self, port: int) -> int:
    #     if port not in self.write_mapping:
    #         raise InvalidWritePort(port)

    #     return self.write_mapping[port]

    # def add_device(self, address: int, device: Device):
    #     self.devices[address] = device

    # def read(self, port: int) -> int:
    #     address = self._get_read_port_address(port)
    #     return self._read_device(address)

    # def write(self, port: int, value: int):
    #     address = self._get_write_port_addresss(port)
    #     self._write_device(address, value, port)

    def write(self, port: int, value: int):
        if port in self.writers:
            self.writers[port](value)
        else:
            raise InvalidWritePort(port)

    def read(self, port: int) -> int:
        if port in self.readers:
            return self.readers[port]()
        else:
            raise InvalidReadPort(port)

    def register_device(self, device_type: int, port: int, handler: Callable):
        if device_type == Bus.DeviceTypes.READ:
            self.readers[port] = handler
        elif device_type == Bus.DeviceTypes.WRITE:
            self.writers[port] = handler
