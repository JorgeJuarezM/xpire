from typing import Dict


class RegisterManager:
    registers: Dict[int, int]

    def __init__(self):
        self.registers = {}

    def __getitem__(self, value: int) -> int:
        return self.registers[value]

    def __setitem__(self, key: int, value: int) -> None:
        self.registers[key] = value
