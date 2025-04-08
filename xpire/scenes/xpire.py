import pygame

from xpire.constants import Colors
from xpire.devices.bus import Bus
from xpire.devices.device import Device
from xpire.scenes.space_invaders import SCREEN_WIDTH, SpaceInvadersScene

COLOR_PALETE = [
    Colors.WHITE,
    Colors.BLACK,
]


class XpireScene(SpaceInvadersScene):

    def __init__(self):
        super().__init__()

        self.color_device = Device()

        self.bus.register_device(Bus.DeviceTypes.READ, 255, self.color_device.read)
        self.bus.register_device(Bus.DeviceTypes.WRITE, 255, self.color_device.write)

    def get_background_color(self):
        color_index = self.color_device.read()
        return COLOR_PALETE[color_index]

    def get_ink_color(self):
        color_index = self.color_device.read()
        color_index = (color_index + 1) % len(COLOR_PALETE)
        return COLOR_PALETE[color_index]

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
