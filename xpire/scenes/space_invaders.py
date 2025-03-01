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


class SpaceInvadersScene(GameScene):

    def __init__(self):
        self.cpu = Intel8080()
        self.room_path = "drafts/invaders.com"
        self.load_rom(self.room_path)

    def load_rom(self, program_path: str) -> bool:
        try:
            with open(program_path, "rb") as f:
                self.cpu.memory = bytearray(f.read())
            self.cpu.memory += bytearray(0x10000 - len(self.cpu.memory))
        except FileNotFoundError:
            print(f"ROM not found: {program_path}")

    def render(self):
        video_memory = []
        surface = pygame.Surface((224, 256))
        for i in self.cpu.memory[0x2400:0x4000]:
            for j in range(8):
                if i & (1 << j):
                    video_memory.append(1)
                else:
                    video_memory.append(0)

        counter = 0
        for x in range(0, 224):
            for y in reversed(range(0, 256)):
                pixel = video_memory[counter]
                if pixel:
                    surface.set_at((x, y), GREEN)
                counter += 1
        return surface

    def update(self):
        """Update the game state."""
        opcode = flipflop.switch()
        self.cpu.execute_interrupt(opcode)

        while frequency_ratio > self.cpu.cycles:
            self.cpu.execute_instruction()

        self.cpu.cycles = 0
        return self.render()
