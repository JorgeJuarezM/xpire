"""
Intel 8080 CPU implementation.
"""

from xpire.cpus.cpu import CPU
from xpire.decorators import increment_stack_pointer
from xpire.instructions.manager import InstructionManager as manager
from xpire.registers.inter_8080 import Registers
from xpire.utils import get_ls_nib, get_twos_complement, join_bytes, split_word


class Intel8080(CPU):
    """
    Intel 8080 CPU implementation.
    """

    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize a new Intel8080 CPU.

        This constructor calls the base class constructor with the given arguments and
        initializes the registers to zero.
        """
        super().__init__(*args, **kwargs)

        self.registers[Registers.A] = 0x00
        self.registers[Registers.B] = 0x00
        self.registers[Registers.C] = 0x00
        self.registers[Registers.D] = 0x00
        self.registers[Registers.E] = 0x00
        self.registers[Registers.H] = 0x00
        self.registers[Registers.L] = 0x00

        self.out = {}

        self.interrupts_enabled = False

    def write_memory_byte(self, address, value) -> None:
        """
        Store a byte in memory at the specified address.

        This method takes a 16-bit address and an 8-bit value, and stores the value in memory at the specified address.
        """
        address = address & 0xFFFF
        self.memory[address] = value & 0xFF

    def write_memory_word(self, address, high_byte, low_byte) -> None:
        """
        Store a 16-bit value in memory at the specified address.

        This method takes a 16-bit address and a 16-bit value, and stores the value in memory at the specified address.
        The value is stored in memory as a 16-bit value (i.e. high byte first, low byte second).
        """
        self.write_memory_byte(address, low_byte)
        self.write_memory_byte(address + 0x01, high_byte)

    def push(self, high_byte, low_byte) -> None:
        """
        Push a word to the stack.

        This method decrements the stack pointer by two and stores
        the given high and low bytes at the new stack pointer location.
        The high byte is stored first, followed by the low byte.

        Args:
            high_byte (int): The high byte of the word to push.
            low_byte (int): The low byte of the word to push.
        """
        self.decrement_stack_pointer()
        self.write_memory_word(self.SP, high_byte, low_byte)

    @increment_stack_pointer()
    def pop(self) -> tuple[int, int]:
        """
        Pop a 16-bit value from the stack.

        This instruction pops two bytes from the stack and returns them as a 16-bit value (i.e. high byte first, low byte second).
        The stack pointer is incremented by two after the pop.
        """
        return self.read_memory_word_bytes(self.SP)

    @manager.add_instruction(0x0E, [Registers.C])
    @manager.add_instruction(0x1E, [Registers.E])
    @manager.add_instruction(0x3E, [Registers.A])
    def mvi_reg_d8(self, register: int) -> callable:
        self.registers[register] = self.fetch_byte()
        self.cycles += 7

    @manager.add_instruction(0x3C, [Registers.A])
    def inr_r(self, register: int) -> None:
        reg_value = self.registers[register]
        new_value = (reg_value + 0x01) & 0xFF
        self.registers[register] = new_value

        self.flags.S = (new_value & 0x80) != 0
        self.flags.Z = (new_value & 0xFF) == 0
        self.flags.P = bin(new_value & 0xFF).count("1") % 2 == 0
        self.flags.A = (get_ls_nib(reg_value) + 0x01) > 0x0F

        self.cycles += 5

    @manager.add_instruction(0xEA)
    def jpe_addr(self) -> None:
        address = self.fetch_word()
        if self.flags.P:
            self.PC = address
        self.cycles += 10

    @manager.add_instruction(0xC3)
    def jmp(self):
        address = self.fetch_word()
        self.PC = address
        self.cycles += 10

    @manager.add_instruction(0xF3)
    def di(self):
        self.interrupts_enabled = False
        self.cycles += 4

    @manager.add_instruction(0x31)
    def lxi_sp_d16(self) -> None:
        self.SP = self.fetch_word()
        self.cycles += 10

    @manager.add_instruction(0xCD)
    def call(self):
        address = self.fetch_word()
        h, l = split_word(self.PC)
        self.push(h, l)
        self.PC = address

    @manager.add_instruction(0xF5)
    def push_processor_state_word(self) -> None:
        self.push(self.registers[Registers.A], self.flags.get_flags())
        self.cycles += 11

    @manager.add_instruction(0xC5, [Registers.B, Registers.C])
    @manager.add_instruction(0xD5, [Registers.D, Registers.E])
    @manager.add_instruction(0xE5, [Registers.H, Registers.L])
    def push_reg(self, h: int, l: int) -> None:
        self.push(self.registers[h], self.registers[l])
        self.cycles += 11

    @manager.add_instruction(0xAF, [Registers.A, Registers.A])
    def xra(self, r1: int, r2: int) -> None:
        value1 = self.registers[r1]
        value2 = self.registers[r2]

        result = value1 ^ value2
        self.registers[r1] = result

        self.flags.C = False
        self.flags.S = (result & 0x80) != 0
        self.flags.Z = (result & 0xFF) == 0
        self.flags.P = bin(result & 0xFF).count("1") % 2 == 0
        self.flags.A = False

        self.cycles += 4

    @manager.add_instruction(0x32)
    def sta_addr(self) -> None:
        address = self.fetch_word()
        self.write_memory_byte(address, self.registers[Registers.A])
        self.cycles += 13

    @manager.add_instruction(0x01, [Registers.B, Registers.C])
    @manager.add_instruction(0x21, [Registers.H, Registers.L])
    def lxi_reg_d16(self, h: int, l: int) -> None:
        self.registers[l] = self.fetch_byte()
        self.registers[h] = self.fetch_byte()
        self.cycles += 10

    @manager.add_instruction(0x7E, [Registers.A])
    def mov_reg_m(self, register: int) -> None:
        address = join_bytes(self.registers[Registers.H], self.registers[Registers.L])
        self.registers[register] = self.read_memory_byte(address)
        self.cycles += 7

    @manager.add_instruction(0xFE, [Registers.A])
    def cpi(self, register: int) -> None:
        reg_value = self.registers[register]
        compl = get_twos_complement(self.fetch_byte())
        result = reg_value + compl

        self.flags.Z = (result & 0xFF) == 0x00
        self.flags.S = (result & 0x80) != 0
        self.flags.A = (get_ls_nib(reg_value) + get_ls_nib(compl)) > 0x0F
        self.flags.P = (bin(result & 0xFF).count("1") % 2) == 0
        self.flags.C = result <= 0xFF
        self.cycles += 7

    @manager.add_instruction(0xC2)
    def jnz(self) -> None:
        address = self.fetch_word()
        if not self.flags.Z:
            self.PC = address

        self.cycles += 10

    @manager.add_instruction(0xC9)
    def return_from_call(self) -> None:
        h, l = self.pop()
        self.PC = join_bytes(h, l)
        self.cycles += 10

    @manager.add_instruction(0x3A)
    def load_memory_address_to_accumulator(self) -> None:
        address = self.fetch_word()
        self.registers[Registers.A] = self.read_memory_byte(address)
        self.cycles += 13

    @manager.add_instruction(0xB7, [Registers.A])
    def ora_reg(self, register: int) -> None:
        result = self.registers[Registers.A] | self.registers[register]
        self.registers[Registers.A] = result

        self.flags.S = (result & 0x80) != 0
        self.flags.Z = (result & 0xFF) == 0
        self.flags.P = bin(result & 0xFF).count("1") % 2 == 0
        self.flags.C = False
        self.flags.A = False

        self.cycles += 4

    @manager.add_instruction(0xF1)
    def pop_psw(self) -> None:
        self.registers[Registers.A], flags_byte = self.pop()
        self.cycles += 10

    @manager.add_instruction(0xC1, [Registers.B, Registers.C])
    @manager.add_instruction(0xD1, [Registers.D, Registers.E])
    @manager.add_instruction(0xE1, [Registers.H, Registers.L])
    def pop_reg(self, h: int, l: int) -> None:
        high, low = self.pop()
        self.registers[h], self.registers[l] = high, low
        self.cycles += 10

    @manager.add_instruction(0xE3)
    def xthl(self):
        h, l = self.registers[Registers.H], self.registers[Registers.L]
        self.registers[Registers.L] = self.read_memory_byte(self.SP)
        self.registers[Registers.H] = self.read_memory_byte(self.SP + 0x01)
        self.write_memory_word(self.SP, h, l)
        self.cycles += 18

    @manager.add_instruction(0x23, [Registers.H, Registers.L])
    def inx_reg16(self, h: int, l: int) -> None:
        value = join_bytes(self.registers[h], self.registers[l])
        result = value + 0x01
        new_value = result & 0xFFFF

        high, low = split_word(new_value)
        self.registers[h] = high
        self.registers[l] = low
        self.cycles += 5

    @manager.add_instruction(0x5F, [Registers.A, Registers.E])
    def mov_reg_reg(self, src: int, dst: int) -> None:
        self.registers[dst] = self.registers[src]
        self.cycles += 5

    @manager.add_instruction(0xCA)
    def jz(self) -> None:
        address = self.fetch_word()
        if self.flags.Z:
            self.PC = address

        self.cycles += 10

    @manager.add_instruction(0x0D, [Registers.C])
    def dcr_reg(self, register: int) -> None:
        reg_value = self.registers[register]
        result = reg_value - 0x01
        new_value = result & 0xFF
        self.registers[register] = new_value

        self.flags.Z = (new_value & 0xFF) == 0
        self.flags.S = (new_value & 0x80) != 0
        self.flags.P = bin(new_value & 0xFF).count("1") % 2 == 0
        self.flags.A = get_ls_nib(reg_value) == 0x00

        self.cycles += 5

    @manager.add_instruction(0x09, [Registers.B, Registers.C])
    def dad_reg16(self, h: int, l: int) -> None:
        h_value = self.registers[h]
        l_value = self.registers[l]

        value1 = join_bytes(h_value, l_value)
        value2 = join_bytes(self.registers[Registers.H], self.registers[Registers.L])

        result = value1 + value2
        new_value = result & 0xFFFF
        self.registers[Registers.H], self.registers[Registers.L] = split_word(new_value)

        self.flags.C = result > 0xFFFF or result < 0x0000
        self.cycles += 10

    @manager.add_instruction(0xD2)
    def jnc(self) -> None:
        address = self.fetch_word()
        if not self.flags.C:
            self.PC = address

        self.cycles += 10
