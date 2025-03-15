from typing import Optional


class Device:

    _value = 0x00

    def write(self, value: int, port: Optional[int] = None):
        self._value = value

    def read(self) -> int:
        return self._value

    def reset(self):
        self._value = 0x00


class P1Controls(Device):
    def __init__(self):
        self._value = 0x08

    def write(self, value: int, port: Optional[int] = None):
        self._value |= value
        self._value |= 0x08


class Shifter(Device):
    def __init__(self):
        self._value = 0x00
        self._offset = 0x00

    def write(self, value, port: Optional[int] = None):
        if port == 0x02:
            self._offset = (value ^ 0xFF) & 0x07
        elif port == 0x04:
            self._value = (self._value >> 8) | (value << 7)
        else:
            raise Exception(f"Invalid port {port}")

    def read(self):
        return (self._value >> self._offset) & 0xFF
