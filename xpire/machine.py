import sys

import pygame

from xpire.cpus.intel_8080 import Intel8080
from xpire.devices.taito_arcade import FlipFlopD
from xpire.screen import Screen


class Machine:
    def __init__(self):
        self.clock_frequency = 2000000  # 2MHz
        self.screen_refresh_rate = 60  # 60Hz
        self.screen_refresh_interval = self.clock_frequency / self.screen_refresh_rate

        self.flipflop = FlipFlopD()
        self.clock = pygame.time.Clock()
        self.cpu = Intel8080()
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

    def load_rom(self, program_path: str) -> bool:
        try:
            with open(program_path, "rb") as f:
                self.cpu.memory = bytearray(f.read())
            self.cpu.memory += bytearray(0x10000 - len(self.cpu.memory))
            return True
        except FileNotFoundError:
            print(f"ROM not found: {program_path}")
            return False

    def render_menu(self, index: int = 0):
        screen = self.screen.screen

        options = ["Load ROM", "Exit"]

        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 32)
        h_position = 100
        for i, option in enumerate(options):
            if i == index:
                text_color = (0, 0, 0)
                bg_color = (255, 255, 255)
            else:
                text_color = (255, 255, 255)
                bg_color = (0, 0, 0)

            text = font.render(option, True, text_color, bg_color)
            text_rect = text.get_rect(
                center=(
                    screen.get_width() // 2,
                    h_position + (i * 50),
                )
            )
            screen.blit(text, text_rect)

        # self.screen.resize()
        pygame.display.flip()

    def show_menu(self):
        index = 0
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        index += 1
                    elif event.key == pygame.K_UP:
                        index -= 1
                    elif event.key == pygame.K_RETURN:
                        if index == 0:
                            self.running = False
                        elif index == 1:
                            sys.exit(0)

            if index > 1:
                index = 0
            elif index < 0:
                index = 1

            self.render_menu(index=index)
            self.clock.tick(self.screen_refresh_rate)

        # Continue execution
        self.running = True

    def run(self, show_menu: bool = False):
        self.running = True

        if show_menu:
            self.show_menu()

        if not self.running:
            return

        while self.running and not self.cpu.halted:
            self.process_interruptions()
            self.cpu.execute_instruction()
