import math
import time

import pygame

from xpire.cpus.cpu import AbstractCPU


class Screen:
    def __init__(self, width: int, height: int, title: str, scale: int = 1):

        pygame.init()
        pygame.font.init()

        self.scale = scale
        self.width = width
        self.height = height
        self.title = title
        self.running = True
        self.fps = 60

        self.clock = pygame.time.Clock()

        self._screen = pygame.Surface((self.width, self.height))
        self.screen = pygame.display.set_mode(
            (self.width * scale, self.height * scale), pygame.RESIZABLE
        )
        pygame.display.set_caption(self.title)
        self.color_table = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255)]
        self.video_data = []
        pygame.display.flip()
        self.current_time = time.perf_counter()

    def resize(self) -> None:
        scaled = pygame.transform.scale(
            self._screen, (self.screen.get_width(), self.screen.get_height())
        )
        self.screen.blit(scaled, (0, 0))

    def render(self, cpu: AbstractCPU) -> None:
        self.update(cpu)
        self.resize()
        self.print_debug_info(cpu, self.screen)
        pygame.display.update()

    def render_pixel(self, pixel_index, x, y) -> None:
        pixel = self.video_data[pixel_index]
        color_index = pixel_index % 256 / (256 / self.color_table.__len__())
        color = self.color_table[math.floor(color_index)]
        if pixel:
            self._screen.set_at((x, y), color)

    def rasterize(self, cpu: AbstractCPU) -> None:
        self.video_data = []
        for i in range(0x2400, 0x4000):
            memory_value = cpu.read_memory_byte(i)
            for j in range(0x08):
                if memory_value & (1 << j):
                    self.video_data.append(1)
                else:
                    self.video_data.append(0)

    def update(self, cpu: AbstractCPU) -> None:
        self._screen.fill((0, 0, 0))
        self.rasterize(cpu)
        counter = 0
        for x in range(self.width):
            for y in reversed(range(self.height)):
                self.render_pixel(counter, x, y)
                counter += 1

    def print_debug_info(self, cpu: AbstractCPU, target: pygame.Surface) -> None:
        my_font = pygame.font.SysFont("Comic Sans MS", 18)
        text_surface = my_font.render(f"PC: 0x{cpu.PC:04X}", False, (0xFF, 0xFF, 0xFF))
        target.blit(text_surface, (5, 100))

        elapsed_time = time.perf_counter() - self.current_time
        fps = math.floor(1 / elapsed_time)

        time_surface = my_font.render(f"FPS: {fps}", False, (0xFF, 0xFF, 0xFF))
        target.blit(time_surface, (5, 120))
        self.current_time = time.perf_counter()
