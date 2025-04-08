class Device:

    _value = 0x00

    def write(self, value: int):
        self._value = value

    def read(self) -> int:
        return self._value

    def reset(self):
        self._value = 0x00


class DummyDevice(Device):

    def write(self, value: int):
        pass

    def read(self) -> int:
        return 0


class P1Controls(Device):
    def __init__(self):
        self._value = 0x08

    def write(self, value: int):
        self._value |= value
        self._value |= 0x08

    def reset(self):
        self._value = 0x08


class P2Controls(Device):
    def __init__(self):
        self._value = 0x04


class DummyInput(Device):
    def __init__(self):
        self._value = 0b10001111


class Shifter(Device):
    def __init__(self):
        self._value = 0x00
        self._offset = 0x00

    def write_offset(self, offset: int):
        self._offset = (offset ^ 0xFF) & 0x07

    def write_value(self, value: int):
        self._value = (self._value >> 8) | (value << 7)

    def read(self):
        return (self._value >> self._offset) & 0xFF
