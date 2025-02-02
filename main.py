import click
from cpus.intel_8080 import Intel8080
from memory import Memory
from utils import load_program_into_memory


@click.group()
def xpire():
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
    memory = Memory(size=0xFFFF)
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

    if cpu.exception:
        print(f"Exception: {cpu.exception}")


if __name__ == "__main__":
    xpire()
