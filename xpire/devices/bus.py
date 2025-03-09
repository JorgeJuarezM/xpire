from typing import Dict

from xpire.devices.device import Device


class Bus:

    class Addresss:
        SHIFTER = 0x00
        P1_CONTROLLER = 0x01
        P2_CONTROLLER = 0x02
        DISABLED = 0xFF

    def __init__(self):
        self.devices: Dict[int, Device] = {}
        self.read_mapping = {
            0x01: self.Addresss.P1_CONTROLLER,
            0x02: self.Addresss.P2_CONTROLLER,
            0x03: self.Addresss.SHIFTER,
        }

        self.write_mapping = {
            0x02: self.Addresss.SHIFTER,
            0x04: self.Addresss.SHIFTER,
        }

    def add_device(self, address: int, device: Device):
        self.devices[address] = device

    def read(self, port: int) -> int:
        if port not in self.read_mapping:
            return 0x00

        address = self.read_mapping[port]
        if not address in self.devices:
            return 0x00

        return self.devices[address].read()

    def write(self, port: int, value: int):
        if port not in self.write_mapping:
            return

        address = self.write_mapping[port]
        if not address in self.devices:
            return

        self.devices[address].write(value, port)
