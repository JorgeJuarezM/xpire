import os

import pygame

from xpire.cpus.intel_8080 import Intel8080
from xpire.devices.taito_arcade import FlipFlopD
from xpire.engine import GameScene

screen_frequency = 60
cpu_frequency = 2000000

frequency_ratio = cpu_frequency // screen_frequency
flipflop = FlipFlopD()


WHITE = (0xFF, 0xFF, 0xFF)
RED = (0xFF, 0x00, 0x00)
GREEN = (0x00, 0xFF, 0x00)
BLUE = (0x00, 0x00, 0xFF)
BLACK = (0x00, 0x00, 0x00)


class SpaceInvadersScene(GameScene):

    def __init__(self):
        self.cpu = Intel8080()

    def load_rom(self, program_path: str) -> None:
        try:
            file_size = os.path.getsize(program_path)
            if file_size > 0xFFFF:
                raise Exception("ROM is too large, max size is 64kb")

            with open(program_path, "rb") as f:
                self.cpu.memory = bytearray(f.read())
            self.cpu.memory += bytearray(0x10000 - len(self.cpu.memory))
        except FileNotFoundError as e:
            raise Exception(f"ROM not found: {program_path}") from e

    def render(self):
        surface = pygame.Surface((256, 224))
        counter = 0
        for value in self.cpu.memory[0x2400:0x4000]:
            x = counter % 32
            y = counter // 32
            for i in range(8):
                if value & (1 << i):
                    surface.set_at((x * 8 + i, y), WHITE)
            counter += 1

        # Draw rect around the screen
        pygame.draw.rect(surface, RED, (0, 0, 256, 224), 1)
        return pygame.transform.rotate(surface, 90)
        # return surface

    def handle_events(self):
        self.cpu.port_1 = 0x08
        if pygame.key.get_pressed()[pygame.K_c]:
            self.cpu.port_1 |= 0x01
        if pygame.key.get_pressed()[pygame.K_RETURN]:
            self.cpu.port_1 |= 0x04
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            self.cpu.port_1 |= 0x10
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            self.cpu.port_1 |= 0x20
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            self.cpu.port_1 |= 0x40

    def update(self):
        """Update the game state."""
        opcode = flipflop.switch()
        self.cpu.execute_interrupt(opcode)
        self.cpu.cycles = 0

        self.handle_events()

        while frequency_ratio > self.cpu.cycles:
            if self.cpu.halted:
                raise Exception("CPU is halted")
            self.cpu.execute_instruction()

        return self.render()
