"""
Main module for the Xpire package.

This module contains the main entry point for the Xpire package.
It provides a command-line interface for loading and running
programs on the Intel 8080 CPU.
"""

import traceback

import click

from xpire.engine import GameManager
from xpire.scenes.space_invaders import SpaceInvadersScene
from xpire.scenes.xpire import XpireScene

MACHINE_OPTIONS = [
    "SI",
    "XPIRE",
]

MACHINE_MAP = {
    "SI": SpaceInvadersScene,
    "XPIRE": XpireScene,
}


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
@click.option(
    "-m",
    "--machine",
    "machine",
    type=click.Choice(MACHINE_OPTIONS, case_sensitive=False),
    default="SI",
    help="""
    The machine to run the program on.
    
    Run `xpire machines` for a list of available machines.
    """,
)
def run(program_file: str, machine: str) -> None:
    """Run an Intel 8080 program from a file."""
    try:
        scene = MACHINE_MAP[machine]()
        scene.load_rom(program_file)
        game = GameManager(scene)
        game.start()
    except Exception:
        print(f"Error: {traceback.format_exc()}")
        exit(1)


if __name__ == "__main__":
    xpire()
