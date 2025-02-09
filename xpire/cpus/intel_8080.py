"""
Intel 8080 CPU implementation.
"""

import xpire.instructions.intel_8080 as OPCodes
from xpire.cpus.cpu import CPU
from xpire.decorators import increment_stack_pointer
from xpire.instructions.manager import InstructionManager as manager
from xpire.registers.inter_8080 import Registers
from xpire.utils import join_bytes, split_word

# import beepy
# import pygame

# pygame.mixer.init()


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

        self.flags["Z"] = False  # Zero flag
        self.flags["S"] = False  # Sign flag
        self.flags["P"] = False  # Parity flag
        self.flags["C"] = False  # Carry flag
        self.flags["A"] = False  # Aux carry flag

        self.interrupts_enabled = False

    def write_memory_byte(self, address, value) -> None:
        """
        Store a byte in memory at the specified address.

        This method takes a 16-bit address and an 8-bit value, and stores the value in memory at the specified address.
        """
        address = address & 0xFFFF
        self.memory[address] = value

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

    def write_memory_word(self, address, high_byte, low_byte) -> None:
        """
        Store a 16-bit value in memory at the specified address.

        This method takes a 16-bit address and a 16-bit value, and stores the value in memory at the specified address.
        The value is stored in memory as a 16-bit value (i.e. high byte first, low byte second).
        """
        self.write_memory_byte(address, high_byte)
        self.write_memory_byte(address + 0x01, low_byte)

    @increment_stack_pointer()
    def pop(self) -> tuple[int, int]:
        """
        Pop a 16-bit value from the stack.

        This instruction pops two bytes from the stack and returns them as a 16-bit value (i.e. high byte first, low byte second).
        The stack pointer is incremented by two after the pop.
        """
        return self.read_memory_word_bytes(self.SP)

    def set_flags(self, value: int, mask: int = 0xFF) -> None:
        self.flags["Z"] = value == 0x00
        self.flags["S"] = bool(value & 0x80)
        self.flags["P"] = self.check_parity(value, mask)

    def check_parity(self, value: int, mask: int = 0xFF) -> bool:
        return bin(value & mask).count("1") % 2 == 0

    def set_carry_flag(self, value: int, mask: int = 0xFF) -> None:
        self.flags["C"] = value > mask

    def set_aux_carry_flag(self, a: int, b: int, mask: int = 0x0F) -> None:
        result = (a & mask) + (b & mask)
        if result > mask or result < 0x00:
            self.flags["A"] = True
        else:
            self.flags["A"] = False

    @manager.add_instruction(OPCodes.LDA)
    def load_memory_address_to_accumulator(self) -> None:
        """
        Load the value at the specified memory address to the accumulator (A register).

        This instruction fetches a 16-bit address from memory and loads the value stored at that address
        to the accumulator. The value is loaded as a byte, not a word.
        """
        address = self.fetch_word()
        value = self.read_memory_byte(address)
        self.registers[Registers.A] = value
        self.cycles += 7

    @manager.add_instruction(OPCodes.JMP)
    def jump_to_address(self) -> None:
        """
        Jump to the specified address.

        This instruction fetches a 16-bit address from memory and sets the
        program counter (PC) to that address, effectively jumping to the
        instruction at that location.
        """
        address = self.fetch_word()
        self.PC = address
        self.cycles += 10

    @manager.add_instruction(OPCodes.LXI_SP)
    def load_immediate_to_stack_pointer(self) -> None:
        """
        Load a 16-bit address from memory to the stack pointer (SP).

        The stack pointer is set to the value of the 16-bit address fetched from memory.
        """
        self.SP = self.fetch_word()
        self.cycles += 10

    @manager.add_instruction(OPCodes.CALL)
    def call_address(self) -> None:
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
        self.push(h, l)
        self.PC = address_to_jump
        self.cycles += 17

    @manager.add_instruction(OPCodes.RET)
    def return_from_call(self) -> None:
        """
        Return from a subroutine call by restoring the program counter.

        This method pops two bytes from the stack and uses them to
        restore the program counter (PC) to the address from which
        the subroutine was called. The high byte is popped first,
        followed by the low byte, and they are combined to form the
        complete address.
        """
        h, l = self.pop()
        self.PC = h << 0x08 | l & 0xFF
        self.cycles += 10

    @manager.add_instruction(OPCodes.PUSH_BC, [Registers.B, Registers.C])
    @manager.add_instruction(OPCodes.PUSH_DE, [Registers.D, Registers.E])
    @manager.add_instruction(OPCodes.PUSH_HL, [Registers.H, Registers.L])
    def push_to_stack(self, h: int, l: int) -> None:
        """
        Push the contents of the BC register pair onto the stack.

        This method pushes the values stored in the B and C registers onto the stack.
        The value in the C register is pushed first as the low byte, followed by the
        value in the B register as the high byte.
        """
        self.push(self.registers[h], self.registers[l])
        self.cycles += 11

    @manager.add_instruction(OPCodes.POP_BC, [Registers.B, Registers.C])
    @manager.add_instruction(OPCodes.POP_DE, [Registers.D, Registers.E])
    @manager.add_instruction(OPCodes.POP_HL, [Registers.H, Registers.L])
    def pop_from_stack(self, h: int, l: int) -> None:
        """
        Pop two bytes from the stack and store them in the specified registers pair.
        The stack pointer is incremented by two after the pop.
        """
        high, low = self.pop()
        self.registers[h], self.registers[l] = high, low
        self.cycles += 10

    @manager.add_instruction(OPCodes.STA)
    def store_accumulator_to_memory(self) -> None:
        """
        Store the value of the accumulator in memory at the address specified by the next two bytes.

        This instruction fetches a 16-bit address from memory and stores the value of the accumulator at that
        address. The address is fetched as a 16-bit value from memory and the accumulator is stored in memory
        as a byte at that address.
        """
        address = self.fetch_word()
        self.write_memory_byte(address, self.registers[Registers.A])
        self.cycles += 13

    @manager.add_instruction(OPCodes.MVI_A, [Registers.A])
    @manager.add_instruction(OPCodes.MVI_B, [Registers.B])
    @manager.add_instruction(OPCodes.MVI_C, [Registers.C])
    @manager.add_instruction(OPCodes.MVI_D, [Registers.D])
    @manager.add_instruction(OPCodes.MVI_E, [Registers.E])
    @manager.add_instruction(OPCodes.MVI_H, [Registers.H])
    @manager.add_instruction(OPCodes.MVI_L, [Registers.L])
    def move_immediate_to_register(self, register: int) -> callable:
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

    @manager.add_instruction(OPCodes.INR_A, [Registers.A])
    @manager.add_instruction(OPCodes.INR_B, [Registers.B])
    @manager.add_instruction(OPCodes.INR_C, [Registers.C])
    @manager.add_instruction(OPCodes.INR_D, [Registers.D])
    @manager.add_instruction(OPCodes.INR_E, [Registers.E])
    @manager.add_instruction(OPCodes.INR_H, [Registers.H])
    @manager.add_instruction(OPCodes.INR_L, [Registers.L])
    def increment_register(self, register: int) -> None:
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

    @manager.add_instruction(OPCodes.DCR_A, [Registers.A])
    @manager.add_instruction(OPCodes.DCR_B, [Registers.B])
    @manager.add_instruction(OPCodes.DCR_C, [Registers.C])
    @manager.add_instruction(OPCodes.DCR_D, [Registers.D])
    @manager.add_instruction(OPCodes.DCR_E, [Registers.E])
    @manager.add_instruction(OPCodes.DCR_H, [Registers.H])
    @manager.add_instruction(OPCodes.DCR_L, [Registers.L])
    def decrement_register(self, register: int) -> None:
        """
        Decrement the value of the specified register by one.

        Condition bits affected: Zero, Sign, Parity, Auxiliary Carry
        """
        reg_value = self.registers[register]
        result = reg_value - 0x01
        new_value = result & 0xFF
        self.registers[register] = new_value

        self.set_flags(new_value)
        self.set_aux_carry_flag(reg_value, 0x01)

        self.cycles += 5

    @manager.add_instruction(OPCodes.INR_BC, [Registers.B, Registers.C])
    @manager.add_instruction(OPCodes.INR_DE, [Registers.D, Registers.E])
    @manager.add_instruction(OPCodes.INR_HL, [Registers.H, Registers.L])
    def increment_register_pair(self, h: int, l: int) -> None:
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

        self.set_flags(new_value, mask=0x00FF)
        self.set_aux_carry_flag(value, 0x01, mask=0x000F)

        self.cycles += 5

    @manager.add_instruction(OPCodes.LXI_BC, [Registers.B, Registers.C])
    @manager.add_instruction(OPCodes.LXI_DE, [Registers.D, Registers.E])
    @manager.add_instruction(OPCodes.LXI_HL, [Registers.H, Registers.L])
    def load_immediate_to_registry_pair(self, h: int, l: int) -> None:
        self.registers[l] = self.fetch_byte()
        self.registers[h] = self.fetch_byte()
        self.cycles += 10

    @manager.add_instruction(OPCodes.LDAX_BC, [Registers.B, Registers.C])
    @manager.add_instruction(OPCodes.LDAX_DE, [Registers.D, Registers.E])
    def load_address_from_register_to_accumulator(self, h: int, l: int) -> None:
        address_l = self.registers[l]
        address_h = self.registers[h]
        address = join_bytes(address_h, address_l)
        self.registers[Registers.A] = self.read_memory_byte(address)
        self.cycles += 7

    @manager.add_instruction(OPCodes.MOV_M_A, [Registers.A])
    @manager.add_instruction(OPCodes.MOV_M_B, [Registers.B])
    def move_register_to_hl_memory(self, register: int) -> None:
        address = join_bytes(self.registers[Registers.H], self.registers[Registers.L])
        self.write_memory_byte(address, self.registers[register])
        self.cycles += 10

    @manager.add_instruction(OPCodes.JNZ)
    def jump_if_not_zero(self) -> None:
        address = self.fetch_word()
        # if self.PC in [0x0AE1, 0x0AA5]:
        #     return

        if not self.flags["Z"]:
            print(f"Salta: {self.PC:04x} -> {address:04x}")
            self.PC = address

        self.cycles += 10

    @manager.add_instruction(OPCodes.MVI_M)
    def move_immediate_to_hl_memory(self) -> None:
        address = join_bytes(self.registers[Registers.H], self.registers[Registers.L])
        self.write_memory_byte(address, self.fetch_byte())
        self.cycles += 10

    @manager.add_instruction(OPCodes.MOV_A_B, [Registers.B, Registers.A])
    @manager.add_instruction(OPCodes.MOV_A_C, [Registers.C, Registers.A])
    @manager.add_instruction(OPCodes.MOV_A_D, [Registers.D, Registers.A])
    @manager.add_instruction(OPCodes.MOV_A_E, [Registers.E, Registers.A])
    @manager.add_instruction(OPCodes.MOV_A_H, [Registers.H, Registers.A])
    @manager.add_instruction(OPCodes.MOV_A_L, [Registers.L, Registers.A])
    @manager.add_instruction(OPCodes.MOV_B_A, [Registers.A, Registers.B])
    @manager.add_instruction(OPCodes.MOV_C_A, [Registers.A, Registers.C])
    @manager.add_instruction(OPCodes.MOV_D_A, [Registers.A, Registers.D])
    @manager.add_instruction(OPCodes.MOV_E_A, [Registers.A, Registers.E])
    @manager.add_instruction(OPCodes.MOV_H_A, [Registers.A, Registers.H])
    @manager.add_instruction(OPCodes.MOV_L_A, [Registers.A, Registers.L])
    @manager.add_instruction(OPCodes.MOV_B_H, [Registers.H, Registers.B])
    def move_register_to_register(self, src: int, dst: int) -> None:
        self.registers[dst] = self.registers[src]
        self.cycles += 5

    @manager.add_instruction(OPCodes.CPI_A, [Registers.A])
    def compare_register_with_immediate(self, register: int) -> None:
        value = self.fetch_byte()
        a_value = self.registers[register]
        result = a_value - value

        self.set_flags(result & 0xFF)
        self.flags["C"] = value > a_value
        if a_value & 0x80 ^ value & 0x80:
            self.flags["C"] = not self.flags["C"]

        self.cycles += 7

    @manager.add_instruction(OPCodes.DAD_DE, [Registers.D, Registers.E])
    @manager.add_instruction(OPCodes.DAD_HL, [Registers.H, Registers.L])
    @manager.add_instruction(OPCodes.DAD_BC, [Registers.B, Registers.C])
    def sum_register_pair_with_hl(self, h: int, l: int) -> None:
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

    @manager.add_instruction(OPCodes.DAD_SP)
    def sum_register_pair_with_self(self) -> None:
        h_value, l_value = split_word(self.SP)

        value1 = join_bytes(h_value, l_value)
        value2 = join_bytes(self.registers[Registers.H], self.registers[Registers.L])

        result = value1 + value2
        new_value = result & 0xFFFF
        self.registers[Registers.H], self.registers[Registers.L] = split_word(new_value)

        self.set_carry_flag(result, mask=0xFFFF)

        self.cycles += 10

    @manager.add_instruction(
        OPCodes.XCHG, [Registers.H, Registers.L, Registers.D, Registers.E]
    )
    def exchange_register_pairs(self, h: int, l: int, d: int, e: int) -> None:
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

    @manager.add_instruction(OPCodes.OUT)
    def out_to_port(self) -> None:
        print("=========== OUT ============", end="")
        port = self.fetch_byte()
        print(f"Port: {port} Value: {chr(self.registers[Registers.A])}")
        # raise NotImplementedError
        # sound = pygame.mixer.Sound("beep-01a.wav")
        # sound.play()
        # self.registers[Registers.A] = 0

        self.cycles += 10

    @manager.add_instruction(OPCodes.RNC)
    def return_if_not_carry(self) -> None:
        h, l = self.pop()
        if not self.flags["C"]:
            self.PC = join_bytes(h, l)

        self.cycles += 13

    @manager.add_instruction(OPCodes.RC)
    def return_if_carry(self) -> None:
        h, l = self.pop()
        if self.flags["C"]:
            self.PC = join_bytes(h, l)

        self.cycles += 13

    @manager.add_instruction(OPCodes.LHLD)
    def load_address_and_next_to_hl(self) -> None:
        address1 = self.fetch_word()
        address2 = (address1 + 0x01) & 0xFFFF

        l = self.read_memory_byte(address1)
        h = self.read_memory_byte(address2)

        self.registers[Registers.L] = l
        self.registers[Registers.H] = h

        self.cycles += 16

    @manager.add_instruction(OPCodes.ORA_B, [Registers.B])
    @manager.add_instruction(OPCodes.ORA_C, [Registers.C])
    @manager.add_instruction(OPCodes.ORA_H, [Registers.H])
    def register_or_with_accumulator(self, register: int) -> None:
        """
        The specified byte is logically ORed bit by bit with
        the contents of the accumulator.

        The carry bit is reset to zero.

        Condition bits affected: Carry, zero, sign, parity.
        """
        result = self.registers[Registers.A] | self.registers[register]
        self.registers[Registers.A] = result

        self.set_flags(result)
        self.flags["C"] = False

        self.cycles += 4

    @manager.add_instruction(OPCodes.ORA_M, [Registers.A])
    def register_or_with_memory(self, register: int) -> None:
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
        self.flags["C"] = False

        self.cycles += 7

    @manager.add_instruction(OPCodes.DCX_HL, [Registers.H, Registers.L])
    def decrement_register_pair(self, h: int, l: int) -> None:
        """
        The 16-bit number held in the specified register pair
        is decremented by one.

        The result replaces the contents of the register pair.

        Condition bits affected: None.
        """
        value = join_bytes(self.registers[h], self.registers[l])
        value = (value - 0x01) & 0xFFFF

        high_byte, low_byte = split_word(value)

        self.registers[h] = high_byte
        self.registers[l] = low_byte

        self.cycles += 5

    @manager.add_instruction(OPCodes.JZ)
    def jump_if_zero(self) -> None:
        address = self.fetch_word()
        if self.flags["Z"]:
            self.PC = address

        self.cycles += 10

    @manager.add_instruction(OPCodes.ADD_D, [Registers.D])
    def add_to_accumulator(self, register: int) -> None:
        """
        The specified byte is added to the contents of the accumulator
        using two's complement arithmetic.

        Condition bits affected: Carry, Sign, Zero, Parity, Auxiliary Carry.
        """
        value_1 = self.registers[register]
        value_2 = self.registers[Registers.A]
        result = value_1 + value_2
        new_value = result & 0xFF

        self.set_flags(new_value)
        self.set_carry_flag(result)
        self.set_aux_carry_flag(value_1, value_2)

        self.registers[Registers.A] = new_value

        self.cycles += 4

    @manager.add_instruction(OPCodes.JPE)
    def jump_if_parity(self) -> None:
        address = self.fetch_word()
        if self.flags.get("P"):
            self.PC = address

        self.cycles += 10

    @manager.add_instruction(OPCodes.MOV_A_M, [Registers.A])
    @manager.add_instruction(OPCodes.MOV_C_M, [Registers.C])
    @manager.add_instruction(OPCodes.MOV_D_M, [Registers.D])
    @manager.add_instruction(OPCodes.MOV_E_M, [Registers.E])
    @manager.add_instruction(OPCodes.MOV_H_M, [Registers.H])
    @manager.add_instruction(OPCodes.MOV_B_M, [Registers.B])
    def move_memory_hl_to_register(self, register: int) -> None:
        address = join_bytes(self.registers[Registers.H], self.registers[Registers.L])
        self.registers[register] = self.read_memory_byte(address)

        self.cycles += 7
        # Todo: Implement flags

    @manager.add_instruction(OPCodes.RAR)
    def rotate_right_a_through_carry(self) -> None:
        """
        The contents of the accumulator are rotated one bit position to the right.

        The low-order bit of the accumulator replaces the carry bit,
        while the carry bit replaces the high-order bit of the accumulator.

        Condition bits affected: Carry.
        """
        carry = 1 if self.flags["C"] else 0
        accumulator = self.registers[Registers.A] & 0xFF

        # Obtener el bit menos significativo (LSB) del acumulador
        new_carry = accumulator & 0x01

        # Rotar el acumulador a la derecha
        # El bit de carry se convierte en el bit más significativo (MSB)
        accumulator = (accumulator >> 1) | (carry << 7)

        # Asegurarse de que el acumulador siga siendo de 8 bits
        accumulator = accumulator & 0xFF

        self.registers[Registers.A] = accumulator
        self.flags["C"] = True if new_carry else False

        self.cycles += 4

    @manager.add_instruction(OPCodes.RRC)
    def rotate_right_a(self) -> None:
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
        self.flags["C"] = True if new_carry else False

        self.cycles += 4

    @manager.add_instruction(OPCodes.JNC)
    def jump_if_not_carry(self) -> None:
        address = self.fetch_word()
        if not self.flags["C"]:
            self.PC = address

        self.cycles += 10

    @manager.add_instruction(OPCodes.JC)
    def jump_if_carry(self) -> None:
        address = self.fetch_word()
        if self.flags["C"]:
            self.PC = address

        self.cycles += 10

    @manager.add_instruction(OPCodes.PUSH_PSW)
    def push_processor_state_word(self) -> None:
        flags_byte = self.flags.get("S") << 0x07
        flags_byte |= self.flags.get("Z") << 0x06
        flags_byte |= self.flags.get("A") << 0x04
        flags_byte |= self.flags.get("P") << 0x02
        flags_byte |= self.flags.get("C") << 0x00

        self.push(self.registers[Registers.A], flags_byte)

        self.cycles += 11

    @manager.add_instruction(OPCodes.POP_PSW)
    def pop_processor_state_word(self) -> None:
        self.registers[Registers.A], flags_byte = self.pop()
        self.flags["S"] = bool((flags_byte >> 0x07) & 0x01)
        self.flags["Z"] = bool((flags_byte >> 0x06) & 0x01)
        self.flags["A"] = bool((flags_byte >> 0x04) & 0x01)
        self.flags["P"] = bool((flags_byte >> 0x02) & 0x01)
        self.flags["C"] = bool((flags_byte >> 0x00) & 0x01)

        self.cycles += 10

    @manager.add_instruction(OPCodes.ANI)
    def accumulator_and_immediate(self) -> None:
        value1 = self.registers[Registers.A]
        value2 = self.fetch_byte()

        result = value1 & value2
        self.registers[Registers.A] = result

        self.flags["C"] = False
        self.set_flags(result)

        self.cycles += 4

    @manager.add_instruction(OPCodes.JM)
    def jump_if_minus(self) -> None:
        address = self.fetch_word()
        if self.flags["S"]:
            self.PC = address

        self.cycles += 10

    @manager.add_instruction(OPCodes.ADI)
    def add_immediate_to_accumulator(self) -> None:
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

    @manager.add_instruction(OPCodes.XRA, [Registers.A, Registers.A])
    def apply_xor_to_registers(self, r1: int, r2: int) -> None:
        """
        The specified byte is EXCLUSIVE-ORed bit by bit
        with the contents of the accumulator.

        The Carry bit is reset to zero.

        Condition bits affected: Carry, Zero, Sign, Parity, Auxiliary Carry
        """
        value1 = self.registers[r1]
        value2 = self.registers[r2]

        result = value1 ^ value2
        self.registers[r1] = result

        self.flags["C"] = False
        self.set_flags(result)
        self.set_aux_carry_flag(value1, value2)

        self.cycles += 4

    @manager.add_instruction(OPCodes.EI)
    def enable_interrupts(self) -> None:
        self.interrupts_enabled = True

        self.cycles += 4

    @manager.add_instruction(OPCodes.ANA_A, [Registers.A, Registers.A])
    def register_and_register(self, r1: int, r2: int) -> None:
        """
        The specified byte is logically ANDed bit by bit
        with the contents of the accumulator.

        The Carry bit is reset to zero.

        Condition bits affected: Carry, Zero, Sign, Parity
        """
        value1 = self.registers[r1]
        value2 = self.registers[r2]
        result = value1 & value2
        self.registers[r1] = result

        self.flags["C"] = False
        self.set_flags(result)

        self.cycles += 4

    @manager.add_instruction(OPCodes.STC)
    def set_carry(self):
        self.flags["C"] = True

        self.cycles += 4

    @manager.add_instruction(OPCodes.RZ)
    def return_if_zero(self) -> None:
        h, l = self.pop()
        if self.flags["Z"]:
            self.PC = join_bytes(h, l)

        self.cycles += 11

    @manager.add_instruction(OPCodes.RNZ)
    def return_if_not_zero(self) -> None:
        h, l = self.pop()
        if not self.flags["Z"]:
            self.PC = join_bytes(h, l)

        self.cycles += 11

    @manager.add_instruction(OPCodes.IN)
    def input(self) -> int:
        port = self.fetch_byte()
        print(f"Port: {port} Value: {chr(self.registers[Registers.A])}")
        # self.registers[Registers.A] = 0x00
        # raise NotImplementedError

        self.cycles += 10

    @manager.add_instruction(OPCodes.XTHL)
    def exchange_sp_hl(self) -> None:
        h, l = self.registers[Registers.H], self.registers[Registers.L]

        sp_value = self.read_memory_byte(self.SP)
        next_sp_value = self.read_memory_byte(self.SP + 0x01)

        _l = sp_value
        _h = next_sp_value

        self.registers[Registers.H] = _h
        self.registers[Registers.L] = _l
        self.SP = l

        self.cycles += 18

    @manager.add_instruction(OPCodes.PCHL)
    def load_stack_pointer(self) -> None:
        h = self.registers[Registers.H]
        l = self.registers[Registers.L]
        self.PC = join_bytes(h, l)

        self.cycles += 5

    @manager.add_instruction(OPCodes.DCR_M)
    def decrement_memory_byte(self) -> None:
        h = self.registers[Registers.H]
        l = self.registers[Registers.L]
        value = self.read_memory_byte(join_bytes(h, l))
        result = value - 0x01
        new_value = result & 0xFF
        self.write_memory_byte(join_bytes(h, l), new_value)

        self.set_flags(new_value)
        self.set_aux_carry_flag(value, 0x01)

        self.cycles += 10

    @manager.add_instruction(OPCodes.CZ)
    def call_if_zero(self) -> None:
        address = self.fetch_word()
        if self.flags["Z"]:
            self.push(self.PC)
            self.PC = address

        self.cycles += 17

    @manager.add_instruction(OPCodes.RST_1)
    def rst_1(self) -> None:
        self.interrupts_enabled = False
        self.push(self.PC >> 0x08, self.PC & 0xFF)
        self.PC = 0x08
        self.cycles += 11

    @manager.add_instruction(OPCodes.RST_2)
    def rst_2(self) -> None:
        self.interrupts_enabled = False
        self.push(self.PC >> 0x08, self.PC & 0xFF)
        self.PC = 0x10
        self.cycles += 11
