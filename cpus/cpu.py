import threading
import time
from tracemalloc import Frame
from memory import Memory
from exceptions import SystemHalt
from typing import Callable
from decorators import increment_program_counter
from cpus.abstract import AbstractCPU
from registers.register import RegisterManager


class CPU(threading.Thread, AbstractCPU):

    instructions: dict[int, Callable]
    exception: Exception
    registers: RegisterManager

    def __init__(self, memory: Memory):
        threading.Thread.__init__(self)

        self.exception = None

        self.close_event = threading.Event()

        self.memory = memory
        self.registers = RegisterManager()

        self.SP = 0xFF
        self.PC = 0x00

        self.instructions = {
            0x00: self._no_operation,
            0x76: self._system_halt,
        }

    def _no_operation(self):
        pass

    def _system_halt(self):
        raise SystemHalt()

    def add_instruction(self, opcode, func: Callable):
        self.instructions[opcode] = func

    def run(self):
        while not self.close_event.is_set() and self.tick():
            continue

    def tick(self):
        try:
            self.execute_instruction()
        except Exception as e:
            if not isinstance(e, SystemHalt):
                self.exception = e

            return False

        return True

    @increment_program_counter()
    def fetch_byte(self):
        return self.read_memory_byte(self.PC)

    def fetch_word(self):
        addr_l = self.fetch_byte()
        addr_h = self.fetch_byte()

        return addr_h << 0x08 | addr_l

    def read_memory_byte(self, addr: int):
        return self.memory[addr & self.memory.max_address()]

    def read_memory_word_bytes(self, addr: int) -> tuple[int, int]:
        h_addr = self.read_memory_byte(addr)
        l_addr = self.read_memory_byte(addr + 0x01)

        return h_addr, l_addr

    def read_memory_word(self, addr: int):
        h_addr, l_addr = self.read_memory_word_bytes(addr)
        return h_addr << 0x08 | l_addr

    def has_instruction(self, opcode):
        return opcode in self.instructions

    def execute_instruction(self):
        opcode = self.fetch_byte()
        if self.has_instruction(opcode):
            self.instructions[opcode]()
        else:
            raise Exception(f"Unknown opcode: 0x{opcode:02x}")

    def set_value_to_register(self, reg_name: str, value: int):
        if hasattr(self, reg_name):
            setattr(self, reg_name, value)
        else:
            raise Exception(f"Unknown register: {reg_name}")

    def decrement_stack_pointer(self) -> None:
        new_value = (self.SP + 0x01) & self.memory.max_address()
        self.SP = new_value
        return None

    def split_word(self, word: int) -> tuple[int, int]:
        return (word >> 0x08) & 0xFF, word & 0xFF
