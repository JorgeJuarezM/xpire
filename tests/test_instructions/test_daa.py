"""
Test class for DAA Instruction.

Thanks to GunshipPenguin for the test cases.
    https://github.com/GunshipPenguin/lib8080/blob/master/test/unit/instructions/daa_test.c
"""

from tests.base.intel_8080 import Intel8080_Base


def bcd_encode(n):
    l = (n % 10) & 0x0F
    h = (n // 10) & 0x0F
    return (h << 4) | l


def bcd_decode(n):
    l = n & 0x0F
    h = (n >> 4) & 0x0F
    return (h * 10) + l


class Test_DAA_Instruction(Intel8080_Base):

    def test_cycles(self):
        self.cpu.write_memory_byte(0x0000, 0x27)  # DAA
        self.cpu.registers.A = 0x11
        self.cpu.execute_instruction()
        self.assertEqual(self.cpu.cycles, 4)

    def test_1_plus_1(self):
        self.cpu.write_memory_byte(0x0000, 0x80)  # ADD 8
        self.cpu.write_memory_byte(0x0001, 0x27)  # DAA

        self.cpu.registers.A = bcd_encode(1)
        self.cpu.registers.B = bcd_encode(1)

        self.cpu.execute_instruction()
        self.cpu.execute_instruction()

        self.assertEqual(bcd_decode(self.cpu.registers.A), 2)
        self.assertFalse(self.cpu.flags.A)
        self.assertFalse(self.cpu.flags.C)
        self.assertEqual(self.cpu.PC, 2)

    def test_9_plus_1(self):
        self.cpu.write_memory_byte(0x0000, 0x80)  # ADD 8
        self.cpu.write_memory_byte(0x0001, 0x27)  # DAA

        self.cpu.registers.A = bcd_encode(9)
        self.cpu.registers.B = bcd_encode(1)

        self.cpu.execute_instruction()
        self.cpu.execute_instruction()

        self.assertEqual(bcd_decode(self.cpu.registers.A), 10)
        self.assertTrue(self.cpu.flags.A)
        self.assertFalse(self.cpu.flags.C)
        self.assertEqual(self.cpu.PC, 2)

    def test_9_plus_10(self):
        self.cpu.write_memory_byte(0x0000, 0x80)  # ADD 8
        self.cpu.write_memory_byte(0x0001, 0x27)  # DAA

        self.cpu.registers.A = bcd_encode(9)
        self.cpu.registers.B = bcd_encode(10)

        self.cpu.execute_instruction()
        self.cpu.execute_instruction()

        self.assertEqual(bcd_decode(self.cpu.registers.A), 19)
        self.assertFalse(self.cpu.flags.A)
        self.assertFalse(self.cpu.flags.C)
        self.assertEqual(self.cpu.PC, 2)

    def test_22_plus_39(self):
        self.cpu.write_memory_byte(0x0000, 0x80)  # ADD 8
        self.cpu.write_memory_byte(0x0001, 0x27)  # DAA

        self.cpu.registers.A = bcd_encode(22)
        self.cpu.registers.B = bcd_encode(39)

        self.cpu.execute_instruction()
        self.cpu.execute_instruction()

        self.assertEqual(bcd_decode(self.cpu.registers.A), 61)
        self.assertTrue(self.cpu.flags.A)
        self.assertFalse(self.cpu.flags.C)
        self.assertEqual(self.cpu.PC, 2)

    def test_95_plus_20(self):
        self.cpu.write_memory_byte(0x0000, 0x80)  # ADD 8
        self.cpu.write_memory_byte(0x0001, 0x27)  # DAA

        self.cpu.registers.A = bcd_encode(95)
        self.cpu.registers.B = bcd_encode(20)

        self.cpu.execute_instruction()
        self.cpu.execute_instruction()

        self.assertEqual(bcd_decode(self.cpu.registers.A), 15)
        self.assertFalse(self.cpu.flags.A)
        self.assertTrue(self.cpu.flags.C)
        self.assertEqual(self.cpu.PC, 2)

    def test_daa_0x3f(self):
        self.cpu.write_memory_byte(0x0000, 0x27)  # DAA
        self.cpu.registers.A = 0x3F

        self.cpu.execute_instruction()

        self.assertEqual(self.cpu.registers.A, 0x45)
        self.assertTrue(self.cpu.flags.A)
        self.assertFalse(self.cpu.flags.C)
        self.assertEqual(self.cpu.PC, 1)

    def test_daa_0xfa(self):
        self.cpu.write_memory_byte(0x0000, 0x27)
        self.cpu.registers.A = 0xFA

        self.cpu.execute_instruction()

        self.assertEqual(self.cpu.registers.A, 0x60)
        self.assertTrue(self.cpu.flags.A)
        self.assertTrue(self.cpu.flags.C)
        self.assertEqual(self.cpu.PC, 1)

    def test_daa_0x11(self):
        self.cpu.write_memory_byte(0x0000, 0x27)
        self.cpu.registers.A = 0x11
        self.cpu.flags.C = True

        self.cpu.execute_instruction()

        self.assertEqual(self.cpu.registers.A, 0x71)
        self.assertFalse(self.cpu.flags.A)
        self.assertFalse(self.cpu.flags.C)
        self.assertEqual(self.cpu.PC, 1)

    def test_daa_20_minus_3(self):
        """
        /*
        * Steps in decimal subtraction on the 8080
        *
        * 1) Set the carry bit to 1 indicating no borrow
        * 2) Load the accumulator with 0x99 representing 99 in decimal
        * 3) Add 0 to the accumulator with carry producing either 0x99 or 0x9A and
        *    resetting the carry bit
        * 4) Subtract the subtrahend digits from the accumulator producing either 99's
        *    or 100's complement
        * 5) Add the minuend digits to the accumulator
        * 6) Use DAA to make sure the result in the accumulator is in decimal format
        *    and to indicate a borrow in the carry bit if one occurred
        * 7) If there are more digits to subtract, got to step 2, otherwise, stop
        */
        """

        #   1
        self.cpu.flags.C = True

        #  2
        self.cpu.registers.A = 0x99
        self.cpu.registers.B = 0x00

        #  3
        self.cpu.write_memory_byte(0x0000, 0x88)  # ADC B
        self.cpu.execute_instruction()

        self.assertEqual(self.cpu.registers.A, 0x9A)
        self.assertFalse(self.cpu.flags.C)

        #  4
        self.cpu.registers.B = 3
        self.cpu.write_memory_byte(0x0001, 0x90)  # SUB B
        self.cpu.execute_instruction()

        self.assertEqual(bcd_decode(self.cpu.registers.A), 97)

        #  5
        self.cpu.registers.B = bcd_encode(20)
        self.cpu.write_memory_byte(0x0002, 0x80)  # ADD B
        self.cpu.execute_instruction()

        self.assertEqual(bcd_decode(self.cpu.registers.A), 117)

        #  6
        self.cpu.write_memory_byte(0x0003, 0x27)
        self.cpu.execute_instruction()

        self.assertEqual(bcd_decode(self.cpu.registers.A), 17)
        self.assertTrue(self.cpu.flags.C)
