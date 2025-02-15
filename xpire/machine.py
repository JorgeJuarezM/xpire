import pygame

from xpire.cpus.intel_8080 import Intel8080
from xpire.devices.taito_arcade import FlipFlopD
from xpire.memory import Memory
from xpire.screen import Screen
from xpire.utils import load_program_into_memory


class Machine:
    def __init__(self):
        self.clock_frequency = 2100000  # 2MHz
        self.screen_refresh_rate = 60  # 60Hz
        self.screen_refresh_interval = self.clock_frequency / self.screen_refresh_rate

        self.flipflop = FlipFlopD()
        self.clock = pygame.time.Clock()
        self.memory = Memory(size=0xFFFF)
        self.cpu = Intel8080(memory=self.memory)
        self.screen = Screen(width=224, height=256, title="Xpire", scale=3)
        self.running = False

    def has_interruption(self):
        return (
            self.cpu.interrupts_enabled
            and self.cpu.cycles > self.screen_refresh_interval
        )

    def render_screen(self):
        self.screen.render(self.cpu)
        self.execute_screen_interruption()

    def execute_screen_interruption(self):
        opcode = self.flipflop.switch()
        self.cpu.execute_interrupt(opcode)

    def process_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def process_interruptions(self):
        if self.has_interruption():
            self.process_input()
            self.render_screen()
            self.cpu.cycles = 0

    def load_rom(self, program_path: str):
        load_program_into_memory(self.memory, program_path)

    def run(self):
        self.running = True
        while self.running:
            self.process_interruptions()
            self.cpu.execute_instruction()
