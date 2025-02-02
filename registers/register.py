from typing import Dict


class RegisterManager:
    """
    A class that manages the registers of the CPU.

    The RegisterManager class provides methods to access and modify the registers
    of the CPU. The registers are stored in a dictionary, where the keys are the
    register identifiers and the values are the register values.
    """

    registers: Dict[int, int]
    """
    A dictionary that stores the registers of the CPU. The keys are the register
    opcodes and the values are the register values.
    """

    def __init__(self) -> None:
        """
        Initialize a new RegisterManager object.

        This constructor initializes an empty dictionary to store the registers.
        """
        self.registers = {}

    def __getitem__(self, opcode: int) -> int:
        """
        Get the value of the register with the given opcode.

        Args:
            opcode (int): The opcode of the register to get.

        Returns:
            int: The value of the register.
        """
        return self.registers[opcode]

    def __setitem__(self, opcode: int, value: int) -> None:
        """
        Set the value of the register with the given opcode.

        Args:
            opcode (int): The opcode of the register to set.
            value (int): The value to set the register to.
        """
        self.registers[opcode] = value
