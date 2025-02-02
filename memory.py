"""
Memory module for the CPU emulator.

This module defines the Memory class, which represents the memory
of the CPU emulator. It provides methods to read and write memory
cells, and to dump the memory contents.

The Memory class is initialized with an empty dictionary to store
the memory cells. The memory is represented as a dictionary where
the keys are memory addresses and the values are memory cells.
"""

from constants import FULL_WORD, BYTE_SIZE, DEFAULT_MEMORY_VALUE
from exceptions import InvalidMemoryAddress, InvalidMemoryValue


class Memory:
    """
    Memory class for the CPU emulator.
    """

    size: int

    def __init__(self, size: int = FULL_WORD):
        """
        Initialize a new Memory object.

        This method initializes a new Memory object by setting up an empty
        dictionary to store the memory cells.
        """
        self.memory = {}
        self.size = size

    def __setitem__(self, addr: int, value: int) -> None:
        """
        Set the value at the specified memory address.

        This method assigns the given value to the memory cell at the
        specified address (key).

        Args:
            key: The memory address where the value is to be stored.
            value: The value to store at the specified memory address.

        Raises:
            Exception: If the memory address is out of bounds.
            Exception: If the value is too large to fit in a byte.
        """
        if addr > self.size:
            raise InvalidMemoryAddress(addr)

        if value.bit_length() > BYTE_SIZE:
            raise InvalidMemoryValue(addr, value)

        self.memory[addr] = value

    def __getitem__(self, addr: int) -> int:
        """
        Get the value at the specified memory address.

        This method returns the value stored at the specified memory address.

        Args:
            addr: The memory address from which to retrieve the value.

        Returns:
            The value stored at the specified memory address.
        """
        if addr > self.size:
            raise InvalidMemoryAddress(addr)

        return self.memory[addr] if addr in self.memory else DEFAULT_MEMORY_VALUE

    def __len__(self):
        return self.size

    def items(self):
        """
        Return an iterator over the memory cells.

        This method returns an iterator over the memory cells. The iterator
        produces tuples where the first element is the memory address and the
        second element is the value stored at that address.

        Returns:
            An iterator over the memory cells.
        """
        return self.memory.items()

    def dump(self):
        """
        Return a string representation of the memory dump.

        This method returns a string containing a memory dump. The dump is
        formatted as a sequence of lines, each line showing the memory address
        and the value stored at that address. The address is displayed in
        hexadecimal format with four digits and the value is displayed in
        hexadecimal format with two digits.

        Returns:
            A string containing a memory dump.
        """
        elements = []
        for k, v in self.memory.items():
            elements.append(f"0x{k:04x}: 0x{v:02x}")
        return "\n".join(elements)

    def max_address(self) -> int:
        """
        Return the maximum address in the memory.

        This method returns the maximum address in the memory, which is the
        highest address that can be used to store a value.

        Returns:
            The maximum address in the memory.
        """
        return self.size
