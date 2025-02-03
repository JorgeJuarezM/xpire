"""
Intel 8080 CPU implementation.
"""

import xpire.instructions.intel_8080 as OPCodes
from xpire.cpus.cpu import CPU
from xpire.instructions.manager import InstructionManager as manager
from xpire.decorators import increment_stack_pointer
from xpire.registers.inter_8080 import Registers
from xpire.utils import increment_bytes_pair, split_word


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

    @manager.add_instruction(opcode=OPCodes.LDA)
    def load_memory_address_to_accumulator(self) -> None:
        """
        Load the value at the specified memory address to the accumulator (A register).

        This instruction fetches a 16-bit address from memory and loads the value stored at that address
        to the accumulator. The value is loaded as a byte, not a word.
        """
        address = self.fetch_word()
        self.registers[Registers.A] = self.read_memory_byte(address)

    @manager.add_instruction(opcode=OPCodes.JMP)
    def jump_to_address(self) -> None:
        """
        Jump to the specified address.

        This instruction fetches a 16-bit address from memory and sets the
        program counter (PC) to that address, effectively jumping to the
        instruction at that location.
        """
        address = self.fetch_word()
        self.PC = address

    @manager.add_instruction(opcode=OPCodes.LXI_SP)
    def load_immediate_to_stack_pointer(self) -> None:
        """
        Load a 16-bit address from memory to the stack pointer (SP).

        The stack pointer is set to the value of the 16-bit address fetched from memory.
        """
        self.SP = self.fetch_word()

    @manager.add_instruction(opcode=OPCodes.CALL)
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

    @manager.add_instruction(opcode=OPCodes.RET)
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

    @manager.add_instruction(
        opcode=OPCodes.PUSH_BC, registers=[Registers.B, Registers.C]
    )
    @manager.add_instruction(
        opcode=OPCodes.PUSH_DE, registers=[Registers.D, Registers.E]
    )
    @manager.add_instruction(
        opcode=OPCodes.PUSH_HL, registers=[Registers.H, Registers.L]
    )
    def push_to_stack(self, h: int, l: int) -> None:
        """
        Push the contents of the BC register pair onto the stack.

        This method pushes the values stored in the B and C registers onto the stack.
        The value in the C register is pushed first as the low byte, followed by the
        value in the B register as the high byte.
        """
        self.push(self.registers[h], self.registers[l])

    @increment_stack_pointer()
    def pop(self) -> tuple[int, int]:
        """
        Pop a 16-bit value from the stack.

        This instruction pops two bytes from the stack and returns them as a 16-bit value (i.e. high byte first, low byte second).
        The stack pointer is incremented by two after the pop.
        """
        return self.read_memory_word_bytes(self.SP)

    @manager.add_instruction(
        opcode=OPCodes.POP_BC, registers=[Registers.B, Registers.C]
    )
    @manager.add_instruction(
        opcode=OPCodes.POP_DE, registers=[Registers.D, Registers.E]
    )
    @manager.add_instruction(
        opcode=OPCodes.POP_HL, registers=[Registers.H, Registers.L]
    )
    def pop_from_stack(self, h: int, l: int) -> None:
        """
        Pop two bytes from the stack and store them in the specified registers pair.
        The stack pointer is incremented by two after the pop.
        """
        self.registers[h], self.registers[l] = self.pop()

    def write_memory_byte(self, address, value) -> None:
        """
        Store a byte in memory at the specified address.

        This method takes a 16-bit address and an 8-bit value, and stores the value in memory at the specified address.
        """
        address = address & 0xFFFF
        self.memory[address] = value

    def write_memory_word(self, address, high_byte, low_byte) -> None:
        """
        Store a 16-bit value in memory at the specified address.

        This method takes a 16-bit address and a 16-bit value, and stores the value in memory at the specified address.
        The value is stored in memory as a 16-bit value (i.e. high byte first, low byte second).
        """
        self.write_memory_byte(address, high_byte)
        self.write_memory_byte(address + 0x01, low_byte)

    @manager.add_instruction(opcode=OPCodes.STA)
    def store_accumulator_to_memory(self) -> None:
        """
        Store the value of the accumulator in memory at the address specified by the next two bytes.

        This instruction fetches a 16-bit address from memory and stores the value of the accumulator at that
        address. The address is fetched as a 16-bit value from memory and the accumulator is stored in memory
        as a byte at that address.
        """
        address = self.fetch_word()
        self.write_memory_byte(address, self.registers[Registers.A])

    @manager.add_instruction(opcode=OPCodes.MVI_A, registers=[Registers.A])
    @manager.add_instruction(opcode=OPCodes.MVI_B, registers=[Registers.B])
    @manager.add_instruction(opcode=OPCodes.MVI_C, registers=[Registers.C])
    @manager.add_instruction(opcode=OPCodes.MVI_D, registers=[Registers.D])
    @manager.add_instruction(opcode=OPCodes.MVI_E, registers=[Registers.E])
    @manager.add_instruction(opcode=OPCodes.MVI_H, registers=[Registers.H])
    @manager.add_instruction(opcode=OPCodes.MVI_L, registers=[Registers.L])
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

    @manager.add_instruction(opcode=OPCodes.INC_A, registers=[Registers.A])
    @manager.add_instruction(opcode=OPCodes.INC_B, registers=[Registers.B])
    @manager.add_instruction(opcode=OPCodes.INC_C, registers=[Registers.C])
    @manager.add_instruction(opcode=OPCodes.INC_D, registers=[Registers.D])
    @manager.add_instruction(opcode=OPCodes.INC_E, registers=[Registers.E])
    @manager.add_instruction(opcode=OPCodes.INC_H, registers=[Registers.H])
    @manager.add_instruction(opcode=OPCodes.INC_L, registers=[Registers.L])
    def increment_register(self, register: int) -> None:
        """
        Increment the value of the specified register by one.

        This method increases the value stored in the specified register by 0x01.
        """
        self.registers[register] += 0x01

    @manager.add_instruction(
        opcode=OPCodes.INR_BC, registers=[Registers.B, Registers.C]
    )
    @manager.add_instruction(
        opcode=OPCodes.INR_DE, registers=[Registers.D, Registers.E]
    )
    @manager.add_instruction(
        opcode=OPCodes.INR_HL, registers=[Registers.H, Registers.L]
    )
    def increment_register_pair(self, h: int, l: int) -> None:
        high_byte, low_byte = increment_bytes_pair(
            self.registers[h],
            self.registers[l],
        )

        self.registers[h] = high_byte
        self.registers[l] = low_byte

    @manager.add_instruction(
        opcode=OPCodes.LXI_BC, registers=[Registers.B, Registers.C]
    )
    @manager.add_instruction(
        opcode=OPCodes.LXI_DE, registers=[Registers.D, Registers.E]
    )
    @manager.add_instruction(
        opcode=OPCodes.LXI_HL, registers=[Registers.H, Registers.L]
    )
    def load_immediate_to_registry_pair(self, h: int, l: int) -> None:
        self.registers[l] = self.fetch_byte()
        self.registers[h] = self.fetch_byte()
