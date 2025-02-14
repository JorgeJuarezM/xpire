"""
Main module for the Xpire package.

This module contains the main entry point for the Xpire package.
It provides a command-line interface for loading and running
programs on the Intel 8080 CPU.
"""

import click

from xpire.machine import Machine


@click.group()
def xpire():
    """
    Xpire is a Python package for emulating hardware on the Intel 8080 CPU.
    Provide an environment for running Intel 8080 programs.

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
    """Run an Intel 8080 program from a file."""
    machine = Machine()
    machine.load_rom(program_file)
    machine.run()


if __name__ == "__main__":
    xpire()
