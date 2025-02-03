"""
Intel 8080 instruction set.
"""

INC_A = 0x3C
INC_B = 0x04
INC_C = 0x0C
INC_D = 0x14
INC_E = 0x1C
INC_H = 0x24
INC_L = 0x2C

MVI_A = 0x3E
MVI_B = 0x06
MVI_C = 0x0E
MVI_D = 0x16
MVI_E = 0x1E
MVI_H = 0x26
MVI_L = 0x2E

INR_BC = 0x03
INR_DE = 0x13
INR_HL = 0x23

LDA = 0x3A
STA = 0x32

LXI_SP = 0x31
LXI_BC = 0x01
LXI_DE = 0x11
LXI_HL = 0x21

PUSH_BC = 0xC5
PUSH_DE = 0xD5
PUSH_HL = 0xE5

POP_BC = 0xC1
POP_DE = 0xD1
POP_HL = 0xE1

JMP = 0xC3
CALL = 0xCD
RET = 0xC9
