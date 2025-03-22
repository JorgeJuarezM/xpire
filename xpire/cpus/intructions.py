from xpire.cpus.abstract import AbstractCPU


class Instruction:
    _cycles = 0

    def __init__(self, *args) -> None:
        """
        Initialize the instruction.
        """
        self.args = args

    def execute(self, cpu: AbstractCPU) -> int:
        pass

    def execute_instruction(self, cpu: AbstractCPU):
        return self.execute(cpu, *self.args)
