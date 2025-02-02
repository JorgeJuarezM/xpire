"""
Utility functions for the CPU emulator.
"""

from memory import Memory


def load_program_into_memory(memory: Memory, program_path: str):
    """
    Load a program into memory from a file.

    This method reads the binary contents of a file specified by the
    program_path and loads it into memory starting at address 0x0000.
    Each byte from the file is stored sequentially in memory.

    Args:
        program_path: The path to the binary file containing the program to load.
    """

    with open(program_path, "rb") as f:
        i = 0
        while opcode := f.read(1):
            memory.memory[i] = int(opcode.hex(), 16)
            i += 1


def reset_value_if_overflow(value: int, max_size: int) -> int:
    return value & max_size
