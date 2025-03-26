import os

import pygame

from xpire.cpus.intel_8080 import Intel8080
from xpire.devices.bus import Bus
from xpire.devices.device import Device, P1Controls, Shifter
from xpire.engine import GameScene

SCREEN_WIDTH = 256
SCREEN_HEIGHT = 224
SCREEN_LINE_SIZE = 32
VIDEO_MEMORY_BASE = 0x2400

SCREEN_FREQUENCY = 60
CPU_FREQUENCY = 2000000
CYCLES_PER_LINE = CPU_FREQUENCY // SCREEN_FREQUENCY // SCREEN_HEIGHT


class SpaceInvadersScene(GameScene):

    def __init__(self):
        super().__init__()
        self.cpu = Intel8080()
        self.p1_controller = P1Controls()
        self.cpu.bus.add_device(Bus.Addresss.SHIFTER, Shifter())
        self.cpu.bus.add_device(Bus.Addresss.P1_CONTROLLER, self.p1_controller)
        self.cpu.bus.add_device(Bus.Addresss.P2_CONTROLLER, Device())
        self.cpu.bus.add_device(Bus.Addresss.DUMMY_DEVICE, Device())
        self.surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

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

    def handle_interrupts(self, line_number=0):
        line_number += 1
        if line_number == 96:
            self.cpu.execute_interrupt(0xCF)
        if line_number == 224:
            self.cpu.execute_interrupt(0xD7)

    def draw_line(self, line):
        counter = line * SCREEN_LINE_SIZE
        memory_base = VIDEO_MEMORY_BASE + counter
        for value in self.cpu.memory[memory_base : memory_base + SCREEN_LINE_SIZE]:
            x = counter % SCREEN_LINE_SIZE
            y = counter // SCREEN_LINE_SIZE
            for i in range(8):
                if value & (1 << i):
                    self.surface.set_at((x * 8 + i, y), self.get_ink_color())
            counter += 1

    def get_frame(self):
        return pygame.transform.rotate(self.surface, 90)

    def clear_screen(self):
        self.surface.fill(self.get_background_color())

    def update(self) -> pygame.surface.Surface:
        """Update the game state."""
        self.handle_events()
        self.clear_screen()

        cycles = CYCLES_PER_LINE
        for line_number in range(SCREEN_HEIGHT):
            self.cpu.cycles = 0
            self.draw_line(line_number)
            self.handle_interrupts(line_number)
            while self.cpu.cycles < cycles:
                self.cpu.execute_instruction()
        return self.get_frame()
