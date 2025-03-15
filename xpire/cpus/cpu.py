"""
CPU module for the CPU emulator.

This module defines the CPU class, which represents the CPU emulator.
It provides methods to read and write memory cells, and to execute
instructions.
"""

import xpire.instructions.common as OPCodes
from xpire.cpus.abstract import AbstractCPU
from xpire.decorators import increment_program_counter
from xpire.devices.bus import Bus
from xpire.exceptions import SystemHalt
from xpire.flags import FlagsManager
from xpire.instructions.manager import InstructionManager as manager
from xpire.registers.intel_8080 import Registers
from xpire.utils import join_bytes


class CPU(AbstractCPU):
    """
    CPU class for the CPU emulator.

    This class represents the CPU emulator.
    It provides methods to read and write memory cells, and to execute
    instructions.
    """

    PC: int
    SP: int

    halted: bool
    interrupts_enabled: bool

    cycles: int

    memory: bytearray
    registers: Registers

    def __init__(self) -> None:
        """
        Initialize a new CPU object.

        This method initializes a new CPU object by setting the memory object and
        initializing the registers to zero. It also sets the program counter to 0x00
        and the stack pointer to 0xFF.

        The CPU object starts a new thread to execute instructions.
        """
        self.memory = bytearray(0x10000)
        self.registers = Registers()
        self.flags = {}

        self.SP = 0x0000
        self.PC = 0x0000

        self.cycles = 0x00
        self.interrupts_enabled = False
        self.halted = False

        self.flags = FlagsManager()
        self.bus = Bus()

    def execute_instruction(self) -> None:
        """
        Execute a single instruction.

        This method fetches and executes the next instruction. If an exception
        occurs during execution, it checks if the exception is a SystemHalt.
        If its not, it raises the exception.

        Returns:
            None
        """
        try:
            opcode = self.fetch_byte()
            manager.execute(opcode, self)
        except SystemHalt:
            self.halted = True
            return

    def execute_interrupt(self, opcode: int) -> None:
        manager.execute(opcode, self)
        self.interrupts_enabled = False

    @increment_program_counter()
    def fetch_byte(self) -> int:
        """
        Fetch a byte from memory at the current program counter (PC) and
        increment the PC by one after the fetch.

        Returns:
            int: The value of the fetched byte.
        """
        return self.read_memory_byte(self.PC)

    def fetch_word(self) -> int:
        """
        Fetch a word (two bytes) from memory at the current program counter (PC).

        This method fetches two consecutive bytes from memory, combining them
        into a single 16-bit word. The PC is incremented by two after fetching
        the word. The low byte is fetched first, followed by the high byte, and
        they are combined into a word with the high byte shifted to the left.

        Returns:
            int: The value of the fetched word.
        """
        addr_l = self.fetch_byte()
        addr_h = self.fetch_byte()
        return join_bytes(addr_h, addr_l)

    def read_memory_byte(self, addr: int) -> int:
        """
        Read a byte from memory at the specified address.

        This method retrieves a byte from the memory at the given
        address. The address is masked with the maximum address
        to ensure it is within valid bounds.

        Args:
            addr (int): The memory address to read the byte from.

        Returns:
            int: The byte value stored at the specified memory address.
        """
        return self.memory[addr & 0xFFFF]

    def read_memory_word_bytes(self, addr: int) -> tuple[int, int]:
        """
        Fetch two bytes from memory at the given address and return them as a tuple of two values.

        The first value in the tuple is the high byte of the word and the second value is the low byte.

        Args:
            addr (int): The address to fetch the word from.

        Returns:
            tuple[int, int]: The fetched word as a tuple of two values.
        """
        l_addr = self.read_memory_byte(addr)
        h_addr = self.read_memory_byte(addr + 0x01)
        return h_addr, l_addr

    def read_memory_word(self, addr: int) -> int:
        """
        Read a word (two bytes) from memory at the specified address.

        This method retrieves a 16-bit word from the memory at the given
        address. The word is composed of two bytes: the high byte and the
        low byte. The high byte is shifted to the left by 8 bits and
        combined with the low byte to form the word.

        Args:
            addr (int): The memory address from which to read the word.

        Returns:
            int: The word value stored at the specified memory address.
        """
        h_addr, l_addr = self.read_memory_word_bytes(addr)
        return join_bytes(h_addr, l_addr)

    def decrement_stack_pointer(self) -> None:
        """
        Decrement the stack pointer (SP) by one, wrapping around if necessary.

        This method adjusts the stack pointer by incrementing it by one and
        ensures it does not exceed the maximum addressable memory. The resulting
        value is wrapped using a bitwise AND with the maximum memory address,
        effectively decrementing the stack pointer with wrapping behavior.
        """
        new_value = self.SP - 0x02
        self.SP = new_value & 0xFFFF
        return None

    @manager.add_instruction(OPCodes.NOP)
    def exec_no_operation(self) -> None:
        """
        No operation.

        This instruction does nothing. It is used to indicate
        no operation should be performed.
        """
        self.cycles += 4

    @manager.add_instruction(OPCodes.HLT)
    def raise_system_halt(self) -> None:
        """
        Halt the system by raising a SystemHalt exception.

        This method is used to signal to the emulator that the program
        has finished executing by raising a SystemHalt exception.
        """
        raise SystemHalt()
