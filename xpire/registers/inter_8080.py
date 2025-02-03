"""
Registers for the Intel 8080 CPU.

This module defines the registers used by the Intel 8080 CPU.
The registers are represented as enum values.
"""

from enum import Enum


class Registers(Enum):
    """Registers for the Intel 8080 CPU."""

    A = 0x00
    B = 0x01
    C = 0x02
    D = 0x03
    E = 0x04
    H = 0x05
    L = 0x06
