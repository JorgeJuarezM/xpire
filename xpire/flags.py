"""
Flags module for the CPU emulator.

This module defines the FlagsManager class, which represents the flags
of the CPU emulator.
"""


class FlagsManager:
    """
    FlagsManager class for the CPU emulator.
    """

    _flags: int

    def __init__(self):
        """
        Initialize a new FlagsManager object.

        Flags are stored in a 8-bit integer, with the following bits:
            S	Z	0	AC	0	P	1	C

        S: Sign flag
        Z: Zero flag
        AC: Aux carry flag
        P: Parity flag
        C: Carry flag
        """
        self.clear_flags()

    def get_flags(self):
        """
        Get the flags as a 8-bit integer.

        Returns:
            int: The flags as a 8-bit integer.
        """
        return self._flags

    def set_flags(self, flags: int):
        """
        Set the flags to the given value.

        Args:
            flags (int): The value to set the flags to.

        Returns:
            None
        """
        self._flags = flags | 0x02  # Second bit is always set

    def add_flag(self, flag: int):
        """
        Add a specific flag to the flags.

        Args:
            flag (int): The flag to add.

        Returns:
            None
        """
        self._flags |= flag

    def remove_flag(self, flag: int):
        """
        Remove a specific flag from the flags.

        Args:
            flag (int): The flag to remove.

        Returns:
            None
        """
        self._flags &= ~flag

    def check_flag(self, flag: int):
        """
        Check if a specific flag is set.

        Args:
            flag (int): The flag to check.

        Returns:
            bool: True if the flag is set, False otherwise.
        """

        return bool(self._flags & flag)

    def clear_flags(self):
        """
        Clear all flags except the second bit.

        This method resets the flags to their default state with only the
        second bit set, effectively clearing all other flags.
        """

        self._flags = 0x02  # Second bit is always set

    def set_flag(self, flag: int, value: bool):
        self.add_flag(flag) if value else self.remove_flag(flag)

    @property
    def C(self) -> bool:
        return self.check_flag(0x01)

    @C.setter
    def C(self, value: bool) -> None:
        self.set_flag(0x01, value)

    @property
    def P(self) -> bool:
        return self.check_flag(0x04)

    @P.setter
    def P(self, value: bool) -> None:
        self.set_flag(0x04, value)

    @property
    def A(self) -> bool:
        return self.check_flag(0x10)

    @A.setter
    def A(self, value: bool) -> None:
        self.set_flag(0x10, value)

    @property
    def Z(self) -> bool:
        return self.check_flag(0x40)

    @Z.setter
    def Z(self, value: bool) -> None:
        self.set_flag(0x40, value)

    @property
    def S(self) -> bool:
        return self.check_flag(0x80)

    @S.setter
    def S(self, value: bool) -> None:
        self.set_flag(0x80, value)
