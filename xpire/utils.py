"""
Utility functions for the CPU emulator.
"""

from xpire.memory import Memory


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


def join_bytes(high_byte: int, low_byte: int) -> int:
    """
    Join two bytes into a 16-bit word.

    This method takes two bytes and joins them into a 16-bit word by
    shifting the high byte left by 8 bits and ORing it with the low byte.

    Returns:
        int: The joined 16-bit word.
    """
    return (high_byte << 0x08) | low_byte


def split_word(word: int) -> tuple[int, int]:
    """
    Split a 16-bit word into two bytes.

    This method takes a 16-bit word and splits it into two bytes: the high byte
    and the low byte. The high byte is the result of shifting the word right by
    8 bits and masking the result with 0xFF, and the low byte is the result of
    masking the word with 0xFF.

    Args:
        word (int): The 16-bit word to split.

    Returns:
        tuple[int, int]: A tuple containing the high byte and low byte of the
        input word.
    """
    return (word >> 0x08) & 0xFF, word & 0xFF


def increment_bytes_pair(high_byte: int, low_byte: int) -> tuple[int, int]:
    """
    Increment a 16-bit word represented as two bytes by one.

    This method takes two bytes representing a 16-bit word and increments
    the word by one. The result is returned as a tuple of two bytes: the
    high byte and the low byte.
    """
    value = join_bytes(high_byte, low_byte)
    value += 0x01
    value = reset_value_if_overflow(value, 0xFFFF)
    return split_word(value)
