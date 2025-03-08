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
        self.port_1 = 0x08

    def write_memory_byte(self, address, value) -> None:
        """
        Store a byte in memory at the specified address.

        This method takes a 16-bit address and an 8-bit value, and stores the value in memory at the specified address.
        """
        address = address & 0xFFFF
        self.memory[address] = value & 0xFF

    def _push(self, high_byte, low_byte) -> None:
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

    def write_memory_word(self, address, high_byte, low_byte) -> None:
        """
        Store a 16-bit value in memory at the specified address.

        This method takes a 16-bit address and a 16-bit value, and stores the value in memory at the specified address.
        The value is stored in memory as a 16-bit value (i.e. high byte first, low byte second).
        """
        self.write_memory_byte(address, low_byte)
        self.write_memory_byte(address + 0x01, high_byte)

    @increment_stack_pointer()
    def _pop(self) -> tuple[int, int]:
        """
        Pop a 16-bit value from the stack.

        This instruction pops two bytes from the stack and returns them as a 16-bit value (i.e. high byte first, low byte second).
        The stack pointer is incremented by two after the pop.
        """
        return self.read_memory_word_bytes(self.SP)

    def set_flags(self, value: int, mask: int = 0xFF) -> None:
        self.flags.Z = value == 0x00
        self.flags.S = bool(value & 0x80)
        self.flags.P = self.check_parity(value, mask)

    def check_parity(self, value: int, mask: int = 0xFF) -> bool:
        return (bin(value & mask).count("1") % 2) == 0

    def set_carry_flag(self, value: int, mask: int = 0xFF) -> None:
        self.flags.C = value > mask or value < 0x00

    def set_aux_carry_flag(self, a: int, b: int, mask: int = 0x0F) -> None:
        result = (a & mask) + (b & mask)
        if result > mask or result < 0x00:
            self.flags.A = True
        else:
            self.flags.A = False

    def substract_with_twos_complement(self, v1: int, v2: int) -> int:
        compl = get_twos_complement(v2)
        result = v1 + compl

        self.flags.S = (result & 0x80) != 0x00
        self.flags.Z = (result & 0xFF) == 0x00
        self.flags.A = (get_ls_nib(v1) + get_ls_nib(compl)) > 0x0F
        self.flags.P = bin(result & 0xFF).count("1") % 2 == 0

        return result

    def decrement_byte_value(self, value: int) -> int:
        result = value - 0x01

        self.flags.S = (result & 0x80) != 0x00
        self.flags.Z = (result & 0xFF) == 0x00
        self.flags.A = get_ls_nib(value) == 0x00
        self.flags.P = bin(result & 0xFF).count("1") % 2 == 0

        return result

    def compare_with_twos_complement(self, v1: int, v2: int) -> int:
        compl = get_twos_complement(v2)
        result = v1 + compl

        self.flags.Z = (result & 0xFF) == 0x00
        self.flags.S = (result & 0x80) != 0
        self.flags.A = (get_ls_nib(v1) + get_ls_nib(compl)) > 0x0F
        self.flags.P = (bin(result & 0xFF).count("1") % 2) == 0
        self.flags.C = result <= 0xFF

    @manager.add_instruction(0x01, [Registers.B, Registers.C])
    @manager.add_instruction(0x11, [Registers.D, Registers.E])
    @manager.add_instruction(0x21, [Registers.H, Registers.L])
    def lxi_reg_d16(self, h: int, l: int) -> None:
        self.registers[l] = self.fetch_byte()
        self.registers[h] = self.fetch_byte()
        self.cycles += 10

    @manager.add_instruction(0x02, [Registers.B, Registers.C])
    @manager.add_instruction(0x12, [Registers.D, Registers.E])
    def stax_reg(self, r1: int, r2: int):
        address = join_bytes(self.registers[r1], self.registers[r2])
        self.write_memory_byte(address, self.registers[Registers.A])
        self.cycles += 7

    @manager.add_instruction(0x03, [Registers.B, Registers.C])
    @manager.add_instruction(0x13, [Registers.D, Registers.E])
    @manager.add_instruction(0x23, [Registers.H, Registers.L])
    def inx_reg(self, h: int, l: int) -> None:
        """
        Increment the value of the specified register pair by one.

        Condition bits affected: Zero, Sign, Parity, Auxiliary.
        """
        value = join_bytes(self.registers[h], self.registers[l])
        result = value + 0x01
        new_value = result & 0xFFFF

        high, low = split_word(new_value)
        self.registers[h] = high
        self.registers[l] = low
        self.cycles += 5

    @manager.add_instruction(0x04, [Registers.B])
    @manager.add_instruction(0x0C, [Registers.C])
    @manager.add_instruction(0x14, [Registers.D])
    @manager.add_instruction(0x1C, [Registers.E])
    @manager.add_instruction(0x24, [Registers.H])
    @manager.add_instruction(0x2C, [Registers.L])
    @manager.add_instruction(0x3C, [Registers.A])
    def inr_reg(self, register: int) -> None:
        """
        Increment the value of the specified register by one.

        Condition bits affected: Zero, Sign, Parity, Auxiliary.
        """
        value = self.registers[register]
        result = value + 0x01
        new_value = result & 0xFF
        self.registers[register] = new_value

        self.set_flags(new_value)
        self.set_aux_carry_flag(value, 0x01)

        self.cycles += 5

    @manager.add_instruction(0x05, [Registers.B])
    @manager.add_instruction(0x0D, [Registers.C])
    @manager.add_instruction(0x15, [Registers.D])
    @manager.add_instruction(0x1D, [Registers.E])
    @manager.add_instruction(0x25, [Registers.H])
    @manager.add_instruction(0x2D, [Registers.L])
    @manager.add_instruction(0x3D, [Registers.A])
    def dcr_reg(self, register: int) -> None:
        """
        Decrement the value of the specified register by one.

        Condition bits affected: Zero, Sign, Parity, Auxiliary Carry
        """
        reg_value = self.registers[register]
        result = reg_value - 0x01
        new_value = result & 0xFF
        self.registers[register] = new_value

        self.set_flags(new_value)
        self.flags.A = ((result & 0xF) - 1) > 0xF
        self.cycles += 5

    @manager.add_instruction(0x06, [Registers.B])
    @manager.add_instruction(0x0E, [Registers.C])
    @manager.add_instruction(0x16, [Registers.D])
    @manager.add_instruction(0x1E, [Registers.E])
    @manager.add_instruction(0x26, [Registers.H])
    @manager.add_instruction(0x2E, [Registers.L])
    @manager.add_instruction(0x3E, [Registers.A])
    def mvi_reg(self, register: int) -> callable:
        """
        Move an immediate value to the specified register.

        This instruction fetches an immediate 8-bit value from memory and stores
        it in the specified register. The opcode determines which register the
        value will be stored in.

        Args:
            register (int): The register identifier where the immediate value
                            should be stored.
        """
        self.registers[register] = self.fetch_byte()
        self.cycles += 7

    @manager.add_instruction(0x07)
    def rlc(self) -> None:
        """
        The carry bit is set equal to the high-order bit of the accumulator.

        The contents of the accumulator are rotated one bit position
        to the left, with the high-order bit being transferred to the
        low-order bit position of the accumulator.

        Condition bits affected: Carry.
        """
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

    @manager.add_instruction(0x08)
    @manager.add_instruction(0x10)
    def ignored_instruction(self) -> None:
        self.cycles += 4

    @manager.add_instruction(0x09, [Registers.B, Registers.C])
    @manager.add_instruction(0x19, [Registers.D, Registers.E])
    @manager.add_instruction(0x29, [Registers.H, Registers.L])
    def dad_reg16(self, h: int, l: int) -> None:
        """
        The 16-bit number in the specified register pair is added
        to the 16-bit number held in the Hand L registers using two's complement arithmetic.

        The result replaces the contents of the Hand L registers.

        Condition bits affected: Carry.
        """
        h_value = self.registers[h]
        l_value = self.registers[l]

        value1 = join_bytes(h_value, l_value)
        value2 = join_bytes(self.registers[Registers.H], self.registers[Registers.L])

        result = value1 + value2
        new_value = result & 0xFFFF
        self.registers[Registers.H], self.registers[Registers.L] = split_word(new_value)

        self.set_carry_flag(result, mask=0xFFFF)

        self.cycles += 10

    @manager.add_instruction(0x0A, [Registers.B, Registers.C])
    @manager.add_instruction(0x1A, [Registers.D, Registers.E])
    def ldax_reg16(self, h: int, l: int) -> None:
        address_l = self.registers[l]
        address_h = self.registers[h]
        address = join_bytes(address_h, address_l)
        self.registers[Registers.A] = self.read_memory_byte(address)
        self.cycles += 7

    @manager.add_instruction(0x0B, [Registers.B, Registers.C])
    @manager.add_instruction(0x1B, [Registers.D, Registers.E])
    @manager.add_instruction(0x2B, [Registers.H, Registers.L])
    def dcx_reg16(self, h: int, l: int):
        value = join_bytes(self.registers[h], self.registers[l])
        result = value - 0x01
        result = result & 0xFFFF
        self.registers[h], self.registers[l] = split_word(result)

        self.cycles += 5

    @manager.add_instruction(0x0F)
    def rrc(self) -> None:
        """
        The carry bit is set equal to the low-order bit of the accumulator.

        The contents of the accumulator are rotated one bit position
        to the right, with the low-order bit being transferred to the
        high-order bit position of the accumulator.

        Condition bits affected: Carry.
        """
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

    @manager.add_instruction(0x17)
    def ral(self):
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
        self.cycles += 4

    @manager.add_instruction(0x1F)
    def rar(self) -> None:
        """
        The contents of the accumulator are rotated one bit position to the right.

        The low-order bit of the accumulator replaces the carry bit,
        while the carry bit replaces the high-order bit of the accumulator.

        Condition bits affected: Carry.
        """
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

    @manager.add_instruction(0x22)
    def shld(self) -> None:
        address = self.fetch_word()
        self.write_memory_byte(address, self.registers[Registers.L])
        self.write_memory_byte(address + 0x01, self.registers[Registers.H])
        self.cycles += 16

    @manager.add_instruction(0x27)
    def daa(self):
        accumulator = self.registers[Registers.A]
        carry = 1 if self.flags.C else 0
        half_carry = 1 if self.flags.A else 0

        lsb = accumulator & 0x0F
        if half_carry or lsb > 9:
            accumulator = (accumulator + 0x06) & 0xFF
            self.flags.A = (lsb + 0x06) > 0xF

        msb = accumulator >> 4
        if carry or msb > 9:
            accumulator = (accumulator + 0x60) & 0xFF
            self.flags.C = (msb + 0x06) > 0x0F
        else:
            self.flags.C = False

        self.registers[Registers.A] = accumulator & 0xFF
        self.flags.Z = (accumulator & 0xFF) == 0x00
        self.flags.S = (accumulator & 0x80) != 0x00
        self.flags.P = (bin(accumulator & 0xFF).count("1") % 2) == 0

    @manager.add_instruction(0x2A)
    def lhld(self) -> None:
        address1 = self.fetch_word()
        address2 = (address1 + 0x01) & 0xFFFF

        l = self.read_memory_byte(address1)
        h = self.read_memory_byte(address2)

        self.registers[Registers.L] = l
        self.registers[Registers.H] = h
        self.cycles += 16

    @manager.add_instruction(0x2F)
    def cma(self) -> None:
        value = self.registers[Registers.A]
        value ^= 0xFF
        self.registers[Registers.A] = value
        self.cycles += 4

    @manager.add_instruction(0x31)
    def lxi_sp_d16(self) -> None:
        """
        Load a 16-bit address from memory to the stack pointer (SP).

        The stack pointer is set to the value of the 16-bit address fetched from memory.
        """
        self.SP = self.fetch_word()
        self.cycles += 10

    @manager.add_instruction(0x32)
    def sta_addr(self) -> None:
        """
        Store the value of the accumulator in memory at the address specified by the next two bytes.

        This instruction fetches a 16-bit address from memory and stores the value of the accumulator at that
        address. The address is fetched as a 16-bit value from memory and the accumulator is stored in memory
        as a byte at that address.
        """
        address = self.fetch_word()
        self.write_memory_byte(address, self.registers[Registers.A])
        self.cycles += 13

    @manager.add_instruction(0x33)
    def inx_sp(self):
        self.SP = (self.SP + 0x01) & 0xFFFF
        self.cycles += 5

    @manager.add_instruction(0x34)
    def inr_m(self):
        address = join_bytes(self.registers[Registers.H], self.registers[Registers.L])
        m_value = self.read_memory_byte(address)
        result = m_value + 0x01
        self.write_memory_byte(address, result)

        self.flags.S = (result & 0x80) != 0x00
        self.flags.Z = (result & 0xFF) == 0x00
        self.flags.A = (get_ls_nib(m_value) + 0x01) > 0x0F
        self.flags.P = bin(result & 0xFF).count("1") % 2 == 0
        self.cycles += 10

    @manager.add_instruction(0x35)
    def dcr_m(self) -> None:
        address = join_bytes(
            self.registers[Registers.H],
            self.registers[Registers.L],
        )
        result = self.decrement_byte_value(self.read_memory_byte(address))
        self.write_memory_byte(address, result)

        self.cycles += 10

    @manager.add_instruction(0x36)
    def move_immediate_to_hl_memory(self) -> None:
        address = join_bytes(self.registers[Registers.H], self.registers[Registers.L])
        self.write_memory_byte(address, self.fetch_byte())
        self.cycles += 10

    @manager.add_instruction(0x37)
    def set_carry(self):
        self.flags.C = True
        self.cycles += 4

    @manager.add_instruction(0x39)
    def dad_sp(self) -> None:
        h_value, l_value = split_word(self.SP)

        value1 = join_bytes(h_value, l_value)
        value2 = join_bytes(self.registers[Registers.H], self.registers[Registers.L])

        result = value1 + value2
        new_value = result & 0xFFFF
        self.registers[Registers.H], self.registers[Registers.L] = split_word(new_value)

        self.set_carry_flag(result, mask=0xFFFF)

        self.cycles += 10

    @manager.add_instruction(0x3A)
    def lda_addr(self) -> None:
        """
        Load the value at the specified memory address to the accumulator (A register).

        This instruction fetches a 16-bit address from memory and loads the value stored at that address
        to the accumulator. The value is loaded as a byte, not a word.
        """
        address = self.fetch_word()
        value = self.read_memory_byte(address)
        self.registers[Registers.A] = value
        self.cycles += 13

    @manager.add_instruction(0x3B)
    def dcx_sp(self):
        self.SP = (self.SP - 0x01) & 0xFFFF
        self.cycles += 5

    @manager.add_instruction(0x3F)
    def cmc(self):
        self.flags.C = not self.flags.C
        self.cycles += 4

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

    @manager.add_instruction(0x86)
    def add_m(self) -> None:
        value1 = self.registers[Registers.A]
        h = self.registers[Registers.H]
        l = self.registers[Registers.L]
        value2 = self.read_memory_byte(join_bytes(h, l))

        result = value1 + value2
        new_value = result & 0xFF
        self.registers[Registers.A] = new_value

        self.set_flags(new_value)
        self.set_carry_flag(result)
        self.set_aux_carry_flag(value1, value2)
        self.cycles += 7

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

        self.flags.S = (result & 0x80) != 0
        self.flags.Z = (result & 0xFF) == 0
        self.flags.P = bin(result & 0xFF).count("1") % 2 == 0
        self.flags.C = False
        self.flags.A = (get_ls_nib(a_value) + get_ls_nib(value2)) > 0xF

        self.cycles += 4

    @manager.add_instruction(0xA6)
    def and_memory_to_accumulator(self) -> None:
        value1 = self.registers[Registers.A]
        h = self.registers[Registers.H]
        l = self.registers[Registers.L]
        value2 = self.read_memory_byte(join_bytes(h, l))

        result = value1 & value2
        self.registers[Registers.A] = result

        self.set_flags(result)
        self.set_aux_carry_flag(value1, value2)
        self.flags.C = False
        self.cycles += 7

    @manager.add_instruction(0xA8, [Registers.B])
    @manager.add_instruction(0xA9, [Registers.C])
    @manager.add_instruction(0xAA, [Registers.D])
    @manager.add_instruction(0xAB, [Registers.E])
    @manager.add_instruction(0xAC, [Registers.H])
    @manager.add_instruction(0xAD, [Registers.L])
    @manager.add_instruction(0xAF, [Registers.A])
    def xra(self, register: int) -> None:
        value1 = self.registers[Registers.A]
        value2 = self.registers[register]

        result = value1 ^ value2
        self.registers[Registers.A] = result

        self.flags.S = (result & 0x80) != 0
        self.flags.Z = (result & 0xFF) == 0
        self.flags.P = bin(result & 0xFF).count("1") % 2 == 0
        self.flags.C = False
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
        self.cycles += 4

    @manager.add_instruction(0xB0, [Registers.B])
    @manager.add_instruction(0xB1, [Registers.C])
    @manager.add_instruction(0xB2, [Registers.D])
    @manager.add_instruction(0xB3, [Registers.E])
    @manager.add_instruction(0xB4, [Registers.H])
    @manager.add_instruction(0xB5, [Registers.L])
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

    @manager.add_instruction(0xB6, [Registers.A])
    def ora_m(self, register: int) -> None:
        """
        The specified byte is logically ORed bit by bit with the
        contents of the accumulator.
        The carry bit is reset to zero.
        """
        address = join_bytes(self.registers[Registers.H], self.registers[Registers.L])
        value = self.read_memory_byte(address)
        result = self.registers[register] | value
        self.registers[register] = result

        self.set_flags(result)
        self.flags.C = False
        self.cycles += 7

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
        self.cycles += 4

    @manager.add_instruction(0xBE)
    def cmp_m(self) -> None:
        address = join_bytes(self.registers[Registers.H], self.registers[Registers.L])
        self.compare_with_twos_complement(
            self.registers[Registers.A], self.read_memory_byte(address)
        )
        self.cycles += 7

    @manager.add_instruction(0xC0)
    def rnz(self) -> None:
        if not self.flags.Z:
            h, l = self._pop()
            self.PC = join_bytes(h, l)
            self.cycles += 11
            return

        self.cycles += 5

    @manager.add_instruction(0xC1, [Registers.B, Registers.C])
    @manager.add_instruction(0xD1, [Registers.D, Registers.E])
    @manager.add_instruction(0xE1, [Registers.H, Registers.L])
    def pop(self, h: int, l: int) -> None:
        """
        Pop two bytes from the stack and store them in the specified registers pair.
        The stack pointer is incremented by two after the pop.
        """
        high, low = self._pop()
        self.registers[h], self.registers[l] = high, low
        self.cycles += 10

    @manager.add_instruction(0xC2)
    def jnz_addr(self) -> None:
        address = self.fetch_word()
        if not self.flags.Z:
            self.PC = address

        self.cycles += 10

    @manager.add_instruction(0xC3)
    def jmp_addr(self) -> None:
        """
        Jump to the specified address.

        This instruction fetches a 16-bit address from memory and sets the
        program counter (PC) to that address, effectively jumping to the
        instruction at that location.
        """
        address = self.fetch_word()
        self.PC = address
        self.cycles += 10

    @manager.add_instruction(0xC4)
    def cnz_addr(self) -> None:
        address = self.fetch_word()
        if not self.flags.Z:
            h, l = split_word(self.PC)
            self._push(h, l)
            self.PC = address
            self.cycles += 17
            return
        self.cycles += 11

    @manager.add_instruction(0xC5, [Registers.B, Registers.C])
    @manager.add_instruction(0xD5, [Registers.D, Registers.E])
    @manager.add_instruction(0xE5, [Registers.H, Registers.L])
    def push(self, h: int, l: int) -> None:
        """
        Push the contents of the BC register pair onto the stack.

        This method pushes the values stored in the B and C registers onto the stack.
        The value in the C register is pushed first as the low byte, followed by the
        value in the B register as the high byte.
        """
        self._push(self.registers[h], self.registers[l])
        self.cycles += 11

    @manager.add_instruction(0xC6)
    def adi_d8(self) -> None:
        """
        The byte of immediate data is added to the contents
        of the accumulator using two's complement arithmetic.

        Condition bits affected: Carry, Sign, Zero,
        Parity, Auxiliary Carry.
        """
        i_value = self.fetch_byte()
        a_value = self.registers[Registers.A]
        result = i_value + a_value
        new_value = result & 0xFF

        self.registers[Registers.A] = new_value

        self.set_flags(new_value)
        self.set_carry_flag(result)
        self.set_aux_carry_flag(i_value, a_value)

        self.cycles += 7

    @manager.add_instruction(0xC8)
    def rz(self) -> None:
        if self.flags.Z:
            h, l = self._pop()
            self.PC = join_bytes(h, l)
            self.cycles += 11
            return

        self.cycles += 5

    @manager.add_instruction(0xC9)
    def ret(self) -> None:
        """
        Return from a subroutine call by restoring the program counter.

        This method pops two bytes from the stack and uses them to
        restore the program counter (PC) to the address from which
        the subroutine was called. The high byte is popped first,
        followed by the low byte, and they are combined to form the
        complete address.
        """
        h, l = self._pop()
        self.PC = h << 0x08 | l & 0xFF
        self.cycles += 10

    @manager.add_instruction(0xCA)
    def jz_addr(self) -> None:
        address = self.fetch_word()
        if self.flags.Z:
            self.PC = address
        self.cycles += 10

    @manager.add_instruction(0xCC)
    def cz_addr(self) -> None:
        address = self.fetch_word()
        if self.flags.Z:
            h, l = split_word(self.PC)
            self._push(h, l)
            self.PC = address
            self.cycles += 17
            return

        self.cycles += 11

    @manager.add_instruction(0xCD)
    def call_addr(self) -> None:
        """
        Call the subroutine at the specified address.

        This function fetches a 16-bit address from memory and sets the program counter (PC)
        to that address, effectively jumping to the subroutine at that location. Before jumping,
        it pushes the current PC onto the stack to allow returning to the original location after
        the subroutine completes.

        The fetch_word method is used to retrieve the 16-bit address from memory, and the current PC
        is split into high and low bytes and pushed onto the stack.
        """
        address_to_jump = self.fetch_word()
        h, l = split_word(self.PC)
        self._push(h, l)
        self.PC = address_to_jump
        self.cycles += 17

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

    @manager.add_instruction(0xCF)
    def rst_1(self) -> None:
        if self.interrupts_enabled:
            self.interrupts_enabled = False
            h, l = split_word(self.PC)
            self._push(h, l)
            self.PC = 0x08
            self.cycles += 11

    @manager.add_instruction(0xD0)
    def rnc(self) -> None:
        if not self.flags.C:
            h, l = self._pop()
            self.PC = join_bytes(h, l)
            self.cycles += 11
            return
        self.cycles += 5

    @manager.add_instruction(0xD2)
    def jnc_addr(self) -> None:
        address = self.fetch_word()
        if not self.flags.C:
            self.PC = address
        self.cycles += 10

    @manager.add_instruction(0xD3)
    def out_d8(self) -> None:
        port = self.fetch_byte()
        print(f"OUT: Port: {port}, Value: {self.registers[Registers.A]}")
        self.cycles += 10

    @manager.add_instruction(0xD4)
    def cnc_addr(self):
        address = self.fetch_word()
        if not self.flags.C:
            h, l = split_word(self.PC)
            self._push(h, l)
            self.PC = address
            self.cycles += 17
            return
        self.cycles += 11

    @manager.add_instruction(0xD6)
    def sui_d8(self) -> None:
        i_value = self.fetch_byte()
        a_value = self.registers[Registers.A]
        result = a_value - i_value
        new_value = result & 0xFF
        self.registers[Registers.A] = new_value
        self.set_flags(new_value)
        self.set_carry_flag(result)
        # twos complement
        x = (i_value ^ 0xFF) + 0x01
        c = ((x & 0xF) + (a_value & 0xF)) > 0xF
        self.flags.A = c
        self.cycles += 7

    @manager.add_instruction(0xD7)
    def rst_2(self) -> None:
        if self.interrupts_enabled:
            self.interrupts_enabled = False
            h, l = split_word(self.PC)
            self._push(h, l)
            self.PC = 0x10
            self.cycles += 11

    @manager.add_instruction(0xD8)
    def rc(self) -> None:
        if self.flags.C:
            h, l = self._pop()
            self.PC = join_bytes(h, l)
            self.cycles += 11
            return
        self.cycles += 5

    @manager.add_instruction(0xDA)
    def jc_addr(self) -> None:
        address = self.fetch_word()
        if self.flags.C:
            self.PC = address
        self.cycles += 10

    @manager.add_instruction(0xDB)
    def in_d8(self) -> int:
        port = self.fetch_byte()
        if port == 0x01:
            self.registers[Registers.A] = self.port_1
        self.cycles += 10

    @manager.add_instruction(0xDC)
    def cc_addr(self):
        address = self.fetch_word()
        if self.flags.C:
            h, l = split_word(self.PC)
            self._push(h, l)
            self.PC = address
            self.cycles += 17
            return
        self.cycles += 11

    @manager.add_instruction(0xDE)
    def sbi_d8(self) -> None:
        carry = 1 if self.flags.C else 0
        i_value = self.fetch_byte()
        i_value += carry
        i_value &= 0xFF

        a_value = self.registers[Registers.A]
        result = a_value - i_value
        new_value = result & 0xFF

        self.registers[Registers.A] = new_value
        self.set_flags(new_value)
        self.set_carry_flag(result)

        # twos complement
        x = (i_value ^ 0xFF) + 0x01

        c = ((x & 0xF) + (a_value & 0xF)) > 0xF
        self.flags.A = c
        self.cycles += 7

    @manager.add_instruction(0xDF)
    def rst_3(self) -> None:
        if self.interrupts_enabled:
            self.interrupts_enabled = False
            h, l = split_word(self.PC)
            self._push(h, l)
            self.PC = 0x08 * 3
            self.cycles += 11

    @manager.add_instruction(0xE0)
    def rpo(self) -> None:
        if not self.flags.P:
            h, l = self._pop()
            self.PC = join_bytes(h, l)
            self.cycles += 11
            return
        self.cycles += 5

    @manager.add_instruction(0xE2)
    def jpo_addr(self) -> None:
        address = self.fetch_word()
        if self.flags.P:
            self.PC = address
            self.cycles += 17
            return
        self.cycles += 11

    @manager.add_instruction(0xE3)
    def xthl(self) -> None:
        h, l = self.registers[Registers.H], self.registers[Registers.L]
        self.registers[Registers.L] = self.read_memory_byte(self.SP)
        self.registers[Registers.H] = self.read_memory_byte(self.SP + 0x01)
        self.write_memory_word(self.SP, h, l)
        self.cycles += 18

    @manager.add_instruction(0xE4)
    def cpo_addr(self) -> None:
        address = self.fetch_word()
        if not self.flags.P:
            h, l = split_word(self.PC)
            self._push(h, l)
            self.PC = address
            self.cycles += 17
            return
        self.cycles += 11

    @manager.add_instruction(0xE6)
    def ani_d8(self) -> None:
        value1 = self.registers[Registers.A]
        value2 = self.fetch_byte()

        result = value1 & value2
        self.registers[Registers.A] = result

        self.set_flags(result)
        self.flags.C = False
        self.set_aux_carry_flag(value1, value2)
        self.cycles += 7

    @manager.add_instruction(0xE7)
    def rst_4(self) -> None:
        if self.interrupts_enabled:
            self.interrupts_enabled = False
            h, l = split_word(self.PC)
            self._push(h, l)
            self.PC = 0x20
            self.cycles += 11

    @manager.add_instruction(0xE8)
    def rpe(self) -> None:
        if self.flags.P:
            h, l = self._pop()
            self.PC = join_bytes(h, l)
            self.cycles += 11
            return
        self.cycles += 5

    @manager.add_instruction(0xE9)
    def pchl(self) -> None:
        h = self.registers[Registers.H]
        l = self.registers[Registers.L]
        self.PC = join_bytes(h, l)
        self.cycles += 5

    @manager.add_instruction(0xEA)
    def jpe_addr(self) -> None:
        address = self.fetch_word()
        if self.flags.P:
            self.PC = address
            self.cycles += 10
            return
        self.cycles += 5

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

    @manager.add_instruction(0xEC)
    def cpe_addr(self) -> None:
        address = self.fetch_word()
        if self.flags.P:
            h, l = split_word(self.PC)
            self._push(h, l)
            self.PC = address
            self.cycles += 17
            return

        self.cycles += 11

    @manager.add_instruction(0xEE)
    def xri_d8(self):
        value1 = self.registers[Registers.A]
        value2 = self.fetch_byte()

        result = value1 ^ value2
        self.registers[Registers.A] = result

        self.flags.S = (result & 0x80) != 0
        self.flags.Z = (result & 0xFF) == 0x00
        self.flags.P = (bin(result & 0xFF).count("1") % 2) == 0
        self.flags.A = False
        self.flags.C = False
        self.cycles += 7

    @manager.add_instruction(0xEF)
    def rst_5(self) -> None:
        if self.interrupts_enabled:
            self.interrupts_enabled = False
            h, l = split_word(self.PC)
            self._push(h, l)
            self.PC = 0x08 * 5
            self.cycles += 11

    @manager.add_instruction(0xF0)
    def rp(self) -> None:
        if self.flags.P:
            h, l = self._pop()
            self.PC = join_bytes(h, l)
            self.cycles += 11
            return
        self.cycles += 5

    @manager.add_instruction(0xF1)
    def pop_psw(self) -> None:
        self.registers[Registers.A], flags_byte = self._pop()
        self.flags.set_flags(flags_byte)
        self.cycles += 10

    @manager.add_instruction(0xF2)
    def jp_addr(self):
        address = self.fetch_word()
        if not self.flags.S:
            self.PC = address
        self.cycles += 10

    @manager.add_instruction(0xF3)
    def di(self):
        self.interrupts_enabled = False
        self.cycles += 4

    @manager.add_instruction(0xF4)
    def cp_addr(self) -> None:
        address = self.fetch_word()
        if not self.flags.S:
            h, l = split_word(self.PC)
            self._push(h, l)
            self.PC = address
            self.cycles += 17
            return
        self.cycles += 11

    @manager.add_instruction(0xF5)
    def push_psw(self) -> None:
        self._push(self.registers[Registers.A], self.flags.get_flags())
        self.cycles += 11

    @manager.add_instruction(0xF6)
    def ori_d8(self) -> None:
        i_value = self.fetch_byte()
        a_value = self.registers[Registers.A]
        result = a_value | i_value
        self.registers[Registers.A] = result

        self.set_flags(result)
        self.set_carry_flag(result)
        self.set_aux_carry_flag(a_value, i_value)

        self.cycles += 7

    @manager.add_instruction(0xF7)
    def rst_6(self) -> None:
        if self.interrupts_enabled:
            self.interrupts_enabled = False
            h, l = split_word(self.PC)
            self._push(h, l)
            self.PC = 0x30
            self.cycles += 11

    @manager.add_instruction(0xF8)
    def rm(self) -> None:
        if self.flags.S:
            h, l = self._pop()
            self.PC = join_bytes(h, l)
            self.cycles += 11
            return
        self.cycles += 5

    @manager.add_instruction(0xF9)
    def sphl(self) -> None:
        self.SP = join_bytes(self.registers[Registers.H], self.registers[Registers.L])
        self.cycles += 5

    @manager.add_instruction(0xFA)
    def jm_addr(self) -> None:
        address = self.fetch_word()
        if self.flags.S:
            self.PC = address

        self.cycles += 10

    @manager.add_instruction(0xFB)
    def ei(self) -> None:
        self.interrupts_enabled = True
        self.cycles += 4

    @manager.add_instruction(0xFC)
    def cm_addr(self) -> None:
        address = self.fetch_word()
        if self.flags.S:
            h, l = split_word(self.PC)
            self._push(h, l)
            self.PC = address
            self.cycles += 17
            return
        self.cycles += 11

    @manager.add_instruction(0xFE, [Registers.A])
    def cpi_d8(self, register: int) -> None:
        """
        The byte of immediate data is compared to the contents of the accumulator.
        The comparison is performed by internally subtracting the data from the
        accumulator using two's complement arithmetic, leaving the accumulator
        unchanged but setting the condition bits by the result.

        Since a subtract operation is performed, the Carry bit will be set if
        there is no carry out of bit 7.
        """
        self.compare_with_twos_complement(self.registers[register], self.fetch_byte())
        self.cycles += 7

    @manager.add_instruction(0xFF)
    def rst_7(self) -> None:
        if not self.interrupts_enabled:
            self.interrupts_enabled = False
            h, l = split_word(self.PC)
            self._push(h, l)
            self.PC = 0x38
            self.cycles += 11
