import os

import pygame

from xpire.cpus.intel_8080 import Intel8080
from xpire.devices.bus import Bus
from xpire.devices.device import Device, P1Controls, Shifter
from xpire.devices.taito_arcade import FlipFlopD
from xpire.engine import GameScene

screen_frequency = 60
cpu_frequency = 2000000

frequency_ratio = cpu_frequency // screen_frequency


WHITE = (0xFF, 0xFF, 0xFF)
RED = (0xFF, 0x00, 0x00)
GREEN = (0x00, 0xFF, 0x00)
BLUE = (0x00, 0x00, 0xFF)
BLACK = (0x00, 0x00, 0x00)


class SpaceInvadersScene(GameScene):

    def __init__(self):
        super().__init__()
        self.cpu = Intel8080()
        self.p1_controller = P1Controls()
        self.cpu.bus.add_device(Bus.Addresss.SHIFTER, Shifter())
        self.cpu.bus.add_device(Bus.Addresss.P1_CONTROLLER, self.p1_controller)
        self.cpu.bus.add_device(Bus.Addresss.P2_CONTROLLER, Device())
        self.cpu.bus.add_device(Bus.Addresss.DUMMY_DEVICE, Device())
        self.clock = pygame.time.Clock()
        self.flipflop = FlipFlopD()

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
        return pygame.transform.rotate(surface, 90)

    def handle_events(self):
        self.p1_controller.reset()
        if pygame.key.get_pressed()[pygame.K_c]:
            self.p1_controller.write(0x01)
        if pygame.key.get_pressed()[pygame.K_RETURN]:
            self.p1_controller.write(0x04)
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            self.p1_controller.write(0x10)
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            self.p1_controller.write(0x20)
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            self.p1_controller.write(0x40)

    def handle_interrupts(self):
        opcode = self.flipflop.switch()
        self.cpu.execute_interrupt(opcode)

    def update(self) -> pygame.surface.Surface:
        """Update the game state."""
        self.handle_events()
        self.handle_interrupts()

        while self.cpu.cycles < frequency_ratio:
            self.cpu.execute_instruction()

        self.cpu.cycles = 0
        return self.render()
