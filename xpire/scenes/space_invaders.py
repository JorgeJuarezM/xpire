import pygame

from xpire.cpus.intel_8080 import Intel8080
from xpire.devices.bus import Bus
from xpire.devices.device import (
    DummyDevice,
    DummyInput,
    P1Controls,
    P2Controls,
    Shifter,
)
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
        self.p2_controller = P2Controls()
        self.dummy_input = DummyInput()

        self.dummy_device = DummyDevice()
        self.shifter = Shifter()

        self.bus.register_device(Bus.DeviceTypes.WRITE, 2, self.shifter.write_offset)
        self.bus.register_device(Bus.DeviceTypes.WRITE, 3, self.dummy_device.write)
        self.bus.register_device(Bus.DeviceTypes.WRITE, 4, self.shifter.write_value)
        self.bus.register_device(Bus.DeviceTypes.WRITE, 5, self.dummy_device.write)
        self.bus.register_device(Bus.DeviceTypes.WRITE, 6, self.dummy_device.write)

        self.bus.register_device(Bus.DeviceTypes.READ, 0, self.dummy_input.read)
        self.bus.register_device(Bus.DeviceTypes.READ, 1, self.p1_controller.read)
        self.bus.register_device(Bus.DeviceTypes.READ, 2, self.p2_controller.read)
        self.bus.register_device(Bus.DeviceTypes.READ, 3, self.shifter.read)

        self.surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    @property
    def bus(self):
        return self.cpu.bus

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
