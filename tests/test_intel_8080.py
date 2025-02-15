import unittest

from xpire.cpus.intel_8080 import Intel8080, Registers
from xpire.memory import Memory


class TestIntel8080(unittest.TestCase):
    def setUp(self):
        memory = Memory()
        self.cpu = Intel8080(memory=memory)

    def test_fetch_word(self):
        """
        Test fetching a 16-bit word from memory.
        """
        self.cpu.PC = 0x0000
        self.cpu.memory[0x0000] = 0x12
        self.cpu.memory[0x0001] = 0x34
        assert self.cpu.fetch_word() == 0x3412, "Shoud fetch correct word"

    def test_fetch_byte(self):
        """
        Test fetching a byte from memory.
        """
        self.cpu.PC = 0x0000
        self.cpu.memory[0x0000] = 0x12
        assert self.cpu.fetch_byte() == 0x12, "Shoud fetch correct byte"

    def test_flags(self):
        self.assertEqual(self.cpu.flags["Z"], False)
        self.assertEqual(self.cpu.flags["S"], False)
        self.assertEqual(self.cpu.flags["P"], False)
        self.assertEqual(self.cpu.flags["C"], False)
        self.assertEqual(self.cpu.flags["A"], False)

        self.cpu.registers[Registers.B] = 0xFF
        self.cpu.registers[Registers.A] = 0xFF
        self.cpu.add_to_accumulator(Registers.B)

        self.assertEqual(self.cpu.flags["Z"], False)
        self.assertEqual(self.cpu.flags["S"], True)
        self.assertEqual(self.cpu.flags["P"], False)
        self.assertEqual(self.cpu.flags["C"], True)
        self.assertEqual(self.cpu.flags["A"], True)

    def test_icr_flags(self):
        self.cpu.flags["Z"] = False
        self.cpu.flags["S"] = False
        self.cpu.flags["P"] = False
        self.cpu.flags["C"] = False
        self.cpu.flags["A"] = False

        self.cpu.registers[Registers.B] = 0xFE
        self.cpu.increment_register(Registers.B)

        self.assertEqual(self.cpu.registers[Registers.B], 0xFF)
        self.assertEqual(self.cpu.flags["Z"], False)
        self.assertEqual(self.cpu.flags["S"], True)
        self.assertEqual(self.cpu.flags["P"], True)
        self.assertEqual(self.cpu.flags["C"], False)
        self.assertEqual(self.cpu.flags["A"], False)

        self.cpu.registers[Registers.B] = 0xFF
        self.cpu.increment_register(Registers.B)

        self.assertEqual(self.cpu.registers[Registers.B], 0x00)
        self.assertEqual(self.cpu.flags["Z"], True)
        self.assertEqual(self.cpu.flags["S"], False)
        self.assertEqual(self.cpu.flags["P"], True)
        self.assertEqual(self.cpu.flags["C"], False)
        self.assertEqual(self.cpu.flags["A"], True)

    def test_add_to_accumulator(self):
        self.cpu.registers[Registers.A] = 0x2E
        self.cpu.registers[Registers.D] = 0x6C
        self.cpu.add_to_accumulator(Registers.D)

        self.assertEqual(self.cpu.registers[Registers.A], 0x9A)
        self.assertEqual(self.cpu.flags["Z"], False)
        self.assertEqual(self.cpu.flags["S"], True)
        self.assertEqual(self.cpu.flags["P"], True)
        self.assertEqual(self.cpu.flags["C"], False)
        self.assertEqual(self.cpu.flags["A"], True)

    def test_register_and_register(self):
        self.cpu.registers[Registers.A] = 0xFC
        self.cpu.registers[Registers.D] = 0x0F
        self.cpu.register_and_register(Registers.A, Registers.D)

        self.assertEqual(self.cpu.registers[Registers.A], 0x0C)
        self.assertEqual(self.cpu.flags["S"], False)
        self.assertEqual(self.cpu.flags["Z"], False)
        self.assertEqual(self.cpu.flags["P"], True)
        self.assertEqual(self.cpu.flags["C"], False)

    def test_apply_xor_to_registers(self):
        self.cpu.registers[Registers.A] = 0xFC
        self.cpu.registers[Registers.B] = 0x0F
        self.cpu.registers[Registers.C] = 0x0F

        self.cpu.apply_xor_to_registers(Registers.A, Registers.A)
        self.cpu.move_register_to_register(Registers.A, Registers.B)
        self.cpu.move_register_to_register(Registers.A, Registers.C)

        self.assertEqual(self.cpu.registers[Registers.A], 0x00)
        self.assertEqual(self.cpu.registers[Registers.B], 0x00)
        self.assertEqual(self.cpu.registers[Registers.C], 0x00)

        self.assertEqual(self.cpu.flags["S"], False)
        self.assertEqual(self.cpu.flags["Z"], True)
        self.assertEqual(self.cpu.flags["P"], True)
        self.assertEqual(self.cpu.flags["C"], False)
        self.assertEqual(self.cpu.flags["A"], False)

    def test_apply_xor_to_registers_2(self):
        self.cpu.registers[Registers.A] = 0b11111111  # 0xFF
        self.cpu.registers[Registers.B] = 0b10111011  # 0xBB

        self.cpu.apply_xor_to_registers(Registers.A, Registers.B)

        self.assertEqual(self.cpu.registers[Registers.A], 0b01000100)  # 0x44
        self.assertEqual(self.cpu.registers[Registers.B], 0b10111011)  # 0xBB

        self.assertEqual(self.cpu.flags["S"], False)
        self.assertEqual(self.cpu.flags["Z"], False)
        self.assertEqual(self.cpu.flags["P"], True)
        self.assertEqual(self.cpu.flags["C"], False)
        self.assertEqual(self.cpu.flags["A"], False)

    def test_register_or_with_accumulator(self):
        self.cpu.registers[Registers.A] = 0x33
        self.cpu.registers[Registers.C] = 0x0F

        self.cpu.register_or_with_accumulator(Registers.C)

        self.assertEqual(self.cpu.registers[Registers.A], 0x3F)
        self.assertEqual(self.cpu.registers[Registers.C], 0x0F)

        self.assertEqual(self.cpu.flags["S"], False)
        self.assertEqual(self.cpu.flags["Z"], False)
        self.assertEqual(self.cpu.flags["P"], True)
        self.assertEqual(self.cpu.flags["C"], False)
        self.assertEqual(self.cpu.flags["A"], False)

    def test_rotate_right_accumulator(self):
        """
        Test rotate right accumulator.

        Example:
            0b11110010 -> 0b01111001
        """
        self.cpu.registers[Registers.A] = 0b11110010  # 0xF2
        self.cpu.rotate_right_a()

        self.assertEqual(self.cpu.registers[Registers.A], 0b1111001)  # 0x79
        self.assertEqual(self.cpu.flags["S"], False)
        self.assertEqual(self.cpu.flags["Z"], False)
        self.assertEqual(self.cpu.flags["P"], False)
        self.assertEqual(self.cpu.flags["C"], False)
        self.assertEqual(self.cpu.flags["A"], False)

    def test_rotate_right_a_through_carry(self):
        self.cpu.registers[Registers.A] = 0b01101010  # 0x6A
        self.cpu.flags["C"] = True

        self.cpu.rotate_right_a_through_carry()

        self.assertEqual(self.cpu.registers[Registers.A], 0b10110101)  # 0xB5
        self.assertEqual(self.cpu.flags["S"], False)
        self.assertEqual(self.cpu.flags["Z"], False)
        self.assertEqual(self.cpu.flags["P"], False)
        self.assertEqual(self.cpu.flags["C"], False)
        self.assertEqual(self.cpu.flags["A"], False)

    def test_sum_register_pair_with_hl(self):
        self.cpu.registers[Registers.B] = 0x33
        self.cpu.registers[Registers.C] = 0x9F

        self.cpu.registers[Registers.H] = 0xA1
        self.cpu.registers[Registers.L] = 0x7B

        self.cpu.sum_register_pair_with_hl(Registers.B, Registers.C)

        self.assertEqual(self.cpu.registers[Registers.H], 0xD5)
        self.assertEqual(self.cpu.registers[Registers.L], 0x1A)

        self.assertEqual(self.cpu.flags["S"], False)
        self.assertEqual(self.cpu.flags["Z"], False)
        self.assertEqual(self.cpu.flags["P"], False)
        self.assertEqual(self.cpu.flags["C"], False)
        self.assertEqual(self.cpu.flags["A"], False)

    def test_exchange_register_pairs(self):
        self.cpu.registers[Registers.H] = 0x00
        self.cpu.registers[Registers.L] = 0xFF
        self.cpu.registers[Registers.D] = 0x33
        self.cpu.registers[Registers.E] = 0x55

        self.cpu.exchange_register_pairs(
            Registers.H, Registers.L, Registers.D, Registers.E
        )

        self.assertEqual(self.cpu.registers[Registers.H], 0x33)
        self.assertEqual(self.cpu.registers[Registers.L], 0x55)
        self.assertEqual(self.cpu.registers[Registers.D], 0x00)
        self.assertEqual(self.cpu.registers[Registers.E], 0xFF)

    def test_add_immediate_to_accumulator(self):
        self.cpu.registers[Registers.A] = 0x14
        self.cpu.PC = 0x0000
        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.add_immediate_to_accumulator()
        self.assertEqual(self.cpu.registers[Registers.A], 0x56)

        self.cpu.add_immediate_to_accumulator()
        self.assertEqual(self.cpu.registers[Registers.A], 0x14)
        self.assertEqual(self.cpu.flags["S"], False)
        self.assertEqual(self.cpu.flags["Z"], False)
        self.assertEqual(self.cpu.flags["P"], True)
        self.assertEqual(self.cpu.flags["C"], True)
        self.assertEqual(self.cpu.flags["A"], True)

    def test_read_memory_word_bytes(self):
        """
        Test read memory word bytes.

        Reads word on litle endian order.
        """
        self.cpu.PC = 0x0000
        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.assertEqual(self.cpu.read_memory_word_bytes(0x0000), (0xBE, 0x42))

    def test_write_memory_word(self):
        """
        Test write memory word.

        Writes word on litle endian order.
        """
        self.cpu.PC = 0x0000
        self.cpu.write_memory_word(0x0000, 0x42, 0xBE)

        self.assertEqual(self.cpu.memory[0x0000], 0xBE)
        self.assertEqual(self.cpu.memory[0x0001], 0x42)
