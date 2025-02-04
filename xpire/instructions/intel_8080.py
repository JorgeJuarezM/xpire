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

# Decrement 8-bit registers
DCR_A = 0x3D
DCR_B = 0x05
DCR_C = 0x0D
DCR_D = 0x15
DCR_E = 0x1D
DCR_H = 0x25
DCR_L = 0x2D

# Decrement 16-bit register pair
DCX_HL = 0x2B

# Move immediate value to 8-bit register
MVI_A = 0x3E
MVI_B = 0x06
MVI_C = 0x0E
MVI_D = 0x16
MVI_E = 0x1E
MVI_H = 0x26
MVI_L = 0x2E

# Move 8-bit register to other register

MOV_D_A = 0x57
MOV_L_A = 0x6F
MOV_A_H = 0x7C
MOV_A_L = 0x7D
MOV_A_D = 0x0A  # check


# Move 8-bit register to memory (HL)
MOV_M_A = 0x77

# Move immediate value to memory (HL)
MVI_M = 0x36

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

# Load accumulator from memory
LDAX_BC = 0x0A
LDAX_DE = 0x1A

# Load content of address in memory, and next to HL
LHLD = 0x2A

# Compare accumulator with immediate
CPI_A = 0xFE

# Arithmetic operations
ADD_D = 0x82  # sum D with A, store result in A

DAD_HL = 0x29  # sum HL with HL, store result in HL
DAD_DE = 0x19  # sum DE with HL, store result in HL

DAD_SP = 0x39


# Exchange registers
XCHG = 0xEB


# Stack operations
PUSH_BC = 0xC5
PUSH_DE = 0xD5
PUSH_HL = 0xE5

POP_BC = 0xC1
POP_DE = 0xD1
POP_HL = 0xE1

# Logical operations
ORA = 0xB4  # OR H with A

# Control flow
JNZ = 0xC2
JMP = 0xC3
JZ = 0xCA

RET = 0xC9
RNC = 0xD0
CALL = 0xCD

# Output
OUT = 0xD3
