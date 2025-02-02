import click
from cpus.intel_8080 import Intel8080
from memory import Memory
from utils import load_program_into_memory
from constants import K_64KB
from exceptions import BaseException


@click.group()
def xpire():
    """
    Xpire is a Python package for emulating CP/M-80 programs
    on the Intel 8080 CPU. It provides a command-line interface
    for loading and running a CP/M-80 program.

    Note that this emulator is not a full CP/M-80 emulator,
    but only an Intel 8080 CPU emulator. It will not provide
    all the features of a full CP/M-80 emulator, such as
    disk I/O, console I/O, or process management.

    This package is intended for educational and development use only.
    """
    pass


@xpire.command()
@click.argument(
    "program_file",
    type=click.Path(
        exists=True,
        resolve_path=True,
    ),
    required=True,
    metavar="FILE",
)
def run(program_file):
    """
    Run a CP/M-80 program.

    This command runs a CP/M-80 program contained in the given file.
    The program is loaded into memory and executed on the Intel 8080 CPU.
    The program is executed until it completes or raises an exception.

    The final values of the CPU registers and any exception that may have occurred
    are displayed after the program completes.

    :param program_file: The file containing the CP/M-80 program to run.
    """

    memory = Memory(size=K_64KB)
    load_program_into_memory(memory, program_file)
    cpu = Intel8080(memory=memory)
    cpu.start()
    cpu.join()

    print("Program execution complete.")
    print(f"Final PC:   0x{cpu.PC:04x}")
    print(f"Final SP:   0x{cpu.SP:04x}")
    print("===================================")
    print(f"Final A:    0x{cpu.REG_A:04x}")
    print(f"Final B:    0x{cpu.REG_B:04x}")
    print(f"Final C:    0x{cpu.REG_C:04x}")
    print(f"Final H:    0x{cpu.REG_H:04x}")
    print(f"Final L:    0x{cpu.REG_L:04x}")

    if cpu.exception:
        if isinstance(cpu.exception, BaseException):
            print(f"Exception: {cpu.exception.message}")
        else:
            print(f"Exception: {cpu.exception}")


if __name__ == "__main__":
    # xpire(args=("run", "test.com"))
    xpire()
