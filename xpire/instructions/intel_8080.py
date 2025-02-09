"""
Intel 8080 instruction set.
"""

# Increment 8-bit registers
INR_A = 0x3C
INR_B = 0x04
INR_C = 0x0C
INR_D = 0x14
INR_E = 0x1C
INR_H = 0x24
INR_L = 0x2C

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

MOV_B_H = 0x44
MOV_B_A = 0x47
MOV_C_A = 0x4F
MOV_D_A = 0x57
MOV_E_A = 0x5F
MOV_H_A = 0x67
MOV_L_A = 0x6F
MOV_A_B = 0x78
MOV_A_C = 0x79
MOV_A_D = 0x7A
MOV_A_E = 0x7B
MOV_A_H = 0x7C
MOV_A_L = 0x7D

# Move 8-bit register to memory (HL)
MOV_M_B = 0x70
MOV_M_A = 0x77

# Move memory (HL) to 8-bit register
MOV_B_M = 0x46
MOV_C_M = 0x4E
MOV_D_M = 0x56
MOV_E_M = 0x5E
MOV_H_M = 0x66
MOV_A_M = 0x7E

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
ADI = 0xC6

DAD_HL = 0x29  # sum HL with HL, store result in HL
DAD_DE = 0x19  # sum DE with HL, store result in HL
DAD_BC = 0x09

DAD_SP = 0x39


# Exchange registers
XCHG = 0xEB


# Stack operations
PUSH_BC = 0xC5
PUSH_DE = 0xD5
PUSH_HL = 0xE5

PUSH_PSW = 0xF5

POP_BC = 0xC1
POP_DE = 0xD1
POP_HL = 0xE1
POP_PSW = 0xF1

# Logical operations
ORA_B = 0xB0  # OR B with A
ORA_C = 0xB1  # OR C with A
ORA_H = 0xB4  # OR H with A

ORA_M = 0xB6  # OR M (HL) with A

# Control flow
JNZ = 0xC2
JMP = 0xC3
JZ = 0xCA
JNC = 0xD2
JPE = 0xEA
JM = 0xFA

RET = 0xC9
RNC = 0xD0
CALL = 0xCD

# Output
OUT = 0xD3

# Rotate
RAR = 0x1F
RRC = 0x0F


# Logical operations
ANI = 0xE6
XRA = 0xAF
ANA_A = 0xA7

# Interrupts
EI = 0xFB

STC = 0x37
RZ = 0xC8

JC = 0xDA
RC = 0xD8
IN = 0xDB

RNZ = 0xC0


XTHL = 0xE3

PCHL = 0xE9

DCR_M = 0x35

CZ = 0xCC


RST_1 = 0xCF
RST_2 = 0xD7
