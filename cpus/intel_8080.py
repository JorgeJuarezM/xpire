from cpus.cpu import CPU
from decorators import increment_stack_pointer
from memory import Memory
from enum import Enum


NEXT_ADDRESS = 0x00


class Register(int):
    size: int = 0x01  # 1 byte

    def __new__(cls, value: int = 0x00):
        try:
            value_bytes = int.to_bytes(value, 1)
            result = int.from_bytes(value_bytes)
        except OverflowError:
            result = 0x00

        return super().__new__(cls, result)

    def __add__(self, other):
        result = super().__add__(other)
        return self.__class__(result)

    def __next__(self):
        return self.__class__(self + 0x01)


class Intel8080(CPU):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.REG_A = Register(0x00)
        self.REG_B = Register(0x00)
        self.REG_C = Register(0x00)
        self.REG_H = Register(0x00)
        self.REG_L = Register(0x00)

        self.add_instruction(0x03, self.increment_bc_register)
        self.add_instruction(0x04, self.increment_b_register)
        self.add_instruction(0x06, self.move_immediate_to_register_b)
        self.add_instruction(0x31, self.load_immediate_to_stack_pointer)
        self.add_instruction(0x32, self.store_accumulator_to_memory)
        self.add_instruction(0x3A, self.load_memory_address_to_accumulator)
        self.add_instruction(0x3C, self.increment_accumulator)
        self.add_instruction(0x3E, self.move_immediate_to_register_a)
        self.add_instruction(0xC3, self.jump_to_address)
        self.add_instruction(0xC5, self.push_bc_to_stack)
        self.add_instruction(0xC9, self.return_from_call)
        self.add_instruction(0xCD, self.call_address)
        self.add_instruction(0xE1, self.pop_hl_from_stack)

    def load_memory_address_to_accumulator(self):
        address = self.fetch_word()
        self.REG_A = self.read_memory_byte(address)

    def jump_to_address(self):
        address = self.fetch_word()
        self.PC = address

    def increment_accumulator(self):
        self.REG_A += 0x01

    def load_immediate_to_stack_pointer(self):
        self.SP = self.fetch_word()

    def move_immediate_to_register_a(self):
        self.REG_A = self.fetch_byte()

    def move_immediate_to_register_b(self):
        self.REG_B = self.fetch_byte()

    def call_address(self):
        address = self.fetch_word()
        # self.push(self.PC)
        NEXT_ADDRESS = self.PC
        self.PC = address

    def increment_b_register(self):
        self.REG_B += 0x01

    def increment_bc_register(self):
        value = self.REG_B << 0x08 | self.REG_C
        value += 0x01

        if value.bit_length() > 16:
            value = 0x00

        self.REG_B = value >> 0x08
        self.REG_C = value & 0x00FF

    def return_from_call(self):
        # self.PC = self.pop()
        self.PC = NEXT_ADDRESS

    def push(self, high_byte, low_byte):
        self.SP -= 0x02
        self.write_memory_word(self.SP, high_byte, low_byte)

    def push_bc_to_stack(self):
        # print(f"push: {self.REG_B}, {self.REG_C}, {self.SP}, {self.memory.size}")
        self.push(self.REG_B, self.REG_C)

    @increment_stack_pointer()
    def pop(self):
        return self.read_memory_word_bytes(self.SP)

    def pop_hl_from_stack(self):
        self.REG_H, self.REG_L = self.pop()

    def write_memory_byte(self, address, value):
        self.memory[address] = value

    def write_memory_word(self, address, high_byte, low_byte):
        self.write_memory_byte(address, high_byte)
        self.write_memory_byte(address + 0x01, low_byte)

    def store_accumulator_to_memory(self):
        address = self.fetch_word()
        self.write_memory_byte(address, self.REG_A)
