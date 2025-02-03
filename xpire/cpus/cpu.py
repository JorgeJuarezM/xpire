"""
CPU module for the CPU emulator.

This module defines the CPU class, which represents the CPU emulator.
It provides methods to read and write memory cells, and to execute
instructions.
"""

import threading
from typing import Callable, Optional

from xpire.cpus.abstract import AbstractCPU
from xpire.decorators import increment_program_counter
from xpire.exceptions import SystemHalt
from xpire.memory import Memory
from xpire.registers.register import RegisterManager
from xpire.utils import join_bytes


class InstructionSet:
    instructions = {}

    @classmethod
    def add_instruction(cls, opcode: int, registers: Optional[list] = []) -> Callable:
        def wrapper(func):
            cls.instructions[opcode] = func, registers
            return func

        return wrapper

    @classmethod
    def execute(cls, opcode: int, cpu: AbstractCPU):
        if opcode not in cls.instructions:
            raise Exception(f"Unknown opcode: 0x{opcode:02x}")

        handler, registers = cls.instructions[opcode]
        handler(cpu, *registers)


class CPU(threading.Thread, AbstractCPU):
    """
    CPU class for the CPU emulator.

    This class represents the CPU emulator.
    It provides methods to read and write memory cells, and to execute
    instructions.
    """

    instructions: dict[int, Callable]
    exception: Exception
    registers: RegisterManager

    def __init__(self, memory: Memory) -> None:
        """
        Initialize a new CPU object.

        This method initializes a new CPU object by setting the memory object and
        initializing the registers to zero. It also sets the program counter to 0x00
        and the stack pointer to 0xFF.

        The CPU object starts a new thread to execute instructions.

        Args:
            memory (Memory): The memory object to use for the CPU.
        """
        threading.Thread.__init__(self)
        self.close_event = threading.Event()

        self.exception = None

        self.memory = memory
        self.registers = RegisterManager()

        self.SP = 0x0000
        self.PC = 0x0000

        self.instructions = {
            0x00: self._no_operation,
            0x76: self._system_halt,
        }

    @InstructionSet.add_instruction(0x00, [])
    def _no_operation(self) -> None:
        """
        No operation.

        This instruction does nothing. It is used to indicate
        no operation should be performed.
        """

    @InstructionSet.add_instruction(0x76, [])
    def _system_halt(self) -> None:
        """
        Halt the system by raising a SystemHalt exception.

        This method is used to signal to the emulator that the program
        has finished executing by raising a SystemHalt exception.
        """
        raise SystemHalt()

    def add_instruction(self, opcode, func: Callable) -> None:
        """
        Add a new instruction to the CPU's instruction set.

        Args:
            opcode (int): The opcode for the instruction.
            func (Callable): The function to call when the instruction is executed.
        """
        self.instructions[opcode] = func

    def run(self) -> None:
        """
        Execute the CPU instructions in a loop until a halt condition is met.

        This method repeatedly calls the `tick` method to execute instructions
        until the `close_event` is set or an exception is raised.
        """
        while not self.close_event.is_set() and self.tick():
            continue

    def tick(self) -> bool:
        """
        Execute a single instruction and handle exceptions.

        This method fetches and executes the next instruction. If an exception
        occurs during execution, it checks if the exception is not a SystemHalt,
        and stores it in the `exception` attribute. The method returns False if
        an exception other than SystemHalt is raised, indicating an issue with
        execution; otherwise, it returns True.

        Returns:
            bool: True if the instruction executed successfully, False if an
                exception was encountered.
        """
        try:
            self.execute_instruction()
        except Exception as e:
            if not isinstance(e, SystemHalt):
                self.exception = e

            return False

        return True

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
        h_addr = self.read_memory_byte(addr)
        l_addr = self.read_memory_byte(addr + 0x01)
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

    def has_instruction(self, opcode) -> bool:
        """
        Check if the given opcode has an associated instruction.

        Args:
            opcode (int): The opcode to check.

        Returns:
            bool: True if the opcode has an associated instruction, False otherwise.
        """
        return opcode in self.instructions

    def execute_instruction(self) -> None:
        """
        Execute the instruction at the current program counter.

        This method fetches a byte from memory, checks if the opcode is known,
        and executes the associated instruction. If the opcode is unknown,
        an exception is raised.

        Returns:
            None
        """
        opcode = self.fetch_byte()
        # if self.has_instruction(opcode):
        #     self.instructions[opcode]()
        # else:
        #     raise Exception(f"Unknown opcode: 0x{opcode:02x}")
        InstructionSet.execute(opcode, self)

    def decrement_stack_pointer(self) -> None:
        """
        Decrement the stack pointer (SP) by one, wrapping around if necessary.

        This method adjusts the stack pointer by incrementing it by one and
        ensures it does not exceed the maximum addressable memory. The resulting
        value is wrapped using a bitwise AND with the maximum memory address,
        effectively decrementing the stack pointer with wrapping behavior.
        """
        new_value = self.SP - 0x02
        if new_value < 0x00:
            new_value = 0xFFFF + new_value + 0x0001

        self.SP = new_value & 0xFFFF
        return None
