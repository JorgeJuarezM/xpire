"""
Intel 8080 CPU implementation.
"""

from cpus.cpu import CPU
from decorators import increment_stack_pointer
from registers.inter_8080 import Registers


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

        self.add_instruction(0x03, self.increment_bc_register)
        self.add_instruction(0x04, self.increment_b_register)
        self.add_instruction(0x06, self.move_immediate_to_register(Registers.B))
        self.add_instruction(0x0E, self.move_immediate_to_register(Registers.C))
        self.add_instruction(0x16, self.move_immediate_to_register(Registers.D))
        self.add_instruction(0x1E, self.move_immediate_to_register(Registers.E))
        self.add_instruction(0x26, self.move_immediate_to_register(Registers.H))
        self.add_instruction(0x2E, self.move_immediate_to_register(Registers.L))
        self.add_instruction(0x31, self.load_immediate_to_stack_pointer)
        self.add_instruction(0x32, self.store_accumulator_to_memory)
        self.add_instruction(0x3A, self.load_memory_address_to_accumulator)
        self.add_instruction(0x3C, self.increment_accumulator)
        self.add_instruction(0x3E, self.move_immediate_to_register(Registers.A))
        self.add_instruction(0xC3, self.jump_to_address)
        self.add_instruction(0xC5, self.push_bc_to_stack)
        self.add_instruction(0xC9, self.return_from_call)
        self.add_instruction(0xCD, self.call_address)
        self.add_instruction(0xE1, self.pop_hl_from_stack)

    def load_memory_address_to_accumulator(self) -> None:
        """
        Load the value at the specified memory address to the accumulator (A register).

        This instruction fetches a 16-bit address from memory and loads the value stored at that address
        to the accumulator. The value is loaded as a byte, not a word.
        """
        address = self.fetch_word()
        self.registers[Registers.A] = self.read_memory_byte(address)

    def jump_to_address(self) -> None:
        """
        Jump to the specified address.

        This instruction fetches a 16-bit address from memory and sets the
        program counter (PC) to that address, effectively jumping to the
        instruction at that location.
        """
        address = self.fetch_word()
        self.PC = address

    def increment_accumulator(self) -> None:
        """
        Increment the accumulator (A register) by one.

        This method increases the value stored in the accumulator by 0x01.
        If the result exceeds 0xFF, it wraps around to 0x00.
        """
        self.registers[Registers.A] += 0x01

    def load_immediate_to_stack_pointer(self) -> None:
        """
        Load a 16-bit address from memory to the stack pointer (SP).

        The stack pointer is set to the value of the 16-bit address fetched from memory.
        """
        self.SP = self.fetch_word()

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

        address = self.fetch_word()
        self.push(self.PC >> 0x08, self.PC & 0x00FF)
        self.PC = address

    def increment_b_register(self) -> None:
        """
        Increment the B register by one.

        This method increments the value in the B register by one. If the
        result is greater than 0xFF, it wraps around to 0x00.
        """
        self.registers[Registers.B] += 0x01

    def increment_bc_register(self) -> None:
        """
        Increment the BC register by one.

        This method increments the value in the BC register by one. If the
        result is greater than 0xFFFF, it wraps around to 0x0000.
        """
        value = self.registers[Registers.B] << 0x08 | self.registers[Registers.C]
        value += 0x01

        if value.bit_length() > 0x10:
            value = 0x00

        self.registers[Registers.B] = value >> 0x08
        self.registers[Registers.C] = value & 0x00FF

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
        self.PC = h << 0x08 | l

    def push(self, high_byte, low_byte) -> None:
        """
        Push a word onto the stack.

        This method decreases the stack pointer by two and stores the
        provided 16-bit value on the stack at the updated stack pointer
        location. The high byte is stored first, followed by the low byte.

        Args:
            high_byte (int): The high byte of the word to push.
            low_byte (int): The low byte of the word to push.
        """

        self.SP -= 0x02
        self.write_memory_word(self.SP, high_byte, low_byte)

    def push_bc_to_stack(self) -> None:
        """
        Push the value of the BC register to the stack.

        This method decrements the stack pointer by two and
        stores the value of the BC register at the new stack
        pointer location.

        """
        self.push(
            self.registers[Registers.B],
            self.registers[Registers.C],
        )

    @increment_stack_pointer()
    def pop(self) -> tuple[int, int]:
        """
        Pop a 16-bit value from the stack.

        This instruction pops two bytes from the stack and returns them as a 16-bit value (i.e. high byte first, low byte second).
        The stack pointer is incremented by two after the pop.
        """
        return self.read_memory_word_bytes(self.SP)

    def pop_hl_from_stack(self) -> None:
        """
        Pop two bytes from the stack and store them in the H and L registers.

        This instruction pops two bytes from the stack and stores them in the H and L registers. The
        value is popped from the stack as a 16-bit value (i.e. high byte first, low byte second) and
        is stored in the H and L registers.

        The stack pointer is incremented by two after the pop.
        """
        self.registers[Registers.H], self.registers[Registers.L] = self.pop()

    def write_memory_byte(self, address, value) -> None:
        """
        Store a byte in memory at the specified address.

        This method takes a 16-bit address and an 8-bit value, and stores the value in memory at the specified address.
        """
        self.memory[address] = value

    def write_memory_word(self, address, high_byte, low_byte) -> None:
        """
        Store a 16-bit value in memory at the specified address.

        This method takes a 16-bit address and a 16-bit value, and stores the value in memory at the specified address.
        The value is stored in memory as a 16-bit value (i.e. high byte first, low byte second).
        """
        self.write_memory_byte(address, high_byte)
        self.write_memory_byte(address + 0x01, low_byte)

    def store_accumulator_to_memory(self) -> None:
        """
        Store the value of the accumulator in memory at the address specified by the next two bytes.

        This instruction fetches a 16-bit address from memory and stores the value of the accumulator at that
        address. The address is fetched as a 16-bit value from memory and the accumulator is stored in memory
        as a byte at that address.
        """
        address = self.fetch_word()
        self.write_memory_byte(address, self.registers[Registers.A])

    def move_immediate_to_register(self, register: int) -> callable:
        """
        Create and return a function to move an immediate value to the specified register.

        This function generates another function that moves the immediate byte
        immediately following the opcode into the specified register. The generated
        function fetches the byte from memory and assigns it to the provided register.

        Args:
            register (int): The register to which the immediate value will be moved.

        Returns:
            Callable: A function that performs the move operation.
        """

        def move_immediate_to_register_func():
            """
            Move the immediate value after the opcode to the register.

            This function moves the byte immediately following the opcode into the
            register specified by the register argument of the outer function. The byte
            is fetched from memory and assigned to the register.
            """
            self.registers[register] = self.fetch_byte()

        return move_immediate_to_register_func
