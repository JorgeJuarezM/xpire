class BaseException(Exception):
    """
    Base class for all exceptions.
    """

    def __init__(self, message):
        self.message = message


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
