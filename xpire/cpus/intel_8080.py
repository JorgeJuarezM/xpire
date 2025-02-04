"""
Intel 8080 CPU implementation.
"""

import xpire.instructions.intel_8080 as OPCodes
from xpire.cpus.cpu import CPU
from xpire.decorators import increment_stack_pointer
from xpire.instructions.manager import InstructionManager as manager
from xpire.registers.inter_8080 import Registers
from xpire.utils import increment_bytes_pair, join_bytes, split_word


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

        self.flags["Z"] = False

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

    @manager.add_instruction(OPCodes.LDA)
    def load_memory_address_to_accumulator(self) -> None:
        """
        Load the value at the specified memory address to the accumulator (A register).

        This instruction fetches a 16-bit address from memory and loads the value stored at that address
        to the accumulator. The value is loaded as a byte, not a word.
        """
        address = self.fetch_word()
        self.registers[Registers.A] = self.read_memory_byte(address)

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

    @manager.add_instruction(OPCodes.LXI_SP)
    def load_immediate_to_stack_pointer(self) -> None:
        """
        Load a 16-bit address from memory to the stack pointer (SP).

        The stack pointer is set to the value of the 16-bit address fetched from memory.
        """
        self.SP = self.fetch_word()

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

    @manager.add_instruction(OPCodes.POP_BC, [Registers.B, Registers.C])
    @manager.add_instruction(OPCodes.POP_DE, [Registers.D, Registers.E])
    @manager.add_instruction(OPCodes.POP_HL, [Registers.H, Registers.L])
    def pop_from_stack(self, h: int, l: int) -> None:
        """
        Pop two bytes from the stack and store them in the specified registers pair.
        The stack pointer is incremented by two after the pop.
        """
        self.registers[h], self.registers[l] = self.pop()

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

    @manager.add_instruction(OPCodes.INC_A, [Registers.A])
    @manager.add_instruction(OPCodes.INC_B, [Registers.B])
    @manager.add_instruction(OPCodes.INC_C, [Registers.C])
    @manager.add_instruction(OPCodes.INC_D, [Registers.D])
    @manager.add_instruction(OPCodes.INC_E, [Registers.E])
    @manager.add_instruction(OPCodes.INC_H, [Registers.H])
    @manager.add_instruction(OPCodes.INC_L, [Registers.L])
    def increment_register(self, register: int) -> None:
        """
        Increment the value of the specified register by one.

        This method increases the value stored in the specified register by 0x01.
        """
        self.registers[register] += 0x01

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

        This method decreases the value stored in the specified register by 0x01.
        """
        new_value = self.registers[register] - 0x01
        self.registers[register] = new_value & 0xFF

    @manager.add_instruction(OPCodes.INR_BC, [Registers.B, Registers.C])
    @manager.add_instruction(OPCodes.INR_DE, [Registers.D, Registers.E])
    @manager.add_instruction(OPCodes.INR_HL, [Registers.H, Registers.L])
    def increment_register_pair(self, h: int, l: int) -> None:
        high_byte, low_byte = increment_bytes_pair(
            self.registers[h],
            self.registers[l],
        )

        self.registers[h] = high_byte
        self.registers[l] = low_byte

    @manager.add_instruction(OPCodes.LXI_BC, [Registers.B, Registers.C])
    @manager.add_instruction(OPCodes.LXI_DE, [Registers.D, Registers.E])
    @manager.add_instruction(OPCodes.LXI_HL, [Registers.H, Registers.L])
    def load_immediate_to_registry_pair(self, h: int, l: int) -> None:
        self.registers[l] = self.fetch_byte()
        self.registers[h] = self.fetch_byte()

    @manager.add_instruction(OPCodes.LDAX_BC, [Registers.B, Registers.C])
    @manager.add_instruction(OPCodes.LDAX_DE, [Registers.D, Registers.E])
    def load_address_from_register_to_accumulator(self, h: int, l: int) -> None:
        address_l = self.registers[l]
        address_h = self.registers[h]
        address = join_bytes(address_h, address_l)
        self.registers[Registers.A] = self.read_memory_byte(address)

    @manager.add_instruction(OPCodes.MOV_M_A, [Registers.A])
    def move_register_to_hl_memory(self, register: int) -> None:
        address = join_bytes(self.registers[Registers.H], self.registers[Registers.L])
        self.write_memory_byte(address, self.registers[register])

    @manager.add_instruction(OPCodes.JNZ)
    def jump_if_not_zero(self) -> None:
        address = self.fetch_word()
        if not self.flags["Z"]:
            self.pc = address

    @manager.add_instruction(OPCodes.MVI_M)
    def move_immediate_to_hl_memory(self) -> None:
        address = join_bytes(self.registers[Registers.H], self.registers[Registers.L])
        self.write_memory_byte(address, self.fetch_byte())

    @manager.add_instruction(OPCodes.MOV_D_A, [Registers.A, Registers.D])
    @manager.add_instruction(OPCodes.MOV_L_A, [Registers.A, Registers.L])
    @manager.add_instruction(OPCodes.MOV_A_H, [Registers.H, Registers.A])
    @manager.add_instruction(OPCodes.MOV_A_L, [Registers.L, Registers.A])
    def move_register_to_register(self, src: int, dst: int) -> None:
        self.registers[dst] = self.registers[src]

    @manager.add_instruction(OPCodes.CPI_A, [Registers.A])
    def compare_register_with_immediate(self, register: int) -> None:
        value = self.fetch_byte()

        # Todo: Implement flags
        self.flags["Z"] = self.registers[register] == value
        self.flags["C"] = self.registers[register] < value
        self.flags["S"] = self.registers[register] < 0
        self.flags["P"] = self.registers[register] % 2 == 1

    @manager.add_instruction(OPCodes.DAD_DE, [Registers.D, Registers.E])
    @manager.add_instruction(OPCodes.DAD_HL, [Registers.H, Registers.L])
    def sum_register_pair_with_self(self, h: int, l: int) -> None:
        h_value = self.registers[h]
        l_value = self.registers[l]

        value1 = join_bytes(h_value, l_value)
        value2 = join_bytes(self.registers[Registers.H], self.registers[Registers.L])

        result = value1 + value2
        result_no_overflow = result & 0xFFFF
        self.registers[Registers.H], self.registers[Registers.L] = split_word(
            result_no_overflow
        )

        self.flags["C"] = result > 0xFFFF

    @manager.add_instruction(OPCodes.DAD_SP)
    def sum_register_pair_with_self(self) -> None:
        h_value, l_value = split_word(self.SP)

        value1 = join_bytes(h_value, l_value)
        value2 = join_bytes(self.registers[Registers.H], self.registers[Registers.L])

        result = value1 + value2
        result_no_overflow = result & 0xFFFF
        self.registers[Registers.H], self.registers[Registers.L] = split_word(
            result_no_overflow
        )

        self.flags["C"] = result > 0xFFFF

    @manager.add_instruction(
        OPCodes.XCHG, [Registers.H, Registers.L, Registers.D, Registers.E]
    )
    def exchange_register_pairs(self, h: int, l: int, d: int, e: int) -> None:
        h1 = self.registers[h]
        l1 = self.registers[l]
        d1 = self.registers[d]
        e1 = self.registers[e]

        self.registers[h] = d1
        self.registers[l] = e1
        self.registers[d] = h1
        self.registers[e] = l1

    @manager.add_instruction(OPCodes.OUT)
    def out_to_port(self) -> None:
        print("=========== OUT ============", end="")
        port = self.fetch_byte()
        print(f"Port: {port} Value: {chr(self.fetch_byte())}")

    @manager.add_instruction(OPCodes.RNC)
    def return_if_not_carry(self) -> None:
        if not self.flags["C"]:
            self.pc = join_bytes(self.pop())

    @manager.add_instruction(OPCodes.LHLD)
    def load_address_and_next_to_hl(self) -> None:
        address1 = self.fetch_word()
        address2 = (address1 + 0x01) & 0xFFFF

        l = self.read_memory_byte(address1)
        h = self.read_memory_byte(address2)

        self.registers[Registers.L] = l
        self.registers[Registers.H] = h

    @manager.add_instruction(OPCodes.ORA, [Registers.H, Registers.L])
    def register_or_with_accumulator(self, h, l) -> None:
        hl = join_bytes(self.registers[h], self.registers[l])
        self.registers[Registers.A] |= hl

        # Todo: Implement flags
        self.flags["Z"] = self.registers[Registers.A] == 0
        self.flags["S"] = self.registers[Registers.A] < 0
        self.flags["P"] = self.registers[Registers.A] % 2 == 1

    @manager.add_instruction(OPCodes.DCX_HL, [Registers.H, Registers.L])
    def decrement_register_pair(self, h: int, l: int) -> None:
        value = join_bytes(self.registers[h], self.registers[l])
        value = (value - 0x01) & 0xFFFF

        high_byte, low_byte = split_word(value)

        self.registers[h] = high_byte
        self.registers[l] = low_byte

    @manager.add_instruction(OPCodes.JZ)
    def jump_if_zero(self) -> None:
        address = self.fetch_word()
        if self.flags["Z"]:
            self.PC = address

    @manager.add_instruction(OPCodes.ADD_D, [Registers.D])
    def add_to_accumulator(self, register: int) -> None:
        result = self.registers[register] + self.registers[Registers.A]

        # Todo: Implement flags
        self.flags["Z"] = result == 0
        self.flags["S"] = result < 0
        self.flags["P"] = result % 2 == 1
        self.flags["C"] = result > 0xFF

        self.registers[Registers.A] = result
