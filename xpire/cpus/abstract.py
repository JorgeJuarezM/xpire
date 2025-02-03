"""Abstract class for CPU emulator"""

from abc import abstractmethod


class AbstractCPU:
    """Abstract class for CPU emulator"""

    PC: int
    SP: int

    @abstractmethod
    def halt(self):
        raise NotImplementedError

    @abstractmethod
    def pop(self):
        """Pop a word from the stack"""
        raise NotImplementedError

    @abstractmethod
    def push(self, high_byte: int, low_byte: int) -> None:
        """Push a word to the stack"""
        raise NotImplementedError
