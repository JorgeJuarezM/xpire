import pygame

from xpire.constants import Colors
from xpire.scenes.space_invaders import SCREEN_WIDTH, SpaceInvadersScene

COLOR_PALETE = [
    Colors.BLACK,
    Colors.RED,
    Colors.GREEN,
    Colors.BLUE,
    Colors.BLACK,
]


class XpireScene(SpaceInvadersScene):
    def get_background_color(self):
        color_index = self.cpu.memory[0x4000]
        try:
            return COLOR_PALETE[color_index]
        except IndexError:
            return super().get_background_color()

    def get_ink_color(self):
        return Colors.BLACK

    def draw_line(self, line):
        pygame.draw.line(
            self.surface,
            self.get_background_color(),
            (0, line),
            (SCREEN_WIDTH, line),
        )
        return super().draw_line(line)

    def clear_screen(self):
        """Clear the screen (Skip)."""
