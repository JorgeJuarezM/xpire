"""
Decorators for the CPU emulator.

This module defines decorators that are used to modify the behavior
of CPU instructions. 
"""

from utils import reset_value_if_overflow
from cpus.abstract import AbstractCPU


def increment_program_counter():
    def wrapper(func):
        def wrapped(self: AbstractCPU, *args, **kwargs):
            result = func(self, *args, **kwargs)
            self.PC += 1
            return result

        return wrapped

    return wrapper


def increment_stack_pointer():
    def wrapper(func):
        def wrapped(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            self.SP = reset_value_if_overflow(self.SP + 0x02, self.memory.max_address())
            return result

        return wrapped

    return wrapper
