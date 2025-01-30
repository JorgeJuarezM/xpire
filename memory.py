"""
Memory module for the CPU emulator.

This module defines the Memory class, which represents the memory
of the CPU emulator. It provides methods to read and write memory
cells, and to dump the memory contents.

The Memory class is initialized with an empty dictionary to store
the memory cells. The memory is represented as a dictionary where
the keys are memory addresses and the values are memory cells.
"""


class Memory:
    """
    Memory class for the CPU emulator.
    """

    def __init__(self):
        """
        Initialize a new Memory object.

        This method initializes a new Memory object by setting up an empty
        dictionary to store the memory cells.
        """
        self.memory = {}

    def __setitem__(self, key, value):
        """
        Set the value at the specified memory address.

        This method assigns the given value to the memory cell at the
        specified address (key).

        Args:
            key: The memory address where the value is to be stored.
            value: The value to store at the specified memory address.
        """

        self.memory[key] = value

    def __getitem__(self, addr: int) -> int:
        """
        Get the value at the specified memory address.

        This method returns the value stored at the specified memory address.

        Args:
            addr: The memory address from which to retrieve the value.

        Returns:
            The value stored at the specified memory address.
        """
        return self.memory[addr]

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

    def fetch(self, addr: int) -> int:
        """
        Retrieve a byte from memory at the specified address.

        This method returns the value stored at the given memory address.
        If the address does not exist in the memory, it returns 0x00.

        Args:
            addr: The memory address from which to retrieve the value.

        Returns:
            int: The value stored at the specified memory address, or 0x00 if not found.
        """

        return self.memory[addr] if addr in self.memory else 0x00
