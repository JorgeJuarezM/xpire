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

    def resize(self) -> None:
        scaled = pygame.transform.scale(
            self._screen, (self.screen.get_width(), self.screen.get_height())
        )
        self.screen.blit(scaled, (0, 0))

    def render(self, cpu: AbstractCPU) -> None:
        self.update(cpu)
        self.resize()
        self.print_debug_info(cpu, self.screen)
        pygame.display.flip()
        self.clock.tick_busy_loop(self.fps)

    def render_pixel(self, pixel_index, x, y) -> None:
        pixel = self.video_data[pixel_index]
        if pixel:
            self._screen.set_at((x, y), (255, 255, 255))

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
        my_font = pygame.font.Font("space_invaders.ttf", 20)
        offset = 500

        text_surface = my_font.render(f"PC: 0x{cpu.PC:04X}", False, (0xFF, 0xFF, 0xFF))
        target.blit(text_surface, (30, 0 + offset))

        time_surface = my_font.render(
            f"FPS: {self.clock.get_fps():.0f}", False, (0xFF, 0xFF, 0xFF)
        )
        target.blit(time_surface, (30, 50 + offset))

        time_surface = my_font.render(
            f"Time: {self.clock.get_time()}", False, (0xFF, 0xFF, 0xFF)
        )
        target.blit(time_surface, (30, 100 + offset))
