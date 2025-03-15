import tempfile
import unittest
import unittest.mock
from unittest.mock import patch

import pygame
from faker import Faker

from xpire.cpus.intel_8080 import Intel8080
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

        self.cpu.registers.B = 0xFF
        self.cpu.registers.A = 0xFF
        self.cpu.add_reg("B")

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

        self.cpu.registers.B = 0xFE
        self.cpu.inr_reg("B")

        self.assertEqual(self.cpu.registers.B, 0xFF)
        self.assertEqual(self.cpu.flags.Z, False)
        self.assertEqual(self.cpu.flags.S, True)
        self.assertEqual(self.cpu.flags.P, True)
        self.assertEqual(self.cpu.flags.C, False)
        self.assertEqual(self.cpu.flags.A, False)

        self.cpu.registers.B = 0xFF
        self.cpu.inr_reg("B")

        self.assertEqual(self.cpu.registers.B, 0x00)
        self.assertEqual(self.cpu.flags.Z, True)
        self.assertEqual(self.cpu.flags.S, False)
        self.assertEqual(self.cpu.flags.P, True)
        self.assertEqual(self.cpu.flags.C, False)
        self.assertEqual(self.cpu.flags.A, True)

    def test_add_to_accumulator(self):
        self.cpu.registers.A = 0x2E
        self.cpu.registers.D = 0x6C
        self.cpu.add_reg("D")

        self.assertEqual(self.cpu.registers.A, 0x9A)
        self.assertEqual(self.cpu.flags.Z, False)
        self.assertEqual(self.cpu.flags.S, True)
        self.assertEqual(self.cpu.flags.P, True)
        self.assertEqual(self.cpu.flags.C, False)
        self.assertEqual(self.cpu.flags.A, True)

    def test_register_and_register(self):
        self.cpu.registers.A = 0xFC
        self.cpu.registers.D = 0x0F
        self.cpu.ana_reg("D")

        self.assertEqual(self.cpu.registers.A, 0x0C)
        self.assertEqual(self.cpu.flags.S, False)
        self.assertEqual(self.cpu.flags.Z, False)
        self.assertEqual(self.cpu.flags.P, True)
        self.assertEqual(self.cpu.flags.C, False)

    def test_apply_xor_to_registers(self):
        self.cpu.registers.A = 0xFC
        self.cpu.xra("A")

        self.assertEqual(self.cpu.registers.A, 0x00)

        self.assertEqual(self.cpu.flags.S, False)
        self.assertEqual(self.cpu.flags.Z, True)
        self.assertEqual(self.cpu.flags.P, True)
        self.assertEqual(self.cpu.flags.C, False)
        self.assertEqual(self.cpu.flags.A, False)

    def test_apply_xor_to_registers_2(self):
        self.cpu.registers.A = 0b11111111  # 0xFF
        self.cpu.registers.B = 0b10111011  # 0xBB

        self.cpu.xra("B")

        self.assertEqual(self.cpu.registers.A, 0b01000100)  # 0x44
        self.assertEqual(self.cpu.registers.B, 0b10111011)  # 0xBB

        self.assertEqual(self.cpu.flags.S, False)
        self.assertEqual(self.cpu.flags.Z, False)
        self.assertEqual(self.cpu.flags.P, True)
        self.assertEqual(self.cpu.flags.C, False)
        self.assertEqual(self.cpu.flags.A, False)

    def test_register_or_with_accumulator(self):
        self.cpu.registers.A = 0x33
        self.cpu.registers.C = 0x0F

        self.cpu.ora_reg("C")

        self.assertEqual(self.cpu.registers.A, 0x3F)
        self.assertEqual(self.cpu.registers.C, 0x0F)

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
        self.cpu.registers.A = 0b11110010  # 0xF2
        self.cpu.rrc()

        self.assertEqual(self.cpu.registers.A, 0b1111001)  # 0x79
        self.assertEqual(self.cpu.flags.S, False)
        self.assertEqual(self.cpu.flags.Z, False)
        self.assertEqual(self.cpu.flags.P, False)
        self.assertEqual(self.cpu.flags.C, False)
        self.assertEqual(self.cpu.flags.A, False)

    def test_rotate_right_a_through_carry(self):
        self.cpu.registers.A = 0b01101010  # 0x6A
        self.cpu.flags.C = True

        self.cpu.rar()

        self.assertEqual(self.cpu.registers.A, 0b10110101)  # 0xB5
        self.assertEqual(self.cpu.flags.S, False)
        self.assertEqual(self.cpu.flags.Z, False)
        self.assertEqual(self.cpu.flags.P, False)
        self.assertEqual(self.cpu.flags.C, False)
        self.assertEqual(self.cpu.flags.A, False)

    def test_sum_register_pair_with_hl(self):
        self.cpu.registers.BC = 0x339F
        self.cpu.registers.HL = 0xA17B
        self.cpu.dad_reg16("BC")

        self.assertEqual(self.cpu.registers.HL, 0xD51A)
        self.assertEqual(self.cpu.flags.S, False)
        self.assertEqual(self.cpu.flags.Z, False)
        self.assertEqual(self.cpu.flags.P, False)
        self.assertEqual(self.cpu.flags.C, False)
        self.assertEqual(self.cpu.flags.A, False)

    def test_exchange_register_pairs(self):
        self.cpu.registers.HL = 0x00FF
        self.cpu.registers.DE = 0x3355

        self.cpu.xchg()

        self.assertEqual(self.cpu.registers.HL, 0x3355)
        self.assertEqual(self.cpu.registers.DE, 0x00FF)

    def test_add_immediate_to_accumulator(self):
        self.cpu.registers.A = 0x14
        self.cpu.PC = 0x0000
        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.adi_d8()
        self.assertEqual(self.cpu.registers.A, 0x56)

        self.cpu.adi_d8()
        self.assertEqual(self.cpu.registers.A, 0x14)
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
        self.cpu.registers.HL = 0x00FF

        self.cpu.push("HL")

        self.assertEqual(self.cpu.memory[self.cpu.SP], 0xFF)
        self.assertEqual(self.cpu.memory[self.cpu.SP - 1], 0x00)
        self.assertEqual(self.cpu.SP, 0xFFFE)

    def test_add_register_to_accumulator(self):
        self.cpu.registers.A = 0x33
        self.cpu.registers.C = 0x0F

        self.cpu.add_reg("C")

        self.assertEqual(self.cpu.registers.A, 0x42)
        self.assertEqual(self.cpu.registers.C, 0x0F)

        self.assertEqual(self.cpu.flags.S, False)
        self.assertEqual(self.cpu.flags.Z, False)
        self.assertEqual(self.cpu.flags.P, True)
        self.assertEqual(self.cpu.flags.C, False)
        self.assertEqual(self.cpu.flags.A, True)

    def test_exchange_sp_with_hl(self):
        self.cpu.SP = 0xAABB
        self.cpu.registers.HL = 0x00CC

        self.cpu.memory[self.cpu.SP] = 0xDD
        self.cpu.memory[self.cpu.SP + 1] = 0xDE

        self.cpu.xthl()

        self.assertEqual(self.cpu.registers.HL, 0xDEDD)  # SP, SP + 1
        self.assertEqual(self.cpu.memory[self.cpu.SP], 0xCC)  # L
        self.assertEqual(self.cpu.memory[self.cpu.SP + 1], 0x00)  # H

    def test_increment_memory_address_on_hl(self):
        self.cpu.registers.HL = 0x0000
        self.cpu.memory[0x0000] = 0x19

        self.cpu.inr_m()

        self.assertEqual(self.cpu.memory[0x0000], 0x1A)
        self.assertEqual(self.cpu.flags.S, False)
        self.assertEqual(self.cpu.flags.Z, False)
        self.assertEqual(self.cpu.flags.P, False)
        self.assertEqual(self.cpu.flags.C, False)
        self.assertEqual(self.cpu.flags.A, False)

    def test_accumulator_and_immediate(self):
        self.cpu.registers.A = 0x14
        self.cpu.PC = 0x0000
        self.cpu.memory[0x0000] = 0x42

        self.cpu.ani_d8()

        self.assertEqual(self.cpu.registers.A, 0x00)
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

        self.cpu.jm_addr()

        self.assertEqual(self.cpu.PC, 0xBE42)

    def test_jump_if_minus_opposite(self):
        self.cpu.PC = 0x0000

        self.cpu.flags.S = False
        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.jm_addr()

        self.assertEqual(self.cpu.PC, 0x0002)  # PC + 2 (fetch word)

    def test_substract_immediate_from_accumulator(self):
        self.cpu.registers.A = 0x14
        self.cpu.PC = 0x0000
        self.cpu.memory[0x0000] = 0x42

        self.cpu.sui_d8()

        self.assertEqual(self.cpu.registers.A, 0xD2)
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

        self.assertEqual(self.machine.cpu.registers.C, 0x14)
        self.assertEqual(self.machine.cpu.registers.A, 0x14)

        self.assertEqual(self.machine.cpu.flags.S, False)
        self.assertEqual(self.machine.cpu.flags.Z, True)
        self.assertEqual(self.machine.cpu.flags.P, True)
        self.assertEqual(self.machine.cpu.flags.C, False)
        self.assertEqual(self.machine.cpu.flags.A, True)

    def test_compare_register_with_accumulator_opposite(self):
        self.cpu.registers.A = 0x14
        self.cpu.registers.C = 0x22

        self.cpu.cmp_reg("C")

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

        self.cpu.cnc_addr()

        self.assertEqual(self.cpu.PC, 0xBE42)
        self.assertEqual(self.cpu.SP, 0xFFFE)

    def test_call_if_not_carry_opposite(self):
        self.cpu.flags.C = True
        self.cpu.PC = 0x0000
        self.cpu.SP = 0x0000

        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.cnc_addr()

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

        self.assertEqual(self.machine.cpu.registers.A, 0x14)
        self.assertEqual(self.machine.cpu.registers.HL, 0xFFFF)

        self.assertEqual(self.machine.cpu.flags.S, False)
        self.assertEqual(self.machine.cpu.flags.Z, True)
        self.assertEqual(self.machine.cpu.flags.P, True)
        self.assertEqual(self.machine.cpu.flags.C, False)
        self.assertEqual(self.machine.cpu.flags.A, True)

    def test_compare_register_with_memory_opposite(self):
        self.cpu.registers.A = 0x14
        self.cpu.PC = 0x0000
        self.cpu.memory[0x0000] = 0x42

        self.cpu.cmp_m()

        self.assertEqual(self.cpu.flags.S, True)
        self.assertEqual(self.cpu.flags.Z, False)
        self.assertEqual(self.cpu.flags.P, True)
        self.assertEqual(self.cpu.flags.C, True)
        self.assertEqual(self.cpu.flags.A, True)

    def test_substract_register_from_accumulator(self):
        self.cpu.registers.A = 0x14
        self.cpu.registers.C = 0x14

        self.cpu.sub_reg("C")

        self.assertEqual(self.cpu.registers.A, 0x00)
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
        self.cpu.registers.A = 0x14
        self.cpu.dcr_reg("A")

        self.assertEqual(self.cpu.registers.A, 0x13)
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

        self.cpu.jnz_addr()

        self.assertEqual(self.cpu.PC, 0xBE42)

        self.cpu.PC = 0x0000
        self.cpu.flags.clear_flags()
        self.cpu.flags.Z = True

        self.cpu.jnz_addr()

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

        self.cpu.rnc()

        self.assertEqual(self.cpu.PC, 0xBE42)
        self.assertEqual(self.cpu.SP, 0x0002)

    def test_return_if_not_carry_opposite(self):
        self.cpu.flags.C = True
        self.cpu.PC = 0x0000
        self.cpu.SP = 0x0000

        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.rnc()

        self.assertEqual(self.cpu.PC, 0x0000)
        self.assertEqual(self.cpu.SP, 0x0000)

    def test_return_if_carry(self):
        self.cpu.flags.C = True
        self.cpu.PC = 0x0000
        self.cpu.SP = 0x0000

        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.rc()

        self.assertEqual(self.cpu.PC, 0xBE42)
        self.assertEqual(self.cpu.SP, 0x0002)

    def test_return_if_carry_opposite(self):
        self.cpu.flags.C = False
        self.cpu.PC = 0x0000
        self.cpu.SP = 0x0000

        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.rc()

        self.assertEqual(self.cpu.PC, 0x0000)
        self.assertEqual(self.cpu.SP, 0x0000)

    def test_register_or_with_memory(self):
        self.cpu.registers.A = 0x14
        self.cpu.PC = 0x0000

        self.cpu.memory[0x0000] = 0x14
        self.cpu.registers.HL = 0x0000

        self.cpu.ora_m()

        self.assertEqual(self.cpu.registers.A, 0x14)
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

        self.cpu.jz_addr()

        self.assertEqual(self.cpu.PC, 0xBE42)

        self.cpu.PC = 0x0000
        self.cpu.flags.clear_flags()
        self.cpu.flags.Z = False

        self.cpu.jz_addr()

        self.assertEqual(self.cpu.PC, 0x0002)

    def test_jump_if_parity(self):
        self.cpu.PC = 0x0000

        self.cpu.flags.P = True
        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.jpe_addr()

        self.assertEqual(self.cpu.PC, 0xBE42)

        self.cpu.PC = 0x0000
        self.cpu.flags.clear_flags()
        self.cpu.flags.P = False

        self.cpu.jpe_addr()

        self.assertEqual(self.cpu.PC, 0x0002)

    def test_rotate_left_accumulator(self):
        self.cpu.registers.A = 0x14
        self.cpu.rlc()

        self.assertEqual(self.cpu.registers.A, 0x28)
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

        self.cpu.jnc_addr()

        self.assertEqual(self.cpu.PC, 0xBE42)

        self.cpu.PC = 0x0000
        self.cpu.flags.clear_flags()
        self.cpu.flags.C = True

        self.cpu.jnc_addr()

        self.assertEqual(self.cpu.PC, 0x0002)

    def test_jump_if_carry(self):
        self.cpu.PC = 0x0000

        self.cpu.flags.C = True
        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.jc_addr()

        self.assertEqual(self.cpu.PC, 0xBE42)

        self.cpu.PC = 0x0000
        self.cpu.flags.clear_flags()
        self.cpu.flags.C = False

        self.cpu.jc_addr()

        self.assertEqual(self.cpu.PC, 0x0002)

    def test_push_and_pop_processor_state_word(self):
        self.cpu.PC = 0x0000
        self.cpu.SP = 0x0000
        self.cpu.registers.A = 0x14
        self.cpu.flags.set_flags(0xFF)

        self.cpu.push_psw()
        self.cpu.registers.A = 0x20
        self.cpu.flags.clear_flags()

        self.cpu.pop_psw()

        self.assertEqual(self.cpu.PC, 0x0000)
        self.assertEqual(self.cpu.SP, 0x0000)
        self.assertEqual(self.cpu.registers.A, 0x14)
        self.assertEqual(self.cpu.flags.get_flags(), 0xFF)

    def test_set_carry_flag(self):
        self.cpu.flags.clear_flags()
        self.cpu.stc()
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

        self.cpu.rz()

        self.assertEqual(self.cpu.PC, 0xBE42)
        self.assertEqual(self.cpu.SP, 0x0002)

    def test_return_if_zero_opposite(self):
        self.cpu.flags.Z = False
        self.cpu.PC = 0x0000
        self.cpu.SP = 0x0000

        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.rz()

        self.assertEqual(self.cpu.PC, 0x0000)
        self.assertEqual(self.cpu.SP, 0x0000)

    def test_return_if_not_zero(self):
        self.cpu.flags.Z = False
        self.cpu.PC = 0x0000
        self.cpu.SP = 0x0000

        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.rnz()

        self.assertEqual(self.cpu.PC, 0xBE42)
        self.assertEqual(self.cpu.SP, 0x0002)

    def test_return_if_not_zero_opposite(self):
        self.cpu.flags.Z = True
        self.cpu.PC = 0x0000
        self.cpu.SP = 0x0000

        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.rnz()

        self.assertEqual(self.cpu.PC, 0x0000)
        self.assertEqual(self.cpu.SP, 0x0000)

    def test_decrement_memory_byte(self):
        self.cpu.memory[0x0000] = 0x14
        self.cpu.dcr_m()

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

        self.cpu.cz_addr()

        self.assertEqual(self.cpu.PC, 0xBE42)
        self.assertEqual(self.cpu.SP, 0xFFFE)

    def test_call_if_zero_opposite(self):
        self.cpu.flags.Z = False
        self.cpu.PC = 0x0000
        self.cpu.SP = 0x0000

        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.cz_addr()

        self.assertEqual(self.cpu.PC, 0x0002)
        self.assertEqual(self.cpu.SP, 0x0000)

    def test_call_if_not_zero(self):
        self.cpu.flags.Z = False
        self.cpu.PC = 0x0000
        self.cpu.SP = 0x0000

        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.cnz_addr()

        self.assertEqual(self.cpu.PC, 0xBE42)
        self.assertEqual(self.cpu.SP, 0xFFFE)

    def test_call_if_not_zero_opposite(self):
        self.cpu.flags.Z = True
        self.cpu.PC = 0x0000
        self.cpu.SP = 0x0000

        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.cnz_addr()

        self.assertEqual(self.cpu.PC, 0x0002)
        self.assertEqual(self.cpu.SP, 0x0000)

    def test_substract_immdiate_from_accumulator_with_borrow(self):
        self.cpu.registers.A = 0x14
        self.cpu.memory[0x0000] = 0x21
        self.cpu.sbi_d8()

        self.assertEqual(self.cpu.registers.A, 0xF3)
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

        self.cpu.rm()

        self.assertEqual(self.cpu.PC, 0xBE42)
        self.assertEqual(self.cpu.SP, 0x0002)

    def test_return_if_minus_opposite(self):
        self.cpu.flags.S = False
        self.cpu.PC = 0x0000
        self.cpu.SP = 0x0000

        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.rm()

        self.assertEqual(self.cpu.PC, 0x0000)
        self.assertEqual(self.cpu.SP, 0x0000)

    def test_return_if_parity_event(self):
        self.cpu.flags.P = True
        self.cpu.PC = 0x0000
        self.cpu.SP = 0x0000

        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.rp()

        self.assertEqual(self.cpu.PC, 0xBE42)
        self.assertEqual(self.cpu.SP, 0x0002)

    def test_return_if_parity_opposite(self):
        self.cpu.flags.P = False
        self.cpu.PC = 0x0000
        self.cpu.SP = 0x0000

        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.rp()

        self.assertEqual(self.cpu.PC, 0x0000)
        self.assertEqual(self.cpu.SP, 0x0000)

    def test_call_if_parity_even(self):
        self.cpu.flags.P = True
        self.cpu.PC = 0x0000
        self.cpu.SP = 0x0000

        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.cpe_addr()

        self.assertEqual(self.cpu.PC, 0xBE42)
        self.assertEqual(self.cpu.SP, 0xFFFE)

    def test_call_if_parity_even_opposite(self):
        self.cpu.flags.P = False
        self.cpu.PC = 0x0000
        self.cpu.SP = 0x0000

        self.cpu.memory[0x0000] = 0x42
        self.cpu.memory[0x0001] = 0xBE

        self.cpu.cpe_addr()

        self.assertEqual(self.cpu.PC, 0x02)
        self.assertEqual(self.cpu.SP, 0x0000)

    def test_and_memory_to_accumulator(self):
        self.cpu.registers.A = 0xCC
        self.cpu.memory[0x0000] = 0x0F
        self.cpu.and_memory_to_accumulator()

        self.assertEqual(self.cpu.registers.A, 0x0C)
        self.assertEqual(self.cpu.flags.S, False)
        self.assertEqual(self.cpu.flags.Z, False)
        self.assertEqual(self.cpu.flags.P, True)
        self.assertEqual(self.cpu.flags.C, False)
        self.assertEqual(self.cpu.flags.A, True)

    def test_dcx_reg16(self):
        self.cpu.registers.HL = 0x1234
        self.cpu.dcx_reg16("HL")

        self.assertEqual(self.cpu.registers.HL, 0x1233)

    @unittest.mock.patch("xpire.cpus.cpu.Bus.read")
    def test_input(self, mock_read):
        mock_read.return_value = 0x00
        self.cpu.registers.A = 0x00
        self.cpu.memory[0x0000] = 0x01  # PORT 1
        self.cpu.in_d8()
        self.assertEqual(self.cpu.registers.A, 0x00)
        mock_read.assert_called_once_with(0x01)

    def test_stax_reg(self):
        self.cpu.registers.A = 0x99
        self.cpu.registers.BC = 0x1234
        self.cpu.stax_reg("BC")
        self.assertEqual(self.cpu.memory[0x1234], 0x99)

    def test_daa(self):
        self.cpu.flags.C = True
        self.cpu.flags.A = True
        self.cpu.registers.A = 0x1B
        self.cpu.daa()
        self.assertEqual(self.cpu.registers.A, 0x81)

    def test_daa_no_carry(self):
        self.cpu.flags.C = False
        self.cpu.flags.A = False
        self.cpu.registers.A = 0x11
        self.cpu.daa()
        self.assertEqual(self.cpu.registers.A, 0x11)

    def test_adc_reg(self):
        self.cpu.flags.C = True
        self.cpu.registers.A = 0x1B
        self.cpu.registers.B = 0x1B
        self.cpu.adc_reg("B")
        self.assertEqual(self.cpu.registers.A, (0x1B + 0x1B + 1))

    def test_ldax_reg16(self):
        self.cpu.registers.BC = 0x1234
        self.cpu.write_memory_byte(self.cpu.registers.BC, 0x99)
        self.cpu.ldax_reg16("BC")
        self.assertEqual(self.cpu.registers.A, 0x99)

    def test_ral(self):
        self.cpu.flags.C = True
        self.cpu.registers.A = 0b01000000
        self.cpu.ral()
        self.assertEqual(self.cpu.registers.A, 0b10000001)
        self.assertEqual(self.cpu.flags.C, False)

    def test_shld(self):
        self.cpu.memory[0x00] = 0xFE
        self.cpu.memory[0x01] = 0xFF
        self.cpu.registers.HL = 0x1234
        self.cpu.shld()
        self.assertEqual(self.cpu.PC, 0x0002)
        self.assertEqual(self.cpu.memory[0xFFFE], 0x34)
        self.assertEqual(self.cpu.memory[0xFFFF], 0x12)

    def test_lhld(self):
        self.cpu.memory[0x00] = 0xFE
        self.cpu.memory[0x01] = 0xFF
        self.cpu.memory[0xFFFE] = 0x34
        self.cpu.memory[0xFFFF] = 0x12
        self.cpu.lhld()
        self.assertEqual(self.cpu.PC, 0x0002)
        self.assertEqual(self.cpu.registers.HL, 0x1234)

    def test_cma(self):
        self.cpu.registers.A = 0x99
        self.cpu.cma()
        self.assertEqual(self.cpu.registers.A, 0x66)

    def test_mvi_m_d8(self):
        self.cpu.memory[0x0000] = 0x99
        self.cpu.registers.HL = 0xFFFF
        self.cpu.memory[self.cpu.registers.HL] = 0x00

        self.cpu.mvi_m_d8()
        self.assertEqual(self.cpu.memory[self.cpu.registers.HL], 0x99)

    def test_dad_sp(self):
        self.cpu.registers.HL = 0x0001
        self.cpu.SP = 0x1234
        self.cpu.dad_sp()
        self.assertEqual(self.cpu.registers.HL, 0x1235)

    def test_lda_addr(self):
        self.cpu.memory[0x0000] = 0xFF
        self.cpu.memory[0x0001] = 0xFF
        self.cpu.memory[0xFFFF] = 0x99
        self.cpu.lda_addr()
        self.assertEqual(self.cpu.registers.A, 0x99)

    def test_mov_reg_m(self):
        self.cpu.registers.HL = 0xFFFF
        self.cpu.memory[0xFFFF] = 0x99
        self.cpu.mov_reg_m("A")
        self.assertEqual(self.cpu.registers.A, 0x99)

    def test_mov_m_reg(self):
        self.cpu.registers.HL = 0xFFFF
        self.cpu.registers.A = 0x99
        self.cpu.mov_m_reg("A")
        self.assertEqual(self.cpu.memory[0xFFFF], 0x99)

    def test_add_m(self):
        self.cpu.registers.A = 0x01
        self.cpu.registers.HL = 0xFFFF
        self.cpu.memory[0xFFFF] = 0x99
        self.cpu.add_m()
        self.assertEqual(self.cpu.registers.A, 0x9A)

    def test_adc_m(self):
        self.cpu.registers.A = 0x01
        self.cpu.registers.HL = 0xFFFF
        self.cpu.memory[0xFFFF] = 0x99
        self.cpu.adc_m()
        self.assertEqual(self.cpu.registers.A, 0x9A)

    def test_sub_m(self):
        self.cpu.registers.A = 0x99
        self.cpu.registers.HL = 0xFFFF
        self.cpu.memory[0xFFFF] = 0x01
        self.cpu.sub_m()
        self.assertEqual(self.cpu.registers.A, 0x98)

    def test_sbb_reg(self):
        self.cpu.registers.A = 0x99
        self.cpu.registers.B = 0x01

        self.cpu.sbb_reg("B")
        self.assertEqual(self.cpu.registers.A, 0x98)

    def test_sbb_m(self):
        self.cpu.registers.A = 0x99
        self.cpu.registers.HL = 0xFFFF
        self.cpu.memory[0xFFFF] = 0x01
        self.cpu.sbb_m()
        self.assertEqual(self.cpu.registers.A, 0x98)

    def test_xra_m(self):
        self.cpu.registers.A = 0x99
        self.cpu.registers.HL = 0xFFFF
        self.cpu.memory[0xFFFF] = 0x01
        self.cpu.xra_m()
        self.assertEqual(self.cpu.registers.A, 0x98)

    def test_aci_d8(self):
        self.cpu.memory[0x0000] = 0x01
        self.cpu.registers.A = 0x99
        self.cpu.aci_d8()
        self.assertEqual(self.cpu.registers.A, 0x9A)

    @unittest.mock.patch("xpire.cpus.cpu.Bus.write")
    def test_out_d8(self, mock_write):
        mock_write.return_value = None
        self.cpu.memory[0x0000] = 0x01
        self.cpu.registers.A = 0x99
        self.cpu.out_d8()
        mock_write.assert_called_once_with(0x01, 0x99)

    def test_pchl(self):
        self.cpu.PC = 0x0000
        self.cpu.registers.HL = 0x1234
        self.cpu.pchl()
        self.assertEqual(self.cpu.PC, 0x1234)

    def test_xri_d8(self):
        self.cpu.memory[0x0000] = 0b00101011
        self.cpu.registers.A = 0b10101010
        self.cpu.xri_d8()
        self.assertEqual(self.cpu.registers.A, 0b10000001)

    def test_ori_d8(self):
        self.cpu.memory[0x0000] = 0b10101010
        self.cpu.registers.A = 0b01010101
        self.cpu.ori_d8()
        self.assertEqual(self.cpu.registers.A, 0b11111111)

    def test_sphl(self):
        self.cpu.SP = 0x0000
        self.cpu.registers.HL = 0x1234
        self.cpu.sphl()
        self.assertEqual(self.cpu.SP, 0x1234)
