"""
Intel 8080 instruction set.
"""

# Increment 8-bit registers
INC_A = 0x3C
INC_B = 0x04
INC_C = 0x0C
INC_D = 0x14
INC_E = 0x1C
INC_H = 0x24
INC_L = 0x2C

# Move immediate value to 8-bit register
MVI_A = 0x3E
MVI_B = 0x06
MVI_C = 0x0E
MVI_D = 0x16
MVI_E = 0x1E
MVI_H = 0x26
MVI_L = 0x2E

# Increment 16-bit register pair
INR_BC = 0x03
INR_DE = 0x13
INR_HL = 0x23

# Load and store accumulator from/to memory
STA = 0x32
LDA = 0x3A

# Load immediate value to 16-bit register
LXI_BC = 0x01
LXI_DE = 0x11
LXI_HL = 0x21

# Load immediate value to stack pointer
LXI_SP = 0x31

# Stack operations
PUSH_BC = 0xC5
PUSH_DE = 0xD5
PUSH_HL = 0xE5

POP_BC = 0xC1
POP_DE = 0xD1
POP_HL = 0xE1

# Control flow
JMP = 0xC3
RET = 0xC9
CALL = 0xCD
