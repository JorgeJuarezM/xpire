import sys

import pygame

from xpire.devices.taito_arcade import FlipFlopD

screen_frequency = 60
cpu_frequency = 2000000

frequency_ratio = cpu_frequency // screen_frequency
flipflop = FlipFlopD()


WHITE = (0xFF, 0xFF, 0xFF)
RED = (0xFF, 0x00, 0x00)
GREEN = (0x00, 0xFF, 0x00)
BLUE = (0x00, 0x00, 0xFF)


class GameScene:
    def update(self):
        """Update the game state."""


class GameManager:

    def __init__(self, scene: GameScene):
        pygame.init()

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
        while True:
            self.clock.tick(60)
            self.screen.fill((0, 0, 0))

            self.handle_events()
            surface = self.scene.update()
            surface = pygame.transform.scale(
                surface, (surface.get_width() * 2, surface.get_height() * 2)
            )

            x_position = self.screen.get_width() // 2 - surface.get_width() // 2
            y_position = self.screen.get_height() // 2 - surface.get_height() // 2
            self.screen.blit(surface, (x_position, y_position))

            self.print_debug_info()
            pygame.display.update()
