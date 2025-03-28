"""
Test class for INR Instruction.

Thanks to chris-j-akers for the test cases.
    https://github.com/chris-j-akers/i8080-javascript/blob/main/src/unit_tests/arithmetic/inr.reg.test.js
"""

from tests.base.intel_8080 import Intel8080_Base

reg_map = {
    "B": 0x04,
    "C": 0x0C,
    "D": 0x14,
    "E": 0x1C,
    "H": 0x24,
    "L": 0x2C,
    "A": 0x3C,
}


class Test_INR_Instruction(Intel8080_Base):

    def test_set_no_flags(self):
        for reg, opcode in reg_map.items():
            self.cpu.registers[reg] = 0x00
            self.cpu.write_memory_byte(0x0000, opcode)  # INR reg

            current_carry = self.cpu.flags.C
            self.cpu.execute_instruction()

            self.assertEqual(
                self.cpu.registers[reg],
                0x01,
                f"Expected {reg} to be incremented to 0x01",
            )
            self.assertEqual(self.cpu.flags.C, current_carry)  # No change
            self.assertFalse(self.cpu.flags.P)
            self.assertFalse(self.cpu.flags.A)
            self.assertFalse(self.cpu.flags.Z)
            self.assertFalse(self.cpu.flags.S)
            self.assertEqual(self.cpu.cycles, 5)
            self.cpu.reset()

    def test_rollover_from_0xff(self):
        for reg, opcode in reg_map.items():
            self.cpu.registers[reg] = 0xFF
            self.cpu.write_memory_byte(0x0000, opcode)

            current_carry = self.cpu.flags.C
            self.cpu.execute_instruction()

            self.assertEqual(
                self.cpu.registers[reg],
                0x00,
                f"Expected {reg} to rollover to 0x00 after incrementing from 0xFF",
            )
            self.assertEqual(self.cpu.flags.C, current_carry)
            self.assertTrue(self.cpu.flags.P)
            self.assertTrue(self.cpu.flags.A)
            self.assertTrue(self.cpu.flags.Z)
            self.assertFalse(self.cpu.flags.S)
            self.assertEqual(self.cpu.cycles, 5)
            self.cpu.reset()

    def test_set_parity_flag(self):
        for reg, opcode in reg_map.items():
            self.cpu.registers[reg] = 0x54  # 84 dec
            self.cpu.write_memory_byte(0x0000, opcode)

            current_carry = self.cpu.flags.C
            self.cpu.execute_instruction()

            self.assertEqual(
                self.cpu.registers[reg],
                0x55,  # 85 dec
                f"Expected {reg} to be incremented to 0x55",
            )
            self.assertEqual(self.cpu.flags.C, current_carry)
            self.assertTrue(self.cpu.flags.P)
            self.assertFalse(self.cpu.flags.A)
            self.assertFalse(self.cpu.flags.Z)
            self.assertFalse(self.cpu.flags.S)
            self.assertEqual(self.cpu.cycles, 5)
            self.cpu.reset()

    def test_set_sign_flag(self):
        for reg, opcode in reg_map.items():
            self.cpu.registers[reg] = 0xAF  # 175 dec
            self.cpu.write_memory_byte(0x0000, opcode)

            current_carry = self.cpu.flags.C
            self.cpu.execute_instruction()

            self.assertEqual(
                self.cpu.registers[reg],
                0xB0,  # 176 dec
                f"Expected {reg} to be incremented to 0xb0",
            )
            self.assertEqual(self.cpu.flags.C, current_carry)
            self.assertFalse(self.cpu.flags.P)
            self.assertTrue(self.cpu.flags.A)
            self.assertFalse(self.cpu.flags.Z)
            self.assertTrue(self.cpu.flags.S)
            self.assertEqual(self.cpu.cycles, 5)
            self.cpu.reset()
