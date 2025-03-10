"""
This module contains the exception classes used in the emulator.
"""


class BaseException(Exception):
    """
    Base class for all exceptions.
    """

    def __init__(self, message):
        """
        Initialize a new BaseException with a given message.

        Args:
            message: the message to associate with the exception.
        """
        self.message = message


class SystemHalt(BaseException):
    """
    Exception raised when the system halts.
    """

    def __init__(self):
        """
        Initialize a new SystemHalt exception with a default message.

        This constructor calls the base exception class with a predefined
        message indicating that the system is exiting with a halt signal.
        """

        super().__init__("System exits with halt signal.")


class InvalidMemoryAddress(BaseException):
    """
    Exception raised when an invalid memory address is accessed.
    """

    def __init__(self, address: int):
        """
        Initialize a new InvalidMemoryAddress exception with the given address.

        This constructor calls the base exception class with a message indicating
        the given address is invalid.

        Args:
            address (int): The invalid memory address.
        """
        message = f"Invalid memory address: {address:02x}"
        super().__init__(message)


class InvalidMemoryValue(BaseException):
    """
    Exception raised when an invalid memory value is accessed.
    """

    def __init__(self, address: int, value: int):
        """
        Initialize a new InvalidMemoryValue exception with the given address and value.

        This constructor calls the base exception class with a message indicating
        the given address is invalid.

        Args:
            address (int): The invalid memory address.
            value (int): The invalid memory value.
        """
        message = f"Invalid memory value: 0x{value:02x} at address: {address:02x}"
        super().__init__(message)


class InvalidReadPort(BaseException):
    def __init__(self, port: int):
        message = f"Invalid read port: {port}"
        super().__init__(message)


class InvalidWritePort(BaseException):
    def __init__(self, port: int):
        message = f"Invalid write port: {port}"
        super().__init__(message)


class InvalidReadAddress(BaseException):
    def __init__(self, address: int):
        message = f"Invalid read address: {address}"
        super().__init__(message)


class InvalidWriteAddress(BaseException):
    def __init__(self, address: int):
        message = f"Invalid write address: {address}"
        super().__init__(message)
