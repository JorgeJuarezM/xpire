"""
Main module for the CPU emulator.
"""

from cpu import CPU, SystemHalt
import sys
from memory import Memory
from utils import load_program_into_memory


def main():
    memory = Memory()
    cpu = CPU(memory=memory)
    try:
        load_program_into_memory(memory, "test.com")
        cpu.execute()
    except SystemHalt:
        print("========= Flags =========")
        print(f"Z: {cpu.Flags.Z}")
        print(f"S: {cpu.Flags.S}")
        print(f"O: {cpu.Flags.O}")
        print(f"C: {cpu.Flags.C}")

        print("========= Stack =========")
        print(f"SP: 0x{cpu.SP:02x} -> {cpu.SP}")
        print(f"PC: 0x{cpu.PC:02x} -> {cpu.PC}")
        print(f"STACK: 0x{cpu.STACK:02x} -> {cpu.STACK}")

        print("========= Registers =========")
        print(f"A: 0x{cpu.A:02x} -> {cpu.A}")
        print(f"B: 0x{cpu.B:02x} -> {cpu.B}")
        print(f"C: 0x{cpu.C:02x} -> {cpu.C}")
        print(f"D: 0x{cpu.D:02x} -> {cpu.D}")

        print("========= Memory Dump =========")
        print(memory.dump())

        sys.exit(0)


if __name__ == "__main__":
    main()
