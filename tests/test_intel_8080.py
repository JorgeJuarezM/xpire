import tempfile
import unittest
from unittest.mock import patch

import pygame
from faker import Faker

from xpire.cpus.intel_8080 import Intel8080, Registers
from xpire.machine import Machine

fake = Faker()


class MockScreen:
    def __init__(self, *args, **kwargs):
        pass

    def render(self, cpu):
        pass


class MockPygameEventType:
    def __init__(self, event):
        self.event = event

    @property
    def type(self):
        return self.event


class MockPygameEvent:
    def __init__(self, events=None):
        if not events:
            events = []
        self.events = [MockPygameEventType(event) for event in events]

    def get(self):
        return self.events


class TestIntel8080(unittest.TestCase):

    @patch("xpire.machine.Screen", MockScreen)
    def setUp(self):
        self.cpu = Intel8080()
        self.machine = Machine()

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
        self.assertEqual(self.cpu.flags.Z, False)
        self.assertEqual(self.cpu.flags.S, False)
        self.assertEqual(self.cpu.flags.P, False)
        self.assertEqual(self.cpu.flags.C, False)
        self.assertEqual(self.cpu.flags.A, False)

        self.cpu.registers[Registers.B] = 0xFF
        self.cpu.registers[Registers.A] = 0xFF
        self.cpu.add_reg(Registers.B)

        self.assertEqual(self.cpu.flags.Z, False)
        self.assertEqual(self.cpu.flags.S, True)
        self.assertEqual(self.cpu.flags.P, False)
        self.assertEqual(self.cpu.flags.C, True)
        self.assertEqual(self.cpu.flags.A, True)

    def test_icr_flags(self):
        self.cpu.flags.Z = False
        self.cpu.flags.S = False
        self.cpu.flags.P = False
        self.cpu.flags.C = False
        self.cpu.flags.A = False

        self.cpu.registers[Registers.B] = 0xFE
        self.cpu.increment_register(Registers.B)

        self.assertEqual(self.cpu.registers[Registers.B], 0xFF)
        self.assertEqual(self.cpu.flags.Z, False)
        self.assertEqual(self.cpu.flags.S, True)
        self.assertEqual(self.cpu.flags.P, True)
        self.assertEqual(self.cpu.flags.C, False)
        self.assertEqual(self.cpu.flags.A, False)

        self.cpu.registers[Registers.B] = 0xFF
        self.cpu.increment_register(Registers.B)

        self.assertEqual(self.cpu.registers[Registers.B], 0x00)
        self.assertEqual(self.cpu.flags.Z, True)
        self.assertEqual(self.cpu.flags.S, False)
        self.assertEqual(self.cpu.flags.P, True)
        self.assertEqual(self.cpu.flags.C, False)
        self.assertEqual(self.cpu.flags.A, True)

    def test_add_to_accumulator(self):
        self.cpu.registers[Registers.A] = 0x2E
        self.cpu.registers[Registers.D] = 0x6C
        self.cpu.add_reg(Registers.D)

        self.assertEqual(self.cpu.registers[Registers.A], 0x9A)
        self.assertEqual(self.cpu.flags.Z, False)
        self.assertEqual(self.cpu.flags.S, True)
        self.assertEqual(self.cpu.flags.P, True)
        self.assertEqual(self.cpu.flags.C, False)
        self.assertEqual(self.cpu.flags.A, True)

    def test_register_and_register(self):
        self.cpu.registers[Registers.A] = 0xFC
        self.cpu.registers[Registers.D] = 0x0F
        self.cpu.register_and_register(Registers.A, Registers.D)

        self.assertEqual(self.cpu.registers[Registers.A], 0x0C)
        self.assertEqual(self.cpu.flags.S, False)
        self.assertEqual(self.cpu.flags.Z, False)
        self.assertEqual(self.cpu.flags.P, True)
        self.assertEqual(self.cpu.flags.C, False)

    def test_apply_xor_to_registers(self):
        self.cpu.registers[Registers.A] = 0xFC
        self.cpu.registers[Registers.B] = 0x0F
        self.cpu.registers[Registers.C] = 0x0F

        self.cpu.apply_xor_to_registers(Registers.A, Registers.A)
        self.cpu.mov_reg_reg(Registers.A, Registers.B)
        self.cpu.mov_reg_reg(Registers.A, Registers.C)

        self.assertEqual(self.cpu.registers[Registers.A], 0x00)
        self.assertEqual(self.cpu.registers[Registers.B], 0x00)
        self.assertEqual(self.cpu.registers[Registers.C], 0x00)

        self.assertEqual(self.cpu.flags.S, False)
        self.assertEqual(self.cpu.flags.Z, True)
        self.assertEqual(self.cpu.flags.P, True)
        self.assertEqual(self.cpu.flags.C, False)
        self.assertEqual(self.cpu.flags.A, False)

    def test_apply_xor_to_registers_2(self):
        self.cpu.registers[Registers.A] = 0b11111111  # 0xFF
        self.cpu.registers[Registers.B] = 0b10111011  # 0xBB

        self.cpu.apply_xor_to_registers(Registers.A, Registers.B)

        self.assertEqual(self.cpu.registers[Registers.A], 0b01000100)  # 0x44
        self.assertEqual(self.cpu.registers[Registers.B], 0b10111011)  # 0xBB

        self.assertEqual(self.cpu.flags.S, False)
        self.assertEqual(self.cpu.flags.Z, False)
        self.assertEqual(self.cpu.flags.P, True)
        self.assertEqual(self.cpu.flags.C, False)
        self.assertEqual(self.cpu.flags.A, False)

    def test_register_or_with_accumulator(self):
        self.cpu.registers[Registers.A] = 0x33
        self.cpu.registers[Registers.C] = 0x0F

        self.cpu.register_or_with_accumulator(Registers.C)

        self.assertEqual(self.cpu.registers[Registers.A], 0x3F)
        self.assertEqual(self.cpu.registers[Registers.C], 0x0F)

        self.assertEqual(self.cpu.flags.S, False)
        self.assertEqual(self.cpu.flags.Z, False)
        self.assertEqual(self.cpu.flags.P, True)
        self.assertEqual(self.cpu.flags.C, False)
        self.assertEqual(self.cpu.flags.A, False)

    def test_rotate_right_accumulator(self):
        """
        Test rotate right accumulator.

        Example:
            0b11110010 -> 0b01111001
        """
        self.cpu.registers[Registers.A] = 0b11110010  # 0xF2
        self.cpu.rotate_right_a()

        self.assertEqual(self.cpu.registers[Registers.A], 0b1111001)  # 0x79
        self.assertEqual(self.cpu.flags.S, False)
        self.assertEqual(self.cpu.flags.Z, False)
        self.assertEqual(self.cpu.flags.P, False)
        self.assertEqual(self.cpu.flags.C, False)
        self.assertEqual(self.cpu.flags.A, False)

    def test_rotate_right_a_through_carry(self):
        self.cpu.registers[Registers.A] = 0b01101010  # 0x6A
        self.cpu.flags.C = True

        self.cpu.rotate_right_a_through_carry()

        self.assertEqual(self.cpu.registers[Registers.A], 0b10110101)  # 0xB5
        self.assertEqual(self.cpu.flags.S, False)
        self.assertEqual(self.cpu.flags.Z, False)
        self.assertEqual(self.cpu.flags.P, False)
        self.assertEqual(self.cpu.flags.C, False)
        self.assertEqual(self.cpu.flags.A, False)

    def test_sum_register_pair_with_hl(self):
        self.cpu.registers[Registers.B] = 0x33
        self.cpu.registers[Registers.C] = 0x9F

        self.cpu.registers[Registers.H] = 0xA1
        self.cpu.registers[Registers.L] = 0x7B

        self.cpu.sum_register_pair_with_hl(Registers.B, Registers.C)

        self.assertEqual(self.cpu.registers[Registers.H], 0xD5)
        self.assertEqual(self.cpu.registers[Registers.L], 0x1A)

        self.assertEqual(self.cpu.flags.S, False)
        self.assertEqual(self.cpu.flags.Z, False)
        self.assertEqual(self.cpu.flags.P, False)
        self.assertEqual(self.cpu.flags.C, False)
        self.assertEqual(self.cpu.flags.A, False)

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
        self.assertEqual(self.cpu.flags.S, False)
        self.assertEqual(self.cpu.flags.Z, False)
        self.assertEqual(self.cpu.flags.P, True)
        self.assertEqual(self.cpu.flags.C, True)
        self.assertEqual(self.cpu.flags.A, True)

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

    def test_push_to_stack(self):
        """
        Test push to stack.

        Pushes word on litle endian order.
        """
        self.cpu.registers[Registers.H] = 0x00
        self.cpu.registers[Registers.L] = 0xFF

        self.cpu.push_to_stack(Registers.H, Registers.L)

        self.assertEqual(self.cpu.memory[self.cpu.SP], 0xFF)
        self.assertEqual(self.cpu.memory[self.cpu.SP - 1], 0x00)
        self.assertEqual(self.cpu.SP, 0xFFFE)

    def test_add_register_to_accumulator(self):
        self.cpu.registers[Registers.A] = 0x33
        self.cpu.registers[Registers.C] = 0x0F

        self.cpu.add_reg(Registers.C)

        self.assertEqual(self.cpu.registers[Registers.A], 0x42)
        self.assertEqual(self.cpu.registers[Registers.C], 0x0F)

        self.assertEqual(self.cpu.flags.S, False)
        self.assertEqual(self.cpu.flags.Z, False)
        self.assertEqual(self.cpu.flags.P, True)
        self.assertEqual(self.cpu.flags.C, False)
        self.assertEqual(self.cpu.flags.A, True)

    def test_exchange_sp_with_hl(self):

        self.cpu.SP = 0xAABB

        self.cpu.registers[Registers.H] = 0x00
        self.cpu.registers[Registers.L] = 0xCC

        self.cpu.memory[self.cpu.SP] = 0xDD
        self.cpu.memory[self.cpu.SP + 1] = 0xDE

        self.cpu.exchange_sp_hl()

        self.assertEqual(self.cpu.registers[Registers.H], 0xDE)  # SP +1
        self.assertEqual(self.cpu.registers[Registers.L], 0xDD)  # SP
        self.assertEqual(self.cpu.memory[self.cpu.SP], 0xCC)  # L
        self.assertEqual(self.cpu.memory[self.cpu.SP + 1], 0x00)  # H

    def test_increment_memory_address_on_hl(self):
        self.cpu.registers[Registers.H] = 0x00
        self.cpu.registers[Registers.L] = 0x00
        self.cpu.memory[0x0000] = 0x19

        self.cpu.increment_memory_address()

        self.assertEqual(self.cpu.memory[0x0000], 0x1A)
        self.assertEqual(self.cpu.flags.S, False)
        self.assertEqual(self.cpu.flags.Z, False)
        self.assertEqual(self.cpu.flags.P, False)
        self.assertEqual(self.cpu.flags.C, False)
        self.assertEqual(self.cpu.flags.A, False)

    def test_accumulator_and_immediate(self):
        self.cpu.registers[Registers.A] = 0x14
        self.cpu.PC = 0x0000
        self.cpu.memory[0x0000] = 0x42

        self.cpu.accumulator_and_immediate()

        self.assertEqual(self.cpu.registers[Registers.A], 0x00)
        self.assertEqual(self.cpu.flags.S, False)
        self.assertEqual(self.cpu.flags.Z, True)
        self.assertEqual(self.cpu.flags.P, True)
        self.assertEqual(self.cpu.flags.C, False)
        self.assertEqual(self.cpu.flags.A, False)

    def test_jump_if_minus(self):
        self.cpu.PC = 0x0000

        self.cpu.flags.S = True
        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.jump_if_minus()

        self.assertEqual(self.cpu.PC, 0xBE42)

    def test_jump_if_minus_opposite(self):
        self.cpu.PC = 0x0000

        self.cpu.flags.S = False
        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.jump_if_minus()

        self.assertEqual(self.cpu.PC, 0x0002)  # PC + 2 (fetch word)

    def test_substract_immediate_from_accumulator(self):
        self.cpu.registers[Registers.A] = 0x14
        self.cpu.PC = 0x0000
        self.cpu.memory[0x0000] = 0x42

        self.cpu.substract_immediate_from_accumulator()

        self.assertEqual(self.cpu.registers[Registers.A], 0xD2)
        self.assertEqual(self.cpu.flags.S, True)
        self.assertEqual(self.cpu.flags.Z, False)
        self.assertEqual(self.cpu.flags.P, True)
        self.assertEqual(self.cpu.flags.C, True)
        self.assertEqual(self.cpu.flags.A, True)

    def test_compare_register_with_accumulator(self):
        self.machine.cpu.memory[0x0000] = 0x0E  # MVI C, 14h
        self.machine.cpu.memory[0x0001] = 0x14
        self.machine.cpu.memory[0x0002] = 0x3E  # MVI A, 14h
        self.machine.cpu.memory[0x0003] = 0x14
        self.machine.cpu.memory[0x0004] = 0xB9  # CMP C
        self.machine.cpu.memory[0x0005] = 0x76  # HLT

        self.machine.cpu.PC = 0x0000

        self.machine.run()

        self.assertEqual(self.machine.cpu.registers[Registers.C], 0x14)
        self.assertEqual(self.machine.cpu.registers[Registers.A], 0x14)

        self.assertEqual(self.machine.cpu.flags.S, False)
        self.assertEqual(self.machine.cpu.flags.Z, True)
        self.assertEqual(self.machine.cpu.flags.P, True)
        self.assertEqual(self.machine.cpu.flags.C, False)
        self.assertEqual(self.machine.cpu.flags.A, True)

    def test_compare_register_with_accumulator_opposite(self):
        self.cpu.registers[Registers.A] = 0x14
        self.cpu.registers[Registers.C] = 0x22

        self.cpu.compare_register_with_accumulator(Registers.C)

        self.assertEqual(self.cpu.flags.S, True)
        self.assertEqual(self.cpu.flags.Z, False)
        self.assertEqual(self.cpu.flags.P, False)
        self.assertEqual(self.cpu.flags.C, True)
        self.assertEqual(self.cpu.flags.A, True)

    def test_call_if_not_carry(self):
        self.cpu.flags.C = False
        self.cpu.PC = 0x0000
        self.cpu.SP = 0x0000

        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.call_if_not_carry()

        self.assertEqual(self.cpu.PC, 0xBE42)
        self.assertEqual(self.cpu.SP, 0xFFFE)

    def test_call_if_not_carry_opposite(self):
        self.cpu.flags.C = True
        self.cpu.PC = 0x0000
        self.cpu.SP = 0x0000

        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.call_if_not_carry()

        self.assertEqual(self.cpu.PC, 0x0002)
        self.assertEqual(self.cpu.SP, 0x0000)

    def test_compare_register_with_memory(self):
        self.machine.cpu.memory[0x0000] = 0x26  # MVI H, FFh
        self.machine.cpu.memory[0x0001] = 0xFF
        self.machine.cpu.memory[0x0002] = 0x2E  # MVI L, FFh
        self.machine.cpu.memory[0x0003] = 0xFF
        self.machine.cpu.memory[0x0004] = 0x3E  # MVI A, 14h
        self.machine.cpu.memory[0x0005] = 0x14
        self.machine.cpu.memory[0x0006] = 0x32  # STA FFFFh
        self.machine.cpu.memory[0x0007] = 0xFF
        self.machine.cpu.memory[0x0008] = 0xFF
        self.machine.cpu.memory[0x0009] = 0xBE  # CMP M
        self.machine.cpu.memory[0x000A] = 0x76  # HLT

        self.machine.PC = 0x0000
        self.machine.run()

        self.assertEqual(self.machine.cpu.registers[Registers.A], 0x14)
        self.assertEqual(self.machine.cpu.registers[Registers.H], 0xFF)
        self.assertEqual(self.machine.cpu.registers[Registers.L], 0xFF)

        self.assertEqual(self.machine.cpu.flags.S, False)
        self.assertEqual(self.machine.cpu.flags.Z, True)
        self.assertEqual(self.machine.cpu.flags.P, True)
        self.assertEqual(self.machine.cpu.flags.C, False)
        self.assertEqual(self.machine.cpu.flags.A, True)

    def test_compare_register_with_memory_opposite(self):
        self.cpu.registers[Registers.A] = 0x14
        self.cpu.PC = 0x0000
        self.cpu.memory[0x0000] = 0x42

        self.cpu.compare_register_with_memory()

        self.assertEqual(self.cpu.flags.S, True)
        self.assertEqual(self.cpu.flags.Z, False)
        self.assertEqual(self.cpu.flags.P, True)
        self.assertEqual(self.cpu.flags.C, True)
        self.assertEqual(self.cpu.flags.A, True)

    def test_substract_register_from_accumulator(self):
        self.cpu.registers[Registers.A] = 0x14
        self.cpu.registers[Registers.C] = 0x14

        self.cpu.substract_register_from_accumulator(Registers.C)

        self.assertEqual(self.cpu.registers[Registers.A], 0x00)
        self.assertEqual(self.cpu.flags.S, False)
        self.assertEqual(self.cpu.flags.Z, True)
        self.assertEqual(self.cpu.flags.P, True)
        self.assertEqual(self.cpu.flags.C, False)
        self.assertEqual(self.cpu.flags.A, True)

    @patch("xpire.machine.Screen", MockScreen)
    @patch("xpire.machine.pygame.event", MockPygameEvent())
    def test_machine_run(self):
        rom_file = tempfile.NamedTemporaryFile(suffix=".com")
        machine = Machine()
        machine.load_rom(rom_file.name)
        machine.cpu.memory[0x0000] = 0x76  # HLT
        machine.cpu.cycles = 40000
        machine.cpu.interrupts_enabled = True
        machine.run()

        self.assertTrue(machine.cpu.halted)

    @patch("xpire.machine.Screen", MockScreen)
    @patch("xpire.machine.pygame.event", MockPygameEvent())
    def test_machine_invalid_rom(self):
        rom_file = fake.file_name()
        machine = Machine()
        result = machine.load_rom(rom_file)
        self.assertFalse(result)

    @patch("xpire.machine.Screen", MockScreen)
    @patch("xpire.machine.pygame.event", MockPygameEvent([pygame.QUIT]))
    def test_machine_process_input(self):
        machine = Machine()
        machine.process_input()
        self.assertFalse(machine.running)

    def test_decrement_register(self):
        self.cpu.registers[Registers.A] = 0x14
        self.cpu.decrement_register(Registers.A)

        self.assertEqual(self.cpu.registers[Registers.A], 0x13)
        self.assertEqual(self.cpu.flags.S, False)
        self.assertEqual(self.cpu.flags.Z, False)
        self.assertEqual(self.cpu.flags.P, False)
        self.assertEqual(self.cpu.flags.C, False)
        self.assertEqual(self.cpu.flags.A, False)

    def test_jump_if_not_zero(self):
        self.cpu.PC = 0x0000

        self.cpu.flags.Z = False
        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.jump_if_not_zero()

        self.assertEqual(self.cpu.PC, 0xBE42)

        self.cpu.PC = 0x0000
        self.cpu.flags.clear_flags()
        self.cpu.flags.Z = True

        self.cpu.jump_if_not_zero()

        self.assertEqual(self.cpu.PC, 0x0002)

    def test_compare_register_with_immediate(self):
        self.machine.cpu.memory[0x0000] = 0x3E  # MVI A, 14h
        self.machine.cpu.memory[0x0001] = 0x14
        self.machine.cpu.memory[0x0002] = 0xFE  # CPI 14h
        self.machine.cpu.memory[0x0003] = 0x14
        self.machine.cpu.memory[0x0004] = 0x76  # HLT

        self.machine.PC = 0x0000
        self.machine.run()

        self.assertEqual(self.machine.cpu.flags.S, False)
        self.assertEqual(self.machine.cpu.flags.Z, True)
        self.assertEqual(self.machine.cpu.flags.P, True)
        self.assertEqual(self.machine.cpu.flags.C, False)
        self.assertEqual(self.machine.cpu.flags.A, True)

    def test_return_if_not_carry(self):
        self.cpu.flags.C = False
        self.cpu.PC = 0x0000
        self.cpu.SP = 0x0000

        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.return_if_not_carry()

        self.assertEqual(self.cpu.PC, 0xBE42)
        self.assertEqual(self.cpu.SP, 0x0002)

    def test_return_if_not_carry_opposite(self):
        self.cpu.flags.C = True
        self.cpu.PC = 0x0000
        self.cpu.SP = 0x0000

        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.return_if_not_carry()

        self.assertEqual(self.cpu.PC, 0x0000)
        self.assertEqual(self.cpu.SP, 0x0000)

    def test_return_if_carry(self):
        self.cpu.flags.C = True
        self.cpu.PC = 0x0000
        self.cpu.SP = 0x0000

        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.return_if_carry()

        self.assertEqual(self.cpu.PC, 0xBE42)
        self.assertEqual(self.cpu.SP, 0x0002)

    def test_return_if_carry_opposite(self):
        self.cpu.flags.C = False
        self.cpu.PC = 0x0000
        self.cpu.SP = 0x0000

        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.return_if_carry()

        self.assertEqual(self.cpu.PC, 0x0000)
        self.assertEqual(self.cpu.SP, 0x0000)

    def test_register_or_with_memory(self):
        self.cpu.registers[Registers.A] = 0x14
        self.cpu.PC = 0x0000

        self.cpu.memory[0x0000] = 0x14
        self.cpu.registers[Registers.H] = 0x00
        self.cpu.registers[Registers.L] = 0x00

        self.cpu.register_or_with_memory(Registers.A)

        self.assertEqual(self.cpu.registers[Registers.A], 0x14)
        self.assertEqual(self.cpu.flags.S, False)
        self.assertEqual(self.cpu.flags.Z, False)
        self.assertEqual(self.cpu.flags.P, True)
        self.assertEqual(self.cpu.flags.C, False)
        self.assertEqual(self.cpu.flags.A, False)

    def test_jump_if_zero(self):
        self.cpu.PC = 0x0000

        self.cpu.flags.Z = True
        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.jump_if_zero()

        self.assertEqual(self.cpu.PC, 0xBE42)

        self.cpu.PC = 0x0000
        self.cpu.flags.clear_flags()
        self.cpu.flags.Z = False

        self.cpu.jump_if_zero()

        self.assertEqual(self.cpu.PC, 0x0002)

    def test_jump_if_parity(self):
        self.cpu.PC = 0x0000

        self.cpu.flags.P = True
        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.jump_if_parity()

        self.assertEqual(self.cpu.PC, 0xBE42)

        self.cpu.PC = 0x0000
        self.cpu.flags.clear_flags()
        self.cpu.flags.P = False

        self.cpu.jump_if_parity()

        self.assertEqual(self.cpu.PC, 0x0002)

    def test_rotate_left_accumulator(self):
        self.cpu.registers[Registers.A] = 0x14
        self.cpu.rotate_left_accumulator()

        self.assertEqual(self.cpu.registers[Registers.A], 0x28)
        self.assertEqual(self.cpu.flags.S, False)
        self.assertEqual(self.cpu.flags.Z, False)
        self.assertEqual(self.cpu.flags.P, False)
        self.assertEqual(self.cpu.flags.C, False)
        self.assertEqual(self.cpu.flags.A, False)

    def test_jump_if_not_carry(self):
        self.cpu.PC = 0x0000

        self.cpu.flags.C = False
        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.jump_if_not_carry()

        self.assertEqual(self.cpu.PC, 0xBE42)

        self.cpu.PC = 0x0000
        self.cpu.flags.clear_flags()
        self.cpu.flags.C = True

        self.cpu.jump_if_not_carry()

        self.assertEqual(self.cpu.PC, 0x0002)

    def test_jump_if_carry(self):
        self.cpu.PC = 0x0000

        self.cpu.flags.C = True
        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.jump_if_carry()

        self.assertEqual(self.cpu.PC, 0xBE42)

        self.cpu.PC = 0x0000
        self.cpu.flags.clear_flags()
        self.cpu.flags.C = False

        self.cpu.jump_if_carry()

        self.assertEqual(self.cpu.PC, 0x0002)

    def test_push_and_pop_processor_state_word(self):
        self.cpu.PC = 0x0000
        self.cpu.SP = 0x0000
        self.cpu.registers[Registers.A] = 0x14
        self.cpu.flags.set_flags(0xFF)

        self.cpu.push_processor_state_word()
        self.cpu.registers[Registers.A] = 0x20
        self.cpu.flags.clear_flags()

        self.cpu.pop_processor_state_word()

        self.assertEqual(self.cpu.PC, 0x0000)
        self.assertEqual(self.cpu.SP, 0x0000)
        self.assertEqual(self.cpu.registers[Registers.A], 0x14)
        self.assertEqual(self.cpu.flags.get_flags(), 0xFF)

    def test_set_carry_flag(self):
        self.cpu.set_carry()
        self.assertEqual(self.cpu.flags.C, True)
        self.assertEqual(self.cpu.flags.S, False)
        self.assertEqual(self.cpu.flags.Z, False)
        self.assertEqual(self.cpu.flags.P, False)
        self.assertEqual(self.cpu.flags.A, False)

    def test_return_if_zero(self):
        self.cpu.flags.Z = True
        self.cpu.PC = 0x0000
        self.cpu.SP = 0x0000

        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.return_if_zero()

        self.assertEqual(self.cpu.PC, 0xBE42)
        self.assertEqual(self.cpu.SP, 0x0002)

    def test_return_if_zero_opposite(self):
        self.cpu.flags.Z = False
        self.cpu.PC = 0x0000
        self.cpu.SP = 0x0000

        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.return_if_zero()

        self.assertEqual(self.cpu.PC, 0x0000)
        self.assertEqual(self.cpu.SP, 0x0000)

    def test_return_if_not_zero(self):
        self.cpu.flags.Z = False
        self.cpu.PC = 0x0000
        self.cpu.SP = 0x0000

        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.return_if_not_zero()

        self.assertEqual(self.cpu.PC, 0xBE42)
        self.assertEqual(self.cpu.SP, 0x0002)

    def test_return_if_not_zero_opposite(self):
        self.cpu.flags.Z = True
        self.cpu.PC = 0x0000
        self.cpu.SP = 0x0000

        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.return_if_not_zero()

        self.assertEqual(self.cpu.PC, 0x0000)
        self.assertEqual(self.cpu.SP, 0x0000)

    def test_decrement_memory_byte(self):
        self.cpu.memory[0x0000] = 0x14
        self.cpu.decrement_memory_byte()

        self.assertEqual(self.cpu.memory[0x0000], 0x13)
        self.assertEqual(self.cpu.flags.S, False)
        self.assertEqual(self.cpu.flags.Z, False)
        self.assertEqual(self.cpu.flags.P, False)
        self.assertEqual(self.cpu.flags.C, False)
        self.assertEqual(self.cpu.flags.A, False)

    def test_call_if_zero(self):
        self.cpu.flags.Z = True
        self.cpu.PC = 0x0000
        self.cpu.SP = 0x0000

        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.call_if_zero()

        self.assertEqual(self.cpu.PC, 0xBE42)
        self.assertEqual(self.cpu.SP, 0xFFFE)

    def test_call_if_zero_opposite(self):
        self.cpu.flags.Z = False
        self.cpu.PC = 0x0000
        self.cpu.SP = 0x0000

        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.call_if_zero()

        self.assertEqual(self.cpu.PC, 0x0002)
        self.assertEqual(self.cpu.SP, 0x0000)

    def test_call_if_not_zero(self):
        self.cpu.flags.Z = False
        self.cpu.PC = 0x0000
        self.cpu.SP = 0x0000

        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.call_if_not_zero()

        self.assertEqual(self.cpu.PC, 0xBE42)
        self.assertEqual(self.cpu.SP, 0xFFFE)

    def test_call_if_not_zero_opposite(self):
        self.cpu.flags.Z = True
        self.cpu.PC = 0x0000
        self.cpu.SP = 0x0000

        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.call_if_not_zero()

        self.assertEqual(self.cpu.PC, 0x0002)
        self.assertEqual(self.cpu.SP, 0x0000)

    def test_substract_immdiate_from_accumulator_with_borrow(self):
        self.cpu.registers[Registers.A] = 0x14
        self.cpu.memory[0x0000] = 0x21
        self.cpu.substract_immediate_from_accumulator_with_borrow()

        self.assertEqual(self.cpu.registers[Registers.A], 0xF3)
        self.assertEqual(self.cpu.flags.S, True)
        self.assertEqual(self.cpu.flags.Z, False)
        self.assertEqual(self.cpu.flags.P, True)
        self.assertEqual(self.cpu.flags.C, True)
        self.assertEqual(self.cpu.flags.A, True)

    def test_return_if_minus(self):
        self.cpu.flags.S = True
        self.cpu.PC = 0x0000
        self.cpu.SP = 0x0000

        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.return_if_minus()

        self.assertEqual(self.cpu.PC, 0xBE42)
        self.assertEqual(self.cpu.SP, 0x0002)

    def test_return_if_minus_opposite(self):
        self.cpu.flags.S = False
        self.cpu.PC = 0x0000
        self.cpu.SP = 0x0000

        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.return_if_minus()

        self.assertEqual(self.cpu.PC, 0x0000)
        self.assertEqual(self.cpu.SP, 0x0000)

    def test_return_if_parity_event(self):
        self.cpu.flags.P = True
        self.cpu.PC = 0x0000
        self.cpu.SP = 0x0000

        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.return_if_parity_even()

        self.assertEqual(self.cpu.PC, 0xBE42)
        self.assertEqual(self.cpu.SP, 0x0002)

    def test_return_if_parity_opposite(self):
        self.cpu.flags.P = False
        self.cpu.PC = 0x0000
        self.cpu.SP = 0x0000

        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.return_if_parity_even()

        self.assertEqual(self.cpu.PC, 0x0000)
        self.assertEqual(self.cpu.SP, 0x0000)

    def test_call_if_parity_even(self):
        self.cpu.flags.P = True
        self.cpu.PC = 0x0000
        self.cpu.SP = 0x0000

        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.call_if_parity_even()

        self.assertEqual(self.cpu.PC, 0xBE42)
        self.assertEqual(self.cpu.SP, 0xFFFE)

    def test_call_if_parity_even_opposite(self):
        self.cpu.flags.P = False
        self.cpu.PC = 0x0000
        self.cpu.SP = 0x0000

        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.call_if_parity_even()

        self.assertEqual(self.cpu.PC, 0x02)
        self.assertEqual(self.cpu.SP, 0x0000)

    def test_and_memory_to_accumulator(self):
        self.cpu.registers[Registers.A] = 0xCC
        self.cpu.memory[0x0000] = 0x0F
        self.cpu.and_memory_to_accumulator()

        self.assertEqual(self.cpu.registers[Registers.A], 0x0C)
        self.assertEqual(self.cpu.flags.S, False)
        self.assertEqual(self.cpu.flags.Z, False)
        self.assertEqual(self.cpu.flags.P, True)
        self.assertEqual(self.cpu.flags.C, False)
        self.assertEqual(self.cpu.flags.A, True)

    def test_dcx_reg16(self):
        self.cpu.registers[Registers.H] = 0x12
        self.cpu.registers[Registers.L] = 0x34
        self.cpu.dcx_reg16(Registers.H, Registers.L)

        self.assertEqual(self.cpu.registers[Registers.H], 0x12)
        self.assertEqual(self.cpu.registers[Registers.L], 0x33)
