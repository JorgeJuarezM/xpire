import sys
from memory import Memory


class SystemHalt(Exception):
    pass


class CPU:

    # Registers
    A: bytes  # Accumulator
    B: bytes  # Base
    C: bytes  # Counter
    D: bytes  # Data

    # Flags
    class Flags:
        Z: bool = False  # Zero
        S: bool = False  # Sign
        O: bool = False  # Overflow
        C: bool = False  # Carry

    # Stack Pointer
    SP: bytes

    # Program Counter
    PC: bytes

    # Stack
    STACK: bytes

    # fmt: off
    instructions = {
        0x04: lambda self: self._increment_register("B"),           # INR b
        0x06: lambda self: self._move_inmediate_to_register("B"),   # MVI b, #
        0x0D: lambda self: self._decrement_register("C"),           # DCR c
        0x0E: lambda self: self._move_inmediate_to_register("C"),   # MVI c, #
        0x16: lambda self: self._move_inmediate_to_register("D"),   # MVI d, #
        0x1E: lambda self: self._move_inmediate_to_register("E"),   # MVI e, #
        0x3C: lambda self: self._increment_register("A"),           # INR a
        0x3E: lambda self: self._move_inmediate_to_register("A"),   # MVI a, #
        0x47: lambda self: self._mov_reg_a_to_reg_b(),              # MOV b, a
        0x76: lambda self: self._system_halt(),                     # HLT
        0x78: lambda self: self._mov_reg_b_to_reg_a(),              # MOV a, b
        0x80: lambda self: self._add_to_a_from_register("B"),       # ADD b
        0xC2: lambda self: self._jump_if_not_zero(),                # JNZ
    }  # fmt: on

    def __init__(self, memory: Memory):

        self.A = self.B = self.C = self.D = 0x00
        self.SP = self.PC = self.STACK = 0x00
        self.memory = memory

    def _add_to_a_from_register(self, reg_name: str):
        """
        Add the value of the given register to the accumulator.

        This method adds the value stored in the given register to the
        accumulator (A).

        Args:
            reg_name (str): The name of the register whose value is to be added.

        Raises:
            Exception: If the register name is invalid.
        """
        if hasattr(self, reg_name):
            reg = getattr(self, reg_name)
            self.A += reg
        else:
            raise Exception(f"Invalid register: {reg_name}")

    def _decrement_register(self, reg_name: str):
        """
        Decrement the value of the specified register by one.

        This method decreases the value stored in the specified register by 0x01.
        If the register does not exist, it raises an exception.

        Args:
            reg_name (str): The name of the register to decrement.

        Raises:
            Exception: If the register name is invalid.

        Sets the Z flag to True if the result of the decrement is 0x00.
        """
        if hasattr(self, reg_name):
            reg = getattr(self, reg_name)
            reg -= 0x01
            setattr(self, reg_name, reg)
        else:
            raise Exception(f"Invalid register: {reg_name}")

        if getattr(self, reg_name) == 0x00:
            self.Flags.Z = True

    def _increment_register(self, reg_name: str):
        """
        Increment the value of the specified register by one.

        This method increases the value stored in the specified register by 0x01.
        If the register does not exist, it raises an exception.

        Args:
            reg_name (str): The name of the register to increment.

        Raises:
            Exception: If the register name is invalid.
        """
        if hasattr(self, reg_name):
            reg = getattr(self, reg_name)
            reg += 0x01
            setattr(self, reg_name, reg)
        else:
            raise Exception(f"Invalid register: {reg_name}")

    def _jump_if_not_zero(self):
        """
        Jump to the given address if the Zero flag is not set.

        This function fetches a word from memory and jumps to the given
        address if the Zero flag is not set.

        The Zero flag is set if the result of the last instruction was zero.
        Otherwise, the flag is cleared.

        Parameters:
            jmp_addr (int): The address to jump to if the Zero flag is not set.
        """
        jmp_addr = self.fetch_word()
        if not self.Flags.Z:
            self.PC = jmp_addr

    def _move_inmediate_to_register(self, reg_name: str):
        """
        Move the value of the immediate after the opcode to the given register.

        This function is a helper for the MVI instructions. It fetches the
        immediate value from memory and moves it to the given register.

        Args:
            reg_name (str): The name of the register to move the value to.

        Raises:
            Exception: If the register name is unknown.
        """
        if hasattr(self, reg_name):
            setattr(self, reg_name, self.fetch())
        else:
            raise Exception(f"Unknown register: {reg_name}")

    def _mov_reg_a_to_reg_b(self):
        self.B = self.A

    def _mov_reg_b_to_reg_a(self):
        self.A = self.B

    def _system_halt(self):
        """
        Halt the system by raising a SystemHalt exception.

        This instruction simply raises an exception to signal to the
        emulator that the program has finished executing.

        Raises:
            SystemHalt: The system has halted.
        """
        raise SystemHalt

    def fetch(self) -> int:
        """
        Fetch a byte from memory and return its value.

        The byte is fetched from the current program counter (PC) and the
        PC is incremented by one after the fetch.

        Returns:
            int: The value of the fetched byte.
        """
        value = self.memory.fetch(self.PC)
        self.PC += 0x01
        return value

    def fetch_word(self) -> int:
        """
        Fetch a word (two bytes) from memory and return its value.

        The word is fetched from the current program counter (PC) and the
        PC is incremented by two after the fetch.

        Returns:
            int: The value of the fetched word.
        """
        addr_l = self.fetch()
        addr_h = self.fetch()

        return addr_h << 0x08 | addr_l

    def execute(self):
        """
        Execute instructions in the code segment.

        This method runs an infinite loop that fetches opcodes from memory
        and executes them. If an unknown opcode is encountered, an
        exception is raised.

        The loop can only be exited by raising an exception.

        Raises:
            Exception: If an unknown opcode is encountered.
        """
        while True:
            opcode = self.fetch()
            if opcode in self.instructions:
                self.instructions[opcode](self)
                continue

            raise Exception(f"Unknown opcode: 0x{opcode:02x}")
