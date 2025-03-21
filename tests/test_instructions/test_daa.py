"""
Test class for DAA Instruction.
"""

import unittest
import unittest.mock

from faker import Faker

from xpire.cpus.intel_8080 import Intel8080


fake = Faker()


def bcd_encode(n):
    l = (n % 10) & 0x0F
    h = (n // 10) & 0x0F
    return (h << 4) | l


def bcd_decode(n):
    l = n & 0x0F
    h = (n >> 4) & 0x0F
    return (h*10) + l

class Test_DAA_Instruction(unittest.TestCase):
    def setUp(self):
        self.cpu = Intel8080()

    def test_cycles(self):
        self.cpu.write_memory_byte(0x0000, 0x27) # DAA
        self.cpu.registers.A = 0x11
        self.cpu.execute_instruction()
        self.assertEqual(self.cpu.cycles, 4)

    def test_1_plus_1(self):
        self.cpu.write_memory_byte(0x0000, 0x80) # ADD 8
        self.cpu.write_memory_byte(0x0001, 0x27) # DAA

        self.cpu.registers.A = bcd_encode(1)
        self.cpu.registers.B = bcd_encode(1)

        self.cpu.execute_instruction()
        self.cpu.execute_instruction()

        self.assertEqual(bcd_decode(self.cpu.registers.A), 2)
        self.assertFalse(self.cpu.flags.A)
        self.assertFalse(self.cpu.flags.C)
        self.assertEqual(self.cpu.PC, 2)

    def test_9_plus_1(self):
        self.cpu.write_memory_byte(0x0000, 0x80) # ADD 8
        self.cpu.write_memory_byte(0x0001, 0x27) # DAA

        self.cpu.registers.A = bcd_encode(9)
        self.cpu.registers.B = bcd_encode(1)

        self.cpu.execute_instruction()
        self.cpu.execute_instruction()

        self.assertEqual(bcd_decode(self.cpu.registers.A), 10)
        self.assertTrue(self.cpu.flags.A)
        self.assertFalse(self.cpu.flags.C)
        self.assertEqual(self.cpu.PC, 2)

    def test_9_plus_10(self):
        self.cpu.write_memory_byte(0x0000, 0x80) # ADD 8
        self.cpu.write_memory_byte(0x0001, 0x27) # DAA

        self.cpu.registers.A = bcd_encode(9)
        self.cpu.registers.B = bcd_encode(10)

        self.cpu.execute_instruction()
        self.cpu.execute_instruction()

        self.assertEqual(bcd_decode(self.cpu.registers.A), 19)
        self.assertFalse(self.cpu.flags.A)
        self.assertFalse(self.cpu.flags.C)
        self.assertEqual(self.cpu.PC, 2)

    def test_22_plus_39(self):
        self.cpu.write_memory_byte(0x0000, 0x80) # ADD 8
        self.cpu.write_memory_byte(0x0001, 0x27) # DAA

        self.cpu.registers.A = bcd_encode(22)
        self.cpu.registers.B = bcd_encode(39)

        self.cpu.execute_instruction()
        self.cpu.execute_instruction()

        self.assertEqual(bcd_decode(self.cpu.registers.A), 61)
        self.assertTrue(self.cpu.flags.A)
        self.assertFalse(self.cpu.flags.C)
        self.assertEqual(self.cpu.PC, 2)

    def test_95_plus_20(self):
        self.cpu.write_memory_byte(0x0000, 0x80) # ADD 8
        self.cpu.write_memory_byte(0x0001, 0x27) # DAA

        self.cpu.registers.A = bcd_encode(95)
        self.cpu.registers.B = bcd_encode(20)

        self.cpu.execute_instruction()
        self.cpu.execute_instruction()

        self.assertEqual(bcd_decode(self.cpu.registers.A), 15)
        self.assertFalse(self.cpu.flags.A)
        self.assertTrue(self.cpu.flags.C)
        self.assertEqual(self.cpu.PC, 2)

    def test_daa_0x3f(self):
        self.cpu.write_memory_byte(0x0000, 0x27) # DAA
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
        #   1
        self.cpu.flags.C = True

        #  2
        self.cpu.registers.A = 0x99
        self.cpu.registers.B = 0x00

        #  3
        self.cpu.write_memory_byte(0x0000, 0x88) # ADC B
        self.cpu.execute_instruction()

        self.assertEqual(self.cpu.registers.A, 0x9A)
        self.assertFalse(self.cpu.flags.C)

        #  4
        self.cpu.registers.B = 3
        self.cpu.write_memory_byte(0x0001, 0x90) # SUB B
        self.cpu.execute_instruction()

        self.assertEqual(bcd_decode(self.cpu.registers.A), 97)

        #  5
        self.cpu.registers.B = bcd_encode(20)
        self.cpu.write_memory_byte(0x0002, 0x80) # ADD B
        self.cpu.execute_instruction()

        self.assertEqual(bcd_decode(self.cpu.registers.A), 117)

        #  6
        self.cpu.write_memory_byte(0x0003, 0x27)
        self.cpu.execute_instruction()

        self.assertEqual(bcd_decode(self.cpu.registers.A), 17)
        self.assertTrue(self.cpu.flags.C)