"""
Test class for ADD Instruction.

Thanks to GunshipPenguin for the test cases.
    https://github.com/GunshipPenguin/lib8080/blob/master/test/unit/instructions/add_test.c
"""

from tests.base.intel_8080 import Intel8080_Base


class Test_ADD_Instruction(Intel8080_Base):

    def test_add_b(self):
        self.cpu.write_memory_byte(0x0000, 0x80)  # ADD B
        self.cpu.registers.B = 0x01
        self.cpu.registers.A = 0x00

        self.cpu.execute_instruction()

        self.assertEqual(self.cpu.registers.A, 0x01)
        self.assertEqual(self.cpu.PC, 0x0001)
        self.assertEqual(self.cpu.cycles, 4)

    def test_add_c(self):
        self.cpu.write_memory_byte(0x0000, 0x81)  # ADD C
        self.cpu.registers.C = 0x01
        self.cpu.registers.A = 0x00

        self.cpu.execute_instruction()

        self.assertEqual(self.cpu.registers.A, 0x01)
        self.assertEqual(self.cpu.PC, 0x0001)
        self.assertEqual(self.cpu.cycles, 4)

    def test_add_d(self):
        self.cpu.write_memory_byte(0x0000, 0x82)
        self.cpu.registers.D = 0x01
        self.cpu.registers.A = 0x00

        self.cpu.execute_instruction()

        self.assertEqual(self.cpu.registers.A, 0x01)
        self.assertEqual(self.cpu.PC, 0x0001)
        self.assertEqual(self.cpu.cycles, 4)

    def test_add_e(self):
        self.cpu.write_memory_byte(0x0000, 0x83)
        self.cpu.registers.E = 0x01
        self.cpu.registers.A = 0x00

        self.cpu.execute_instruction()

        self.assertEqual(self.cpu.registers.A, 0x01)
        self.assertEqual(self.cpu.PC, 0x0001)
        self.assertEqual(self.cpu.cycles, 4)

    def test_add_h(self):
        self.cpu.write_memory_byte(0x0000, 0x84)
        self.cpu.registers.H = 0x01
        self.cpu.registers.A = 0x00

        self.cpu.execute_instruction()

        self.assertEqual(self.cpu.registers.A, 0x01)
        self.assertEqual(self.cpu.PC, 0x0001)
        self.assertEqual(self.cpu.cycles, 4)

    def test_add_l(self):
        self.cpu.write_memory_byte(0x0000, 0x85)
        self.cpu.registers.L = 0x01
        self.cpu.registers.A = 0x00

        self.cpu.execute_instruction()

        self.assertEqual(self.cpu.registers.A, 0x01)
        self.assertEqual(self.cpu.PC, 0x0001)
        self.assertEqual(self.cpu.cycles, 4)

    def test_add_m(self):
        self.cpu.write_memory_byte(0x0000, 0x86)
        self.cpu.write_memory_byte(0x0008, 0x01)
        self.cpu.registers.A = 0x00
        self.cpu.registers.HL = 0x0008

        self.cpu.execute_instruction()

        self.assertEqual(self.cpu.registers.A, 0x01)
        self.assertEqual(self.cpu.PC, 0x0001)
        self.assertEqual(self.cpu.cycles, 7)

    def test_add_a(self):
        self.cpu.write_memory_byte(0x0000, 0x87)
        self.cpu.registers.A = 0x01

        self.cpu.execute_instruction()

        self.assertEqual(self.cpu.registers.A, 0x02)
        self.assertEqual(self.cpu.PC, 0x0001)
        self.assertEqual(self.cpu.cycles, 4)

    def test_set_zero_flag(self):
        self.cpu.write_memory_byte(0x0000, 0x80)  # ADD B
        self.cpu.registers.A = 0x00
        self.cpu.registers.B = 0x00

        self.cpu.flags.Z = False

        self.cpu.execute_instruction()

        self.assertTrue(self.cpu.flags.Z)

    def test_set_parity_flag(self):
        self.cpu.write_memory_byte(0x0000, 0x80)
        self.cpu.registers.A = 0x02
        self.cpu.registers.B = 0x01

        self.cpu.flags.P = False

        self.cpu.execute_instruction()

        self.assertTrue(self.cpu.flags.P)

    def test_set_sign_flag(self):
        self.cpu.write_memory_byte(0x0000, 0x80)
        self.cpu.registers.A = 0x7F
        self.cpu.registers.B = 0x01

        self.cpu.flags.S = False

        self.cpu.execute_instruction()

        self.assertTrue(self.cpu.flags.S)

    def test_set_auxiliary_carry_flag(self):
        self.cpu.write_memory_byte(0x0000, 0x80)
        self.cpu.registers.A = 0x0F
        self.cpu.registers.B = 0x01

        self.cpu.flags.AC = False

        self.cpu.execute_instruction()

        self.assertTrue(self.cpu.flags.A)

    def test_set_carry_flag(self):
        self.cpu.write_memory_byte(0x0000, 0x80)
        self.cpu.registers.A = 0xFF
        self.cpu.registers.B = 0x01

        self.cpu.flags.C = False

        self.cpu.execute_instruction()

        self.assertTrue(self.cpu.flags.C)
