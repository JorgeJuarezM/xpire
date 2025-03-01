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
        self.scene = scene
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((800, 600))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    pygame.display.toggle_fullscreen()

    def start(self):
        while True:
            self.clock.tick(60)
            self.screen.fill((0, 0, 0))

            self.handle_events()
            surface = self.scene.update()
            surface = pygame.transform.scale(surface, (800, 600))
            self.screen.blit(surface, (0, 0))

            pygame.display.update()
