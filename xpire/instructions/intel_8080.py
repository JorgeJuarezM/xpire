"""
Intel 8080 instruction set.
"""

# ====================================== #
# ======= Arithmetic operations ======== #
# ====================================== #

# ADD through accumulator and register
ADD_D = 0x82
ADD_E = 0x83
ADD_L = 0x85
ADD_M = 0x86

# ADD through accumulator and immediate
ADI = 0xC6

# Subtract immediate from accumulator
SUI = 0xD6

# ====================================== #
# ========= Logical operations ========= #
# ====================================== #

# AND through accumulator and register
ANA_A = 0xA7
ANA_B = 0xA0
ANA_M = 0xA6

# AND through accumulator and immediate
ANI = 0xE6

# Complement accumulator (NOT A)
CMA = 0x2F

# OR through accumulator and register
ORA_B = 0xB0
ORA_C = 0xB1
ORA_H = 0xB4

# OR through accumulator and memory (HL)
ORA_M = 0xB6

# OR through accumulator and immediate
ORI = 0xF6

# Set carry flag
STC = 0x37

# XOR through accumulator and register
XRA_A = 0xAF
XRA_B = 0xA8


CALL = 0xCD
CMP_H = 0xBC
CNZ = 0xC4
CPE = 0xEC
CPI_A = 0xFE
CZ = 0xCC

DAD_BC = 0x09
DAD_DE = 0x19  # sum DE with HL, store result in HL
DAD_HL = 0x29  # sum HL with HL, store result in HL
DAD_SP = 0x39

DCR_A = 0x3D
DCR_B = 0x05
DCR_C = 0x0D
DCR_D = 0x15
DCR_E = 0x1D
DCR_H = 0x25
DCR_L = 0x2D
DCR_M = 0x35

DCX_HL = 0x2B

EI = 0xFB
IN = 0xDB

INR_A = 0x3C
INR_B = 0x04
INR_C = 0x0C
INR_D = 0x14
INR_E = 0x1C
INR_H = 0x24
INR_L = 0x2C


INX_BC = 0x03
INX_DE = 0x13
INX_HL = 0x23


JC = 0xDA
JM = 0xFA
JMP = 0xC3
JNC = 0xD2
JNZ = 0xC2
JPE = 0xEA
JZ = 0xCA

LDA = 0x3A

LDAX_BC = 0x0A
LDAX_DE = 0x1A

LHLD = 0x2A

LXI_BC = 0x01
LXI_DE = 0x11
LXI_HL = 0x21
LXI_SP = 0x31

MOV_A_A = 0x7F
MOV_A_B = 0x78
MOV_A_C = 0x79
MOV_A_D = 0x7A
MOV_A_E = 0x7B
MOV_A_H = 0x7C
MOV_A_L = 0x7D
MOV_A_M = 0x7E
MOV_B_A = 0x47
MOV_B_C = 0x41
MOV_B_D = 0x42
MOV_B_H = 0x44
MOV_B_L = 0x45
MOV_B_M = 0x46
MOV_C_A = 0x4F
MOV_C_C = 0x49
MOV_C_M = 0x4E
MOV_D_A = 0x57
MOV_D_C = 0x51
MOV_D_M = 0x56
MOV_E_A = 0x5F
MOV_E_B = 0x58
MOV_E_C = 0x59
MOV_E_M = 0x5E
MOV_H_A = 0x67
MOV_H_C = 0x61
MOV_H_M = 0x66
MOV_L_A = 0x6F
MOV_L_B = 0x68
MOV_L_M = 0x6E
MOV_M_A = 0x77
MOV_M_B = 0x70


MVI_A = 0x3E
MVI_B = 0x06
MVI_C = 0x0E
MVI_D = 0x16
MVI_E = 0x1E
MVI_H = 0x26
MVI_L = 0x2E
MVI_M = 0x36

OUT = 0xD3

PCHL = 0xE9

POP_BC = 0xC1
POP_DE = 0xD1
POP_HL = 0xE1
POP_PSW = 0xF1

PUSH_BC = 0xC5
PUSH_DE = 0xD5
PUSH_HL = 0xE5
PUSH_PSW = 0xF5

RAR = 0x1F
RC = 0xD8
RET = 0xC9
RLC = 0x07
RM = 0xF8
RNC = 0xD0
RNZ = 0xC0
RP = 0xF0
RRC = 0x0F

RST_1 = 0xCF
RST_2 = 0xD7
RST_7 = 0xFF

RZ = 0xC8
SBI = 0xDE
SHLD = 0x22


STA = 0x32
STAX_B = 0x02


# ==================
INR_M = 0x34
CNC = 0xD4
MOV_L_C = 0x69
CMP_B = 0xB8
CMP_C = 0xB9
CMP_M = 0xBE


ADD_B = 0x80
ADD_C = 0x81
MOV_M_C = 0x71
MOV_H_L = 0x65
SUB_A = 0x97
XCHG = 0xEB

XTHL = 0xE3
