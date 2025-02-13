"""
Main module for the Xpire package.

This module contains the main entry point for the Xpire package.
It provides a command-line interface for loading and running
CP/M-80 programs on the Intel 8080 CPU.
"""

from collections import deque

import click
import pygame

from xpire.cpus.intel_8080 import Intel8080
from xpire.memory import Memory
from xpire.screen import Screen
from xpire.utils import load_program_into_memory


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


@xpire.command()
@click.argument(
    "program_file",
    type=click.Path(exists=True, resolve_path=True),
    required=True,
    metavar="FILE",
)
def run(program_file: str) -> None:
    """
    Run a CP/M-80 program.

    This command runs a CP/M-80 program contained in the given file.
    The program is loaded into memory and executed on the Intel 8080 CPU.
    The program is executed until it completes or raises an exception.

    The final values of the CPU registers and any exception that may have occurred
    are displayed after the program completes.

    :param program_file: The file containing the CP/M-80 program to run.
    """
    memory = Memory(size=0xFFFF)
    cpu = Intel8080(memory=memory)
    interrupts = deque()

    load_program_into_memory(memory, program_file)
    screen = Screen(224, 256, "Xpire", scale=3)

    running = True
    while running:
        if cpu.interrupts_enabled:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            if cpu.cycles > 200000 / 60:
                screen.render(cpu)
                interrupts.extend((207, 215))
                interrupt = interrupts.popleft()
                cpu.execute_interrupt(interrupt)
                cpu.cycles = 0
                continue

        cpu.execute_instruction()


if __name__ == "__main__":
    xpire()
