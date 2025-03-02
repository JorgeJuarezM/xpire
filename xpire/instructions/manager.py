"""
InstructionManager class.

This class provides a way to manage instructions. It allows to add an instruction
with its opcode and registers, and to execute an instruction with its opcode.

The instructions are stored in a dictionary where the keys are the opcodes and the
values are tuples containing the instruction handler and the registers.
"""

from typing import Callable, List, Optional, Tuple

from xpire.cpus.abstract import AbstractCPU


class InstructionManager:
    """InstructionManager class."""

    instructions: dict[int, Tuple[Callable, List[str]]] = {}

    @classmethod
    def add_instruction(
        cls, opcode: int, registers: Optional[List[str]] = None
    ) -> Callable:
        """
        Add an instruction with its opcode and registers.

        Args:
            opcode (int): The opcode of the instruction.
            registers (Optional[List[str]], optional): The registers of the instruction.
                Defaults to None.

        Returns:
            Callable: The decorator.
        """

        def wrapper(func):
            """
            Wrapper function.

            Args:
                func (Callable): The instruction handler.

            Returns:
                Callable: The decorated function.
            """
            if opcode in cls.instructions:
                raise Exception(f"Duplicate opcode: 0x{opcode:02x}")
            cls.instructions[opcode] = func, registers or []
            return func

        return wrapper

    @classmethod
    def execute(cls, opcode: int, cpu: AbstractCPU) -> None:
        """
        Execute an instruction.

        Args:
            opcode (int): The opcode of the instruction.
            cpu (AbstractCPU): The CPU object.

        Raises:
            Exception: If the opcode is unknown.
        """
        if opcode not in cls.instructions:
            raise Exception(f"Unknown opcode: 0x{opcode:02x}")

        handler, registers = cls.instructions[opcode]
        handler(cpu, *registers)
