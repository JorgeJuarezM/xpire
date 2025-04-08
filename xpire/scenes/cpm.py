import os

import pygame

from xpire.constants import Colors
from xpire.cpus.intel_8080 import Intel8080
from xpire.engine import GameScene


class CPM80_Scene(GameScene):
    _memory_offset = 0x100

    def __init__(self):
        super().__init__()
        pygame.font.init()

        self.surface = pygame.surface.Surface((640, 480))
        self.cpu = Intel8080()
        self.cpu.PC = 0x100

        # self.font = pygame.font.Font(None, 12)
        font_dir_path = os.path.dirname(__file__)
        font_path = os.path.join(
            font_dir_path, "../../" "CPMono_v07/CPMono_v07_Bold.otf"
        )

        self.font = pygame.font.Font(font_path, 12)
        self.text_lines = []

    def load_rom(self, program_path):
        super().load_rom(program_path)
        self.cpu.memory[0x0005] = 0xC9

    def add_line(self):
        if len(self.text_lines) > 0 and self.text_lines[-1] == "":
            return

        self.text_lines.append("")

    def print_char(self, char_value):
        if char_value in ["\n", "\r"]:
            self.add_line()
            return

        if len(self.text_lines) == 0:
            self.add_line()

        if not char_value.isprintable():
            return

        self.text_lines[-1] += char_value

    def print_text(self):
        if self.cpu.PC == 0x0005:
            if self.cpu.registers.C == 0x09:
                de = self.cpu.registers.DE
                print(f"Getting text from DE = {de}")
                print(len(self.cpu.memory))
                v = self.cpu.memory[de]
                while v != ord("$"):
                    self.print_char(chr(v))
                    de += 1
                    v = self.cpu.memory[de]

            if self.cpu.registers.C == 0x02:
                self.print_char(chr(self.cpu.registers.E))

    def draw(self):
        self.surface.fill((0, 0, 0))
        for i, line in enumerate(self.text_lines):
            text = self.font.render(line, True, Colors.GREEN)
            self.surface.blit(text, (2, 2 + (i * 12)))

        # text_pc = self.font.render(f"PC: 0x{self.cpu.PC:04X}", True, Colors.WHITE)
        # self.surface.blit(text_pc, (20, 500))

        # text_a = self.font.render(
        #     f"A: 0x{self.cpu.registers.A:02X}", True, Colors.WHITE
        # )
        # self.surface.blit(text_a, (20, 520))

        # text_b = self.font.render(
        #     f"B: 0x{self.cpu.registers.B:02X}", True, Colors.WHITE
        # )
        # self.surface.blit(text_b, (120, 520))

        # text_c = self.font.render(
        #     f"C: 0x{self.cpu.registers.C:02X}", True, Colors.WHITE
        # )
        # self.surface.blit(text_c, (220, 520))

        # text_d = self.font.render(
        #     f"D: 0x{self.cpu.registers.D:02X}", True, Colors.WHITE
        # )
        # self.surface.blit(text_d, (320, 520))

        # text_e = self.font.render(
        #     f"E: 0x{self.cpu.registers.E:02X}", True, Colors.WHITE
        # )
        # self.surface.blit(text_e, (420, 520))

        # text_h = self.font.render(
        #     f"H: 0x{self.cpu.registers.H:02X}", True, Colors.WHITE
        # )
        # self.surface.blit(text_h, (20, 540))

        # text_l = self.font.render(
        #     f"L: 0x{self.cpu.registers.L:02X}", True, Colors.WHITE
        # )
        # self.surface.blit(text_l, (120, 540))

    def update(self):
        cycles = 2000000 / 60
        while cycles > self.cpu.cycles:
            if self.cpu.PC == 0x0000:
                break

            self.print_text()
            self.cpu.execute_instruction()
            if self.cpu.halted:
                self.is_finished = True
                break

        self.cpu.cycles = 0
        self.draw()
        return self.surface
