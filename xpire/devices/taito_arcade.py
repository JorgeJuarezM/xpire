"""
Taito Arcade device.
"""


class FlipFlopD:
    """
    Flip-flop D.

    The flip-flop D is a 2-input, 1-output flip-flop.
    """

    MID_SCREEN = 0xCF
    TOP_SCREEN = 0xD7

    state: bool

    def __init__(self):
        """
        Initialize a new FlipFlopD.
        """
        self.state = False

    def switch(self):
        """
        Switch the flip-flop D.
        """
        self.state = not self.state
        return self.MID_SCREEN if self.state else self.TOP_SCREEN
