"""
Registers for the Intel 8080 CPU.

This module defines the registers used by the Intel 8080 CPU.
The registers are represented as enum values.
"""

from xpire.utils import join_bytes, split_word


class Registers:
    A = 0x00
    B = 0x01
    C = 0x02
    D = 0x03
    E = 0x04
    H = 0x05
    L = 0x06

    def __init__(self):
        self.A = 0x00
        self.B = 0x00
        self.C = 0x00
        self.D = 0x00
        self.E = 0x00
        self.H = 0x00
        self.L = 0x00

    @property
    def BC(self):
        return join_bytes(self.B, self.C)

    @BC.setter
    def BC(self, value):
        self.B, self.C = split_word(value)

    @property
    def DE(self):
        return join_bytes(self.D, self.E)

    @DE.setter
    def DE(self, value):
        self.D, self.E = split_word(value)

    @property
    def HL(self):
        return join_bytes(self.H, self.L)

    @HL.setter
    def HL(self, value):
        self.H, self.L = split_word(value)

    def __getitem__(self, register: str):
        return getattr(self, register, 0x00)

    def __setitem__(self, register: str, value: int):
        setattr(self, register, value)
