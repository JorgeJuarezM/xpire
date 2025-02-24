"""
Intel 8080 CPU implementation.
"""

from xpire.cpus.cpu import CPU, logger
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

    @manager.add_instruction(0x06, [Registers.B])
    @manager.add_instruction(0x0E, [Registers.C])
    @manager.add_instruction(0x16, [Registers.D])
    @manager.add_instruction(0x1E, [Registers.E])
    @manager.add_instruction(0x26, [Registers.H])
    @manager.add_instruction(0x2E, [Registers.L])
    @manager.add_instruction(0x3E, [Registers.A])
    def mvi_reg_d8(self, register: int) -> callable:
        self.registers[register] = self.fetch_byte()
        self.cycles += 7

    @manager.add_instruction(0x04, [Registers.B])
    @manager.add_instruction(0x0C, [Registers.C])
    @manager.add_instruction(0x14, [Registers.D])
    @manager.add_instruction(0x1C, [Registers.E])
    @manager.add_instruction(0x24, [Registers.H])
    @manager.add_instruction(0x2C, [Registers.L])
    @manager.add_instruction(0x3C, [Registers.A])
    def inr_reg(self, register: int) -> None:
        reg_value = self.registers[register]
        new_value = (reg_value + 0x01) & 0xFF
        self.registers[register] = new_value

        self.flags.S = (new_value & 0x80) != 0
        self.flags.Z = (new_value & 0xFF) == 0
        self.flags.P = bin(new_value & 0xFF).count("1") % 2 == 0
        self.flags.A = (get_ls_nib(reg_value) + 0x01) > 0x0F

        # print(f"INR {register} --> {hex(reg_value)} --> {hex(new_value)}")

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
    def push_psw(self) -> None:
        flags = self.flags.get_flags()
        logger.info("PUSH FLAGS: %s", hex(flags))
        self.push(self.registers[Registers.A], self.flags.get_flags())
        self.cycles += 11

    @manager.add_instruction(0xC5, [Registers.B, Registers.C])
    @manager.add_instruction(0xD5, [Registers.D, Registers.E])
    @manager.add_instruction(0xE5, [Registers.H, Registers.L])
    def push_reg(self, h: int, l: int) -> None:
        self.push(self.registers[h], self.registers[l])
        self.cycles += 11

    @manager.add_instruction(0xA8, [Registers.A, Registers.B])
    @manager.add_instruction(0xA9, [Registers.A, Registers.C])
    @manager.add_instruction(0xAA, [Registers.A, Registers.D])
    @manager.add_instruction(0xAB, [Registers.A, Registers.E])
    @manager.add_instruction(0xAC, [Registers.A, Registers.H])
    @manager.add_instruction(0xAD, [Registers.A, Registers.L])
    @manager.add_instruction(0xAF, [Registers.A, Registers.A])
    def xra(self, r1: int, r2: int) -> None:
        value1 = self.registers[r1]
        value2 = self.registers[r2]

        result = value1 ^ value2
        self.registers[r1] = result

        self.flags.S = (result & 0x80) != 0
        self.flags.Z = (result & 0xFF) == 0
        self.flags.P = bin(result & 0xFF).count("1") % 2 == 0
        self.flags.A = False
        self.flags.C = False

        # print(f"XRA {r1} --> {hex(value1)} --> {hex(value2)} --> {hex(result)}")

        self.cycles += 4

    @manager.add_instruction(0x32)
    def sta_addr(self) -> None:
        address = self.fetch_word()
        self.write_memory_byte(address, self.registers[Registers.A])
        self.cycles += 13

    @manager.add_instruction(0x01, [Registers.B, Registers.C])
    @manager.add_instruction(0x11, [Registers.D, Registers.E])
    @manager.add_instruction(0x21, [Registers.H, Registers.L])
    def lxi_reg_d16(self, h: int, l: int) -> None:
        self.registers[l] = self.fetch_byte()
        self.registers[h] = self.fetch_byte()
        self.cycles += 10

    @manager.add_instruction(0x46, [Registers.B])
    @manager.add_instruction(0x4E, [Registers.C])
    @manager.add_instruction(0x56, [Registers.D])
    @manager.add_instruction(0x5E, [Registers.E])
    @manager.add_instruction(0x66, [Registers.H])
    @manager.add_instruction(0x6E, [Registers.L])
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
        self.flags.P = (bin(result & 0xFF).count("1") % 2) == 0

        self.flags.A = (get_ls_nib(reg_value) + get_ls_nib(compl)) > 0x0F
        self.flags.C = result <= 0xFF
        self.cycles += 7

        # print(f"CPI {hex(reg_value)} + {hex(compl)} = {hex(result)} --> {self.flags.A}")

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

    @manager.add_instruction(0xB0, [Registers.B])
    @manager.add_instruction(0xB1, [Registers.C])
    @manager.add_instruction(0xB2, [Registers.D])
    @manager.add_instruction(0xB3, [Registers.E])
    @manager.add_instruction(0xB4, [Registers.H])
    @manager.add_instruction(0xB5, [Registers.L])
    @manager.add_instruction(0xB7, [Registers.A])
    def ora_reg(self, register: int) -> None:
        # print("<<<" + hex(self.flags.get_flags()))
        result = self.registers[Registers.A] | self.registers[register]
        self.registers[Registers.A] = result

        self.flags.S = (result & 0x80) != 0
        self.flags.Z = (result & 0xFF) == 0
        self.flags.P = bin(result & 0xFF).count("1") % 2 == 0
        self.flags.C = False
        self.flags.A = False

        # print(">>>" + hex(self.flags.get_flags()))

        # print(
        #     f"ORA {hex(self.registers[register])} --> {hex(self.registers[Registers.A])} --> {hex(result)} --> {self.flags.A}"
        # )
        self.cycles += 4

    @manager.add_instruction(0xF1)
    def pop_psw(self) -> None:
        self.registers[Registers.A], flags_byte = self.pop()
        self.flags.set_flags(flags_byte)
        self.cycles += 10
        logger.info("POP FLAGS: %s", hex(flags_byte))

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

    @manager.add_instruction(0x03, [Registers.B, Registers.C])
    @manager.add_instruction(0x13, [Registers.D, Registers.E])
    @manager.add_instruction(0x23, [Registers.H, Registers.L])
    def inx_reg16(self, h: int, l: int) -> None:
        value = join_bytes(self.registers[h], self.registers[l])
        result = value + 0x01
        new_value = result & 0xFFFF

        high, low = split_word(new_value)
        self.registers[h] = high
        self.registers[l] = low
        self.cycles += 5

    @manager.add_instruction(0x40, [Registers.B, Registers.B])
    @manager.add_instruction(0x41, [Registers.C, Registers.B])
    @manager.add_instruction(0x42, [Registers.D, Registers.B])
    @manager.add_instruction(0x43, [Registers.E, Registers.B])
    @manager.add_instruction(0x44, [Registers.H, Registers.B])
    @manager.add_instruction(0x45, [Registers.L, Registers.B])
    @manager.add_instruction(0x47, [Registers.A, Registers.B])
    @manager.add_instruction(0x48, [Registers.B, Registers.C])
    @manager.add_instruction(0x49, [Registers.C, Registers.C])
    @manager.add_instruction(0x4A, [Registers.D, Registers.C])
    @manager.add_instruction(0x4B, [Registers.E, Registers.C])
    @manager.add_instruction(0x4C, [Registers.H, Registers.C])
    @manager.add_instruction(0x4D, [Registers.L, Registers.C])
    @manager.add_instruction(0x4F, [Registers.A, Registers.C])
    @manager.add_instruction(0x50, [Registers.B, Registers.D])
    @manager.add_instruction(0x51, [Registers.C, Registers.D])
    @manager.add_instruction(0x52, [Registers.D, Registers.D])
    @manager.add_instruction(0x53, [Registers.E, Registers.D])
    @manager.add_instruction(0x54, [Registers.H, Registers.D])
    @manager.add_instruction(0x55, [Registers.L, Registers.D])
    @manager.add_instruction(0x57, [Registers.A, Registers.D])
    @manager.add_instruction(0x58, [Registers.B, Registers.E])
    @manager.add_instruction(0x59, [Registers.C, Registers.E])
    @manager.add_instruction(0x5A, [Registers.D, Registers.E])
    @manager.add_instruction(0x5B, [Registers.E, Registers.E])
    @manager.add_instruction(0x5C, [Registers.H, Registers.E])
    @manager.add_instruction(0x5D, [Registers.L, Registers.E])
    @manager.add_instruction(0x5F, [Registers.A, Registers.E])
    @manager.add_instruction(0x60, [Registers.B, Registers.H])
    @manager.add_instruction(0x61, [Registers.C, Registers.H])
    @manager.add_instruction(0x62, [Registers.D, Registers.H])
    @manager.add_instruction(0x63, [Registers.E, Registers.H])
    @manager.add_instruction(0x64, [Registers.H, Registers.H])
    @manager.add_instruction(0x65, [Registers.L, Registers.H])
    @manager.add_instruction(0x67, [Registers.A, Registers.H])
    @manager.add_instruction(0x68, [Registers.B, Registers.L])
    @manager.add_instruction(0x69, [Registers.C, Registers.L])
    @manager.add_instruction(0x6A, [Registers.D, Registers.L])
    @manager.add_instruction(0x6B, [Registers.E, Registers.L])
    @manager.add_instruction(0x6C, [Registers.H, Registers.L])
    @manager.add_instruction(0x6D, [Registers.L, Registers.L])
    @manager.add_instruction(0x6F, [Registers.A, Registers.L])
    @manager.add_instruction(0x78, [Registers.B, Registers.A])
    @manager.add_instruction(0x79, [Registers.C, Registers.A])
    @manager.add_instruction(0x7A, [Registers.D, Registers.A])
    @manager.add_instruction(0x7B, [Registers.E, Registers.A])
    @manager.add_instruction(0x7C, [Registers.H, Registers.A])
    @manager.add_instruction(0x7D, [Registers.L, Registers.A])
    @manager.add_instruction(0x7F, [Registers.A, Registers.A])
    def mov_reg_reg(self, src: int, dst: int) -> None:
        self.registers[dst] = self.registers[src]
        self.cycles += 5

    @manager.add_instruction(0xCA)
    def jz(self) -> None:
        address = self.fetch_word()
        if self.flags.Z:
            self.PC = address

        self.cycles += 10

    @manager.add_instruction(0x05, [Registers.B])
    @manager.add_instruction(0x0D, [Registers.C])
    @manager.add_instruction(0x15, [Registers.D])
    @manager.add_instruction(0x1D, [Registers.E])
    @manager.add_instruction(0x25, [Registers.H])
    @manager.add_instruction(0x2D, [Registers.L])
    @manager.add_instruction(0x3D, [Registers.A])
    def dcr_reg(self, register: int) -> None:
        reg_value = self.registers[register]
        result = reg_value - 0x01
        new_value = result & 0xFF
        self.registers[register] = new_value

        self.flags.Z = (result & 0xFF) == 0
        self.flags.S = (result & 0x80) != 0
        self.flags.P = bin(result & 0xFF).count("1") % 2 == 0
        # self.flags.A = get_ls_nib(reg_value) == 0x00
        # self.flags.A = True
        # print(f"DCR {register} --> {hex(reg_value)} --> {hex(new_value)}")
        # self.flags.A = not ((result & 0xF) == 0xF)
        self.flags.A = (get_ls_nib(reg_value) - 1) > 0x0F

        self.cycles += 5

    @manager.add_instruction(0x09, [Registers.B, Registers.C])
    @manager.add_instruction(0x19, [Registers.D, Registers.E])
    @manager.add_instruction(0x29, [Registers.H, Registers.L])
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

    @manager.add_instruction(0xEB, [Registers.H, Registers.L, Registers.D, Registers.E])
    def xchg(self, h: int, l: int, d: int, e: int) -> None:
        """
        The 16 bits of data held in the Hand L registers are exchanged
        with the 16 bits of data held in the D and E registers.

        Condition bits affected: None
        """
        h1 = self.registers[h]
        l1 = self.registers[l]
        d1 = self.registers[d]
        e1 = self.registers[e]

        self.registers[h] = d1
        self.registers[l] = e1
        self.registers[d] = h1
        self.registers[e] = l1

        self.cycles += 5

    @manager.add_instruction(0x0B, [Registers.B, Registers.C])
    @manager.add_instruction(0x1B, [Registers.D, Registers.E])
    @manager.add_instruction(0x2B, [Registers.H, Registers.L])
    def dcx_reg16(self, h: int, l: int):
        value = join_bytes(self.registers[h], self.registers[l])
        result = value - 0x01
        result = result & 0xFFFF
        self.registers[h], self.registers[l] = split_word(result)

    @manager.add_instruction(0x33)
    def inx_sp(self):
        self.SP = (self.SP + 0x01) & 0xFFFF
        self.cycles += 5

    @manager.add_instruction(0x22)
    def shld(self) -> None:
        address = self.fetch_word()
        self.write_memory_byte(address, self.registers[Registers.L])
        self.write_memory_byte(address + 0x01, self.registers[Registers.H])

        self.cycles += 16

    @manager.add_instruction(0x2A)
    def lhld(self) -> None:
        address1 = self.fetch_word()
        address2 = (address1 + 0x01) & 0xFFFF

        l = self.read_memory_byte(address1)
        h = self.read_memory_byte(address2)

        self.registers[Registers.L] = l
        self.registers[Registers.H] = h

        self.cycles += 16

    @manager.add_instruction(0x70, [Registers.B])
    @manager.add_instruction(0x71, [Registers.C])
    @manager.add_instruction(0x72, [Registers.D])
    @manager.add_instruction(0x73, [Registers.E])
    @manager.add_instruction(0x74, [Registers.H])
    @manager.add_instruction(0x75, [Registers.L])
    @manager.add_instruction(0x77, [Registers.A])
    def mov_m_reg(self, register: int) -> None:
        address = join_bytes(self.registers[Registers.H], self.registers[Registers.L])
        self.write_memory_byte(address, self.registers[register])
        self.cycles += 7

    @manager.add_instruction(0x39)
    def dad_sp(self) -> None:
        s, p = split_word(self.SP)

        sp = join_bytes(s, p)
        hl = join_bytes(self.registers[Registers.H], self.registers[Registers.L])

        result = hl + sp
        new_value = result & 0xFFFF
        self.registers[Registers.H], self.registers[Registers.L] = split_word(new_value)

        self.flags.C = result > 0xFFFF or result < 0x0000

        self.cycles += 10

    @manager.add_instruction(0xFA)
    def jm_addr(self) -> None:
        address = self.fetch_word()
        if self.flags.S:
            self.PC = address

        self.cycles += 10

    @manager.add_instruction(0xF2)
    def jp(self):
        address = self.fetch_word()
        if not self.flags.S:
            self.PC = address

    @manager.add_instruction(0xB8, [Registers.B])
    @manager.add_instruction(0xB9, [Registers.C])
    @manager.add_instruction(0xBA, [Registers.D])
    @manager.add_instruction(0xBB, [Registers.E])
    @manager.add_instruction(0xBC, [Registers.H])
    @manager.add_instruction(0xBD, [Registers.L])
    @manager.add_instruction(0xBF, [Registers.A])
    def cmp_reg(self, register: int) -> None:
        a_value = self.registers[Registers.A]
        reg_value = self.registers[register]
        compl = get_twos_complement(reg_value)
        result = a_value + compl

        self.flags.Z = (result & 0xFF) == 0x00
        self.flags.S = (result & 0x80) != 0
        self.flags.P = (bin(result & 0xFF).count("1") % 2) == 0
        self.flags.C = result <= 0xFF

        self.flags.A = (get_ls_nib(a_value) + get_ls_nib(compl)) > 0x0F

        # print(
        #     f"CMP {register} --> A: {hex(a_value)} --> Reg: {hex(reg_value)} --> Comp: {hex(compl)} --> {hex(result)}",
        #     self.flags.A,
        # )
        self.cycles += 4

    @manager.add_instruction(0xBE)
    def cmp_m(self) -> None:
        address = join_bytes(self.registers[Registers.H], self.registers[Registers.L])
        a_value = self.registers[Registers.A]
        compl = get_twos_complement(self.read_memory_byte(address))

        result = a_value + compl

        self.flags.Z = (result & 0xFF) == 0x00
        self.flags.S = (result & 0x80) != 0
        self.flags.A = (get_ls_nib(a_value) + get_ls_nib(compl)) > 0x0F
        self.flags.P = (bin(result & 0xFF).count("1") % 2) == 0
        self.flags.C = result <= 0xFF

        # print(
        #     f"CMP M --> A: {hex(a_value)} --> Mem: {hex(self.read_memory_byte(address))} --> Comp: {hex(compl)} --> {hex(result)}",
        #     self.flags.A,
        # )

        self.cycles += 7

    @manager.add_instruction(0xC4)
    def cnz_addr(self) -> None:
        address = self.fetch_word()
        if not self.flags.Z:
            h, l = split_word(self.PC)
            self.push(h, l)
            self.PC = address
            self.cycles += 17
            return

        self.cycles += 11

    @manager.add_instruction(0x0F)
    def rotate_right_a(self) -> None:
        accumulator = self.registers[Registers.A] & 0xFF

        # Obtener el bit menos significativo (LSB) del acumulador
        new_carry = accumulator & 0x01

        # Rotar el acumulador a la derecha
        # El bit de carry se convierte en el bit más significativo (MSB)
        accumulator = (accumulator >> 1) | (new_carry << 7)

        # Asegurarse de que el acumulador siga siendo de 8 bits
        accumulator = accumulator & 0xFF

        self.registers[Registers.A] = accumulator
        self.flags.C = True if new_carry else False

        self.cycles += 4

    @manager.add_instruction(0xE6)
    def ani_d8(self) -> None:
        value1 = self.registers[Registers.A]
        value2 = self.fetch_byte()

        result = value1 & value2
        self.registers[Registers.A] = result

        self.flags.S = (result & 0x80) != 0
        self.flags.Z = (result & 0xFF) == 0x00
        self.flags.P = (bin(result & 0xFF).count("1") % 2) == 0
        self.flags.A = (get_ls_nib(value1) + get_ls_nib(value2)) > 0x0F
        self.flags.C = False

        # print(
        #     f"ANI {hex(value2)} --> A: {hex(value1)} --> Result: {hex(result)}",
        #     self.flags.A,
        # )

        self.cycles += 7

    @manager.add_instruction(0xC7)
    def rst_0(self):
        # if self.interrupts_enabled:
        h, l = split_word(self.PC)
        self.push(h, l)
        self.PC = 0x0000
        self.interrupts_enabled = False

    @manager.add_instruction(0x07)
    def rotate_left_accumulator(self) -> None:
        accumulator = self.registers[Registers.A] & 0xFF

        # Obtener el bit menos significativo (LSB) del acumulador
        new_carry = accumulator & 0x80

        # Rotar el acumulador a la izquierda
        # El bit de carry se convierte en el bit menos significativo (LSB)
        accumulator = (accumulator << 1) | (new_carry >> 7)

        # Asegurarse de que el acumulador siga siendo de 8 bits
        accumulator = accumulator & 0xFF

        self.registers[Registers.A] = accumulator
        self.flags.C = True if new_carry else False

        self.cycles += 4

    @manager.add_instruction(0x17)
    def ral_carry(self):
        carry = 1 if self.flags.C else 0
        a_value = self.registers[Registers.A]
        new_carry = a_value & 0x80

        # Rotar el acumulador a la izquierda
        # El bit de carry se convierte en el bit menos significativo (LSB)
        a_value = (a_value << 1) | (carry >> 7)

        # Asegurarse de que el acumulador siga siendo de 8 bits
        a_value = a_value & 0xFF

        self.registers[Registers.A] = a_value
        self.flags.C = True if new_carry else False

    @manager.add_instruction(0x1F)
    def rar(self) -> None:
        carry = 1 if self.flags.C else 0
        accumulator = self.registers[Registers.A] & 0xFF

        # Obtener el bit menos significativo (LSB) del acumulador
        new_carry = accumulator & 0x01

        # Rotar el acumulador a la derecha
        # El bit de carry se convierte en el bit más significativo (MSB)
        accumulator = (accumulator >> 1) | (carry << 7)

        # Asegurarse de que el acumulador siga siendo de 8 bits
        accumulator = accumulator & 0xFF

        self.registers[Registers.A] = accumulator
        self.flags.C = True if new_carry else False

        self.cycles += 4

    @manager.add_instruction(0x27)
    def daa(self):
        accumulator = self.registers[Registers.A]
        carry = 1 if self.flags.C else 0
        half_carry = 1 if self.flags.A else 0

        lsb = accumulator & 0x0F
        if half_carry or lsb > 9:
            accumulator = (accumulator + 0x06) & 0xFF
            self.flags.A = lsb > 0xF

        msb = accumulator >> 4
        if carry or msb > 9:
            accumulator = (accumulator + 0x60) & 0xFF
            self.flags.C = (msb + 0x60) > 0x0F
        else:
            self.flags.C = False

        self.registers[Registers.A] = accumulator & 0xFF
        self.flags.Z = (accumulator & 0xFF) == 0x00
        self.flags.S = (accumulator & 0x80) != 0x00
        self.flags.P = (bin(accumulator & 0xFF).count("1") % 2) == 0

    @manager.add_instruction(0x2F)
    def cma(self) -> None:
        value = self.registers[Registers.A]
        value ^= 0xFF
        self.registers[Registers.A] = value
        self.cycles += 4

    @manager.add_instruction(0x37)
    def set_carry(self):
        self.flags.C = True

        self.cycles += 4

    @manager.add_instruction(0x3F)
    def cmc(self):
        self.flags.C = not self.flags.C

    @manager.add_instruction(0x80, [Registers.B])
    @manager.add_instruction(0x81, [Registers.C])
    @manager.add_instruction(0x82, [Registers.D])
    @manager.add_instruction(0x83, [Registers.E])
    @manager.add_instruction(0x84, [Registers.H])
    @manager.add_instruction(0x85, [Registers.L])
    @manager.add_instruction(0x87, [Registers.A])
    def add_reg(self, register: int) -> None:
        value_1 = self.registers[Registers.A]
        value_2 = self.registers[register]
        result = value_1 + value_2

        self.flags.S = (result & 0x80) != 0x00
        self.flags.Z = (result & 0xFF) == 0x00
        self.flags.P = (bin(result & 0xFF).count("1") % 2) == 0
        self.flags.A = (get_ls_nib(value_1) + get_ls_nib(value_2)) > 0x0F
        self.flags.C = result > 0xFF

        self.registers[Registers.A] = result & 0xFF
        self.cycles += 4

    @manager.add_instruction(0x88, [Registers.B])
    @manager.add_instruction(0x89, [Registers.C])
    @manager.add_instruction(0x8A, [Registers.D])
    @manager.add_instruction(0x8B, [Registers.E])
    @manager.add_instruction(0x8C, [Registers.H])
    @manager.add_instruction(0x8D, [Registers.L])
    @manager.add_instruction(0x8F, [Registers.A])
    def adc_reg(self, register: int) -> None:
        a_value = self.registers[Registers.A]
        reg_value = self.registers[register]
        reg_value += 1 if self.flags.C else 0
        result = a_value + reg_value

        self.flags.S = (result & 0x80) != 0x00
        self.flags.Z = (result & 0xFF) == 0x00
        self.flags.P = (bin(result & 0xFF).count("1") % 2) == 0
        self.flags.A = (get_ls_nib(a_value) + get_ls_nib(reg_value)) > 0x0F
        self.flags.C = result > 0xFF

        self.registers[Registers.A] = result & 0xFF

        self.cycles += 4

    @manager.add_instruction(0x90, [Registers.B])
    @manager.add_instruction(0x91, [Registers.C])
    @manager.add_instruction(0x92, [Registers.D])
    @manager.add_instruction(0x93, [Registers.E])
    @manager.add_instruction(0x94, [Registers.H])
    @manager.add_instruction(0x95, [Registers.L])
    @manager.add_instruction(0x97, [Registers.A])
    def sub_reg(self, register: int) -> None:
        a_value = self.registers[Registers.A]
        reg_value = self.registers[register]
        compl = get_twos_complement(reg_value)
        result = a_value + compl

        self.flags.S = (result & 0x80) != 0x00
        self.flags.Z = (result & 0xFF) == 0x00
        self.flags.P = (bin(result & 0xFF).count("1") % 2) == 0
        self.flags.A = (get_ls_nib(a_value) + get_ls_nib(compl)) > 0x0F
        self.flags.C = result <= 0xFF

        self.registers[Registers.A] = result & 0xFF
        self.cycles += 4

    @manager.add_instruction(0xA0, [Registers.B])
    @manager.add_instruction(0xA1, [Registers.C])
    @manager.add_instruction(0xA2, [Registers.D])
    @manager.add_instruction(0xA3, [Registers.E])
    @manager.add_instruction(0xA4, [Registers.H])
    @manager.add_instruction(0xA5, [Registers.L])
    @manager.add_instruction(0xA7, [Registers.A])
    def ana_reg(self, register: int) -> None:
        a_value = self.registers[Registers.A]
        value2 = self.registers[register]
        result = a_value & value2
        self.registers[Registers.A] = result

        # print(result, result & 0x80)

        self.flags.S = (result & 0x80) != 0
        # self.flags.S = (result & (0xFF - (0xFF >> 1))) != 0
        self.flags.Z = (result & 0xFF) == 0
        self.flags.P = bin(result & 0xFF).count("1") % 2 == 0
        # self.flags.A = False
        self.flags.C = False
        self.flags.A = (get_ls_nib(a_value) + get_ls_nib(value2)) > 0xF

        self.cycles += 4

    @manager.add_instruction(0xDC)
    def cc(self):
        address = self.fetch_word()
        if self.flags.C:
            h, l = split_word(self.PC)
            self.push(h, l)
            self.PC = address
            self.cycles += 17
            return

        self.cycles += 11

    @manager.add_instruction(0xD4)
    def cnc(self):
        address = self.fetch_word()
        if not self.flags.C:
            h, l = split_word(self.PC)
            self.push(h, l)
            self.PC = address
            self.cycles += 17
            return

        self.cycles += 11

    @manager.add_instruction(0xD8)
    def rc(self) -> None:
        if self.flags.C:
            h, l = self.pop()
            self.PC = join_bytes(h, l)
            self.cycles += 11
            return

        self.cycles += 5

    @manager.add_instruction(0xD0)
    def rnc(self) -> None:
        if not self.flags.C:
            h, l = self.pop()
            self.PC = join_bytes(h, l)
            self.cycles += 11
            return

        self.cycles += 5

    @manager.add_instruction(0xDA)
    def jc(self) -> None:
        address = self.fetch_word()
        if self.flags.C:
            # h, l = split_word(self.PC)
            # self.push(h, l)
            self.PC = address
            self.cycles += 17
            return

        self.cycles += 11

    @manager.add_instruction(0xEC)
    def cpe_addr(self) -> None:
        address = self.fetch_word()
        if self.flags.P:
            h, l = split_word(self.PC)
            self.push(h, l)
            self.PC = address
            self.cycles += 17
            return

        self.cycles += 11

    @manager.add_instruction(0xE4)
    def cpo_addr(self) -> None:
        address = self.fetch_word()
        if not self.flags.P:
            h, l = split_word(self.PC)
            self.push(h, l)
            self.PC = address
            self.cycles += 17
            return

        self.cycles += 11

    @manager.add_instruction(0xE8)
    def rpe(self) -> None:
        if self.flags.P:
            h, l = self.pop()
            self.PC = join_bytes(h, l)
            self.cycles += 11
            return

        self.cycles += 5

    @manager.add_instruction(0xE0)
    def rpo(self) -> None:
        if not self.flags.P:
            h, l = self.pop()
            self.PC = join_bytes(h, l)
            self.cycles += 11
            return

        self.cycles += 5

    @manager.add_instruction(0xE2)
    def jpo(self) -> None:
        address = self.fetch_word()
        if not self.flags.P:
            # h, l = split_word(self.PC)
            # self.push(h, l)
            self.PC = address
            self.cycles += 17
            return

        self.cycles += 11

    @manager.add_instruction(0xCC)
    def cz_addr(self) -> None:
        address = self.fetch_word()
        if self.flags.Z:
            h, l = split_word(self.PC)
            self.push(h, l)
            self.PC = address
            self.cycles += 17
            return

        self.cycles += 11

    @manager.add_instruction(0xC8)
    def rz(self) -> None:
        if self.flags.Z:
            h, l = self.pop()
            self.PC = join_bytes(h, l)
            self.cycles += 11
            return

        self.cycles += 5

    @manager.add_instruction(0xC0)
    def rnz(self) -> None:
        if not self.flags.Z:
            h, l = self.pop()
            self.PC = join_bytes(h, l)
            self.cycles += 11
            return

        self.cycles += 5

    @manager.add_instruction(0xFC)
    def cm_addr(self) -> None:
        address = self.fetch_word()
        if self.flags.S:
            h, l = split_word(self.PC)
            self.push(h, l)
            self.PC = address
            self.cycles += 17
            return

        self.cycles += 11

    @manager.add_instruction(0xF4)
    def cp_addr(self) -> None:
        address = self.fetch_word()
        if not self.flags.S:
            h, l = split_word(self.PC)
            self.push(h, l)
            self.PC = address
            self.cycles += 17
            return

        self.cycles += 11

    @manager.add_instruction(0xF8)
    def rm(self) -> None:
        if self.flags.S:
            h, l = self.pop()
            self.PC = join_bytes(h, l)
            self.cycles += 11
            return

        self.cycles += 5

    @manager.add_instruction(0xF0)
    def rp(self) -> None:
        if not self.flags.S:
            h, l = self.pop()
            self.PC = join_bytes(h, l)
            self.cycles += 11
            return

        self.cycles += 5

    @manager.add_instruction(0xE9)
    def pchl(self) -> None:
        self.PC = join_bytes(self.registers[Registers.H], self.registers[Registers.L])
        self.cycles += 5

    @manager.add_instruction(0xF9)
    def sphl(self) -> None:
        self.SP = join_bytes(self.registers[Registers.H], self.registers[Registers.L])
        self.cycles += 5

    @manager.add_instruction(0xC6)
    def adi_d8(self) -> None:
        value1 = self.registers[Registers.A]
        value2 = self.fetch_byte()

        result = value1 + value2
        self.registers[Registers.A] = result & 0xFF

        self.flags.C = result > 0xFF or result < 0x00
        self.flags.Z = (result & 0xFF) == 0
        self.flags.S = result & 0x80 != 0x00
        self.flags.P = bin(result & 0xFF).count("1") % 2 == 0
        self.flags.A = (get_ls_nib(value1) + get_ls_nib(value2)) > 0x0F

        self.cycles += 7

    @manager.add_instruction(0xCE)
    def aci_d8(self):
        value1 = self.registers[Registers.A]
        value2 = self.fetch_byte()

        result = value1 + value2 + self.flags.C
        self.registers[Registers.A] = result & 0xFF

        self.flags.C = result > 0xFF
        self.flags.Z = self.registers[Registers.A] == 0
        self.flags.S = self.registers[Registers.A] & 0x80 != 0x00
        self.flags.P = bin(result & 0xFF).count("1") % 2 == 0
        self.flags.A = (get_ls_nib(value1) + get_ls_nib(value2) + self.flags.C) > 0x0F

        self.cycles += 7

    @manager.add_instruction(0xD6)
    def sui_d8(self):
        a_value = self.registers[Registers.A]
        i_value = self.fetch_byte()

        compl = get_twos_complement(i_value)

        result = a_value + compl
        self.registers[Registers.A] = result & 0xFF

        self.flags.C = result <= 0xFF
        self.flags.Z = (result & 0xFF) == 0x00
        self.flags.S = (result & 0x80) != 0x00
        self.flags.P = bin(result & 0xFF).count("1") % 2 == 0
        self.flags.A = (get_ls_nib(a_value) + get_ls_nib(compl)) > 0x0F

        self.cycles += 7

    @manager.add_instruction(0xDE)
    def sbi_d8(self):
        a_value = self.registers[Registers.A]
        i_value = self.fetch_byte()

        i_value += 1 if self.flags.C else 0
        compl = get_twos_complement(i_value)

        result = a_value + compl
        self.registers[Registers.A] = result & 0xFF

        self.flags.Z = (result & 0xFF) == 0x00
        self.flags.S = (result & 0x80) != 0x00
        self.flags.P = bin(result & 0xFF).count("1") % 2 == 0

        self.flags.A = (get_ls_nib(a_value) + get_ls_nib(i_value)) > 0x0F
        self.flags.C = result <= 0xFF

        self.cycles += 7

    @manager.add_instruction(0xF6)
    def ori_d8(self):
        value1 = self.registers[Registers.A]
        value2 = self.fetch_byte()

        result = value1 | value2
        self.registers[Registers.A] = result

        self.flags.S = (result & 0x80) != 0
        self.flags.Z = (result & 0xFF) == 0x00
        self.flags.P = (bin(result & 0xFF).count("1") % 2) == 0
        # self.flags.A = (get_ls_nib(value1) + get_ls_nib(value2)) > 0x0F
        self.flags.A = False
        self.flags.C = False

        self.cycles += 7

    @manager.add_instruction(0xEE)
    def xri_d8(self):
        value1 = self.registers[Registers.A]
        value2 = self.fetch_byte()

        result = value1 ^ value2
        self.registers[Registers.A] = result

        self.flags.S = (result & 0x80) != 0
        self.flags.Z = (result & 0xFF) == 0x00
        self.flags.P = (bin(result & 0xFF).count("1") % 2) == 0
        # self.flags.A = (get_ls_nib(value1) + get_ls_nib(value2)) > 0x0F
        self.flags.A = False
        self.flags.C = False

        self.cycles += 7

    @manager.add_instruction(0x98, [Registers.B])
    @manager.add_instruction(0x99, [Registers.C])
    @manager.add_instruction(0x9A, [Registers.D])
    @manager.add_instruction(0x9B, [Registers.E])
    @manager.add_instruction(0x9C, [Registers.H])
    @manager.add_instruction(0x9D, [Registers.L])
    @manager.add_instruction(0x9F, [Registers.A])
    def sbb_reg(self, register: int):
        a_value = self.registers[Registers.A]
        reg_value = self.registers[register]

        reg_value += 1 if self.flags.C else 0
        compl = get_twos_complement(reg_value)

        result = a_value + compl
        self.registers[Registers.A] = result & 0xFF

        self.flags.S = (result & 0x80) != 0x00
        self.flags.Z = (result & 0xFF) == 0x00
        self.flags.P = bin(result & 0xFF).count("1") % 2 == 0

        self.flags.C = result <= 0xFF
        self.flags.A = (get_ls_nib(a_value) + get_ls_nib(compl)) > 0x0F

        self.cycles += 4

    @manager.add_instruction(0x86)
    def add_m(self) -> None:
        value_1 = self.registers[Registers.A]

        address = join_bytes(self.registers[Registers.H], self.registers[Registers.L])
        value_2 = self.read_memory_byte(address)
        result = value_1 + value_2

        self.flags.S = (result & 0x80) != 0x00
        self.flags.Z = (result & 0xFF) == 0x00
        self.flags.P = (bin(result & 0xFF).count("1") % 2) == 0
        self.flags.A = (get_ls_nib(value_1) + get_ls_nib(value_2)) > 0x0F
        self.flags.C = result > 0xFF

        self.registers[Registers.A] = result & 0xFF
        self.cycles += 4

    @manager.add_instruction(0x96)
    def sub_m(self) -> None:
        a_value = self.registers[Registers.A]

        address = join_bytes(self.registers[Registers.H], self.registers[Registers.L])
        value_2 = self.read_memory_byte(address)

        compl = get_twos_complement(value_2)
        result = a_value + compl

        self.flags.S = (result & 0x80) != 0x00
        self.flags.Z = (result & 0xFF) == 0x00
        self.flags.P = (bin(result & 0xFF).count("1") % 2) == 0
        self.flags.A = (get_ls_nib(a_value) + get_ls_nib(compl)) > 0x0F
        self.flags.C = result <= 0xFF

        self.registers[Registers.A] = result & 0xFF
        self.cycles += 4

    @manager.add_instruction(0x8E)
    def adc_m(self) -> None:
        a_value = self.registers[Registers.A]

        address = join_bytes(self.registers[Registers.H], self.registers[Registers.L])
        value_2 = self.read_memory_byte(address)

        value_2 += 1 if self.flags.C else 0
        result = a_value + value_2

        self.flags.S = (result & 0x80) != 0x00
        self.flags.Z = (result & 0xFF) == 0x00
        self.flags.P = (bin(result & 0xFF).count("1") % 2) == 0
        self.flags.A = (get_ls_nib(a_value) + get_ls_nib(value_2)) > 0x0F
        self.flags.C = result > 0xFF

        self.registers[Registers.A] = result & 0xFF

        self.cycles += 4

    @manager.add_instruction(0x9E)
    def sbb_m(self):
        a_value = self.registers[Registers.A]

        address = join_bytes(self.registers[Registers.H], self.registers[Registers.L])
        value_2 = self.read_memory_byte(address)

        value_2 += 1 if self.flags.C else 0
        compl = get_twos_complement(value_2)

        result = a_value + compl
        self.registers[Registers.A] = result & 0xFF

        self.flags.S = (result & 0x80) != 0x00
        self.flags.Z = (result & 0xFF) == 0x00
        self.flags.P = bin(result & 0xFF).count("1") % 2 == 0

        self.flags.C = result <= 0xFF
        self.flags.A = (get_ls_nib(a_value) + get_ls_nib(compl)) > 0x0F

        self.cycles += 4

    @manager.add_instruction(0xA6)
    def ana_m(self) -> None:
        a_value = self.registers[Registers.A]

        address = join_bytes(self.registers[Registers.H], self.registers[Registers.L])
        value_2 = self.read_memory_byte(address)

        result = a_value & value_2
        self.registers[Registers.A] = result

        # print(result, result & 0x80)

        self.flags.S = (result & 0x80) != 0
        # self.flags.S = (result & (0xFF - (0xFF >> 1))) != 0
        self.flags.Z = (result & 0xFF) == 0
        self.flags.P = bin(result & 0xFF).count("1") % 2 == 0
        # self.flags.A = False
        self.flags.C = False
        self.flags.A = (get_ls_nib(a_value) + get_ls_nib(value_2)) > 0xF

        self.cycles += 4

    @manager.add_instruction(0xB6)
    def ora_m(self) -> None:
        # print("<<<" + hex(self.flags.get_flags()))

        address = join_bytes(self.registers[Registers.H], self.registers[Registers.L])
        value_2 = self.read_memory_byte(address)

        result = self.registers[Registers.A] | value_2
        self.registers[Registers.A] = result

        self.flags.S = (result & 0x80) != 0
        self.flags.Z = (result & 0xFF) == 0
        self.flags.P = bin(result & 0xFF).count("1") % 2 == 0
        self.flags.C = False
        self.flags.A = False

        # print(">>>" + hex(self.flags.get_flags()))

        # print(
        #     f"ORA {hex(self.registers[register])} --> {hex(self.registers[Registers.A])} --> {hex(result)} --> {self.flags.A}"
        # )
        self.cycles += 4

    @manager.add_instruction(0xAE, [Registers.A])
    def xra_m(self, r1: int) -> None:
        value1 = self.registers[r1]

        address = join_bytes(self.registers[Registers.H], self.registers[Registers.L])
        value_2 = self.read_memory_byte(address)

        result = value1 ^ value_2
        self.registers[r1] = result

        self.flags.S = (result & 0x80) != 0
        self.flags.Z = (result & 0xFF) == 0
        self.flags.P = bin(result & 0xFF).count("1") % 2 == 0
        self.flags.A = False
        self.flags.C = False

        # print(f"XRA {r1} --> {hex(value1)} --> {hex(value2)} --> {hex(result)}")

        self.cycles += 4

    @manager.add_instruction(0x36)
    def mvi_m(self):
        address = join_bytes(self.registers[Registers.H], self.registers[Registers.L])
        self.write_memory_byte(address, self.fetch_byte())
        self.cycles += 7

    @manager.add_instruction(0x34)
    def inr_m(self) -> None:

        address = join_bytes(self.registers[Registers.H], self.registers[Registers.L])
        value_2 = self.read_memory_byte(address)

        new_value = (value_2 + 0x01) & 0xFF

        self.write_memory_byte(address, new_value)

        self.flags.S = (new_value & 0x80) != 0
        self.flags.Z = (new_value & 0xFF) == 0
        self.flags.P = bin(new_value & 0xFF).count("1") % 2 == 0
        self.flags.A = (get_ls_nib(value_2) + 0x01) > 0x0F

        # print(f"INR {register} --> {hex(reg_value)} --> {hex(new_value)}")

        self.cycles += 5

    @manager.add_instruction(0x35)
    def dcr_m(self) -> None:

        address = join_bytes(self.registers[Registers.H], self.registers[Registers.L])
        value_2 = self.read_memory_byte(address)

        result = value_2 - 0x01
        new_value = result & 0xFF
        self.write_memory_byte(address, new_value)

        self.flags.Z = (result & 0xFF) == 0
        self.flags.S = (result & 0x80) != 0
        self.flags.P = bin(result & 0xFF).count("1") % 2 == 0
        # self.flags.A = get_ls_nib(reg_value) == 0x00
        # self.flags.A = True
        # print(f"DCR {register} --> {hex(reg_value)} --> {hex(new_value)}")
        # self.flags.A = not ((result & 0xF) == 0xF)
        self.flags.A = (get_ls_nib(value_2) - 1) > 0x0F

        self.cycles += 5

    @manager.add_instruction(0x1A, [Registers.D, Registers.E])
    @manager.add_instruction(0x0A, [Registers.B, Registers.C])
    def load_address_from_register_to_accumulator(self, h: int, l: int) -> None:
        address_l = self.registers[l]
        address_h = self.registers[h]
        address = join_bytes(address_h, address_l)
        self.registers[Registers.A] = self.read_memory_byte(address)
        self.cycles += 7

    @manager.add_instruction(0x12, [Registers.D, Registers.E])
    @manager.add_instruction(0x02, [Registers.B, Registers.C])
    def store_accumulator_to_mem_reg(self, r1: int, r2: int):
        address = join_bytes(self.registers[r1], self.registers[r2])
        self.write_memory_byte(address, self.registers[Registers.A])

    @manager.add_instruction(0x3B)
    def dcx_sp(self):
        self.SP = (self.SP - 0x01) & 0xFFFF
