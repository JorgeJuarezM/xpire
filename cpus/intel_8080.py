from cpus.cpu import CPU
from decorators import increment_stack_pointer, increment_program_counter
from memory import Memory
from enum import Enum


class Registers(Enum):
    A = 0x00
    B = 0x01
    C = 0x02
    D = 0x03
    E = 0x04
    H = 0x05
    L = 0x06


NEXT_ADDRESS = 0x00


class Intel8080(CPU):
    def __init__(self, *args, **kwargs):
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

    def load_memory_address_to_accumulator(self):
        address = self.fetch_word()
        self.registers[Registers.A] = self.read_memory_byte(address)

    def jump_to_address(self):
        address = self.fetch_word()
        self.PC = address

    def increment_accumulator(self):
        self.registers[Registers.A] += 0x01

    def load_immediate_to_stack_pointer(self):
        self.SP = self.fetch_word()

    def call_address(self):
        address = self.fetch_word()
        self.push(self.PC >> 0x08, self.PC & 0x00FF)
        self.PC = address

    def increment_b_register(self):
        self.registers[Registers.B] += 0x01

    def increment_bc_register(self):
        value = self.registers[Registers.B] << 0x08 | self.registers[Registers.C]
        value += 0x01

        if value.bit_length() > 0x10:
            value = 0x00

        self.registers[Registers.B] = value >> 0x08
        self.registers[Registers.C] = value & 0x00FF

    def return_from_call(self):
        h, l = self.pop()
        self.PC = h << 0x08 | l

    def push(self, high_byte, low_byte):
        self.SP -= 0x02
        self.write_memory_word(self.SP, high_byte, low_byte)

    def push_bc_to_stack(self):
        self.push(
            self.registers[Registers.B],
            self.registers[Registers.C],
        )

    @increment_stack_pointer()
    def pop(self):
        return self.read_memory_word_bytes(self.SP)

    def pop_hl_from_stack(self):
        self.registers[Registers.H], self.registers[Registers.L] = self.pop()

    def write_memory_byte(self, address, value):
        self.memory[address] = value

    def write_memory_word(self, address, high_byte, low_byte):
        self.write_memory_byte(address, high_byte)
        self.write_memory_byte(address + 0x01, low_byte)

    def store_accumulator_to_memory(self):
        address = self.fetch_word()
        self.write_memory_byte(address, self.registers[Registers.A])

    def move_immediate_to_register(self, register: int):
        def move_immediate_to_register_func():
            self.registers[register] = self.fetch_byte()

        return move_immediate_to_register_func
