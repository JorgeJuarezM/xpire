import os
import sys

import pygame
from pygame.surface import Surface

from xpire.constants import Colors
from xpire.devices.taito_arcade import FlipFlopD

screen_frequency = 60
cpu_frequency = 2000000

frequency_ratio = cpu_frequency // screen_frequency
flipflop = FlipFlopD()


class GameScene:
    _memory_offset = 0

    def __init__(self):
        self.is_finished = False

    def update(self) -> pygame.surface.Surface:
        """Update the game state."""

    def get_background_color(self) -> tuple[int, int, int]:
        return Colors.BLACK

    def get_ink_color(self) -> tuple[int, int, int]:
        return Colors.WHITE

    def load_rom(self, program_path: str) -> None:
        try:
            file_size = os.path.getsize(program_path)
            if file_size > 0xFFFF:
                raise Exception("ROM is too large, max size is 64kb")

            self.cpu.memory = bytearray(self._memory_offset)
            with open(program_path, "rb") as f:
                self.cpu.memory += bytearray(f.read())
            self.cpu.memory += bytearray(0x10000 - len(self.cpu.memory))
        except FileNotFoundError as e:
            raise Exception(f"ROM not found: {program_path}") from e


class GameManager:

    def __init__(self, scene: GameScene):
        pygame.init()
        pygame.font.init()

        self.screen_size = (800, 600)

        self.scene = scene
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(self.screen_size)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    pygame.display.toggle_fullscreen()

    def print_debug_info(self) -> None:
        my_font = pygame.font.Font("space_invaders.ttf", 20)
        offset = 500

        time_surface = my_font.render(
            f"FPS: {self.clock.get_fps():.0f}", False, (0xFF, 0xFF, 0xFF)
        )
        self.screen.blit(time_surface, (30, 0 + offset))

        time_surface = my_font.render(
            f"Time: {self.clock.get_time()}", False, (0xFF, 0xFF, 0xFF)
        )
        self.screen.blit(time_surface, (30, 50 + offset))

    def start(self):
        running = True
        while running:
            self.clock.tick(60)
            self.screen.fill(Colors.BLACK)
            frame: Surface = self.scene.update()

            self.handle_events()

            scale_x = self.screen.get_width() // frame.get_width()
            scale_y = self.screen.get_height() // frame.get_height()
            scale = min(scale_x, scale_y)

            surface = pygame.transform.scale(
                frame,
                (frame.get_width() * scale, frame.get_height() * scale),
            )

            x_position = (self.screen.get_width() // 2) - (surface.get_width() // 2)
            y_position = (self.screen.get_height() // 2) - (surface.get_height() // 2)
            self.screen.blit(surface, (x_position, y_position))

            # self.print_debug_info()
            pygame.display.update()

            running = not self.scene.is_finished
