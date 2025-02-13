"""
Decorators for the CPU emulator.

This module defines decorators that are used to modify the behavior
of CPU instructions.
"""

from typing import Callable

from xpire.cpus.abstract import AbstractCPU


def increment_program_counter() -> Callable:
    """
    Increment the program counter by one after an instruction has been executed.

    This decorator can be used to automatically increment the program counter
    after an instruction has been executed. It assumes that the instruction does
    not modify the program counter itself.

    Args:
        func (function): The instruction to be decorated.
    """

    def wrapper(func):
        """
        Wrapper function that increments the program counter after an instruction
        has been executed.

        Args:
            self (AbstractCPU): The CPU that the instruction is being executed on.
            *args: Any arguments that the instruction takes.
            **kwargs: Any keyword arguments that the instruction takes.

        Returns:
            The result of the instruction.
        """

        def wrapped(self: AbstractCPU, *args, **kwargs):
            """
            Executes the given function with the provided arguments and
            increments the program counter by one.

            Args:
                self (AbstractCPU): The CPU instance on which the function
                    is executed.
                *args: Variable length argument list for the function.
                **kwargs: Arbitrary keyword arguments for the function.

            Returns:
                The result of executing the given function.
            """

            result = func(self, *args, **kwargs)
            self.PC += 0x01
            return result

        return wrapped

    return wrapper


def increment_stack_pointer() -> Callable:
    """
    Increment the stack pointer by two after an instruction has been executed.

    This decorator can be used to automatically increment the stack pointer
    after an instruction has been executed. It assumes that the instruction does
    not modify the stack pointer itself.

    Args:
        func (function): The instruction to be decorated.
    """

    def wrapper(func):
        """
        Decorator function that wraps an instruction to increment the stack pointer.

        This wrapper function modifies the behavior of the given function to
        automatically increment the stack pointer by two after the function is
        executed. It assumes that the function does not modify the stack pointer
        itself.

        Args:
            func (Callable): The function to be wrapped.

        Returns:
            Callable: The wrapped function with stack pointer increment behavior.
        """

        def wrapped(self, *args, **kwargs):
            """
            Executes the given function with the provided arguments and
            increments the stack pointer by two afterwards.

            Args:
                self (AbstractCPU): The CPU instance on which the function
                    is executed.
                *args: Variable length argument list for the function.
                **kwargs: Arbitrary keyword arguments for the function.

            Returns:
                The result of executing the given function.
            """
            result = func(self, *args, **kwargs)
            self.SP = (self.SP + 0x02) & 0xFFFF
            return result

        return wrapped

    return wrapper
