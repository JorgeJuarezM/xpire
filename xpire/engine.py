import sys

import pygame
from pygame.surface import Surface
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import (
    QApplication,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QBoxLayout,
)
from PyQt5.QtGui import QColor, QFont, QFontDatabase, QKeyEvent

from xpire.cpus.cpu import CPU
from xpire.devices.taito_arcade import FlipFlopD
from xpire.dissasembler import get_decode_opcode
from xpire import resolve_path
from xpire.flags import FlagsManager
from xpire.debugger.app import DebuggerApp
from tkinter import ttk, Tk


class XQLineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setReadOnly(True)

        self.setStyleSheet(
            """
            QLineEdit {
                padding: 5px;
            }
            """
        )


class RightPanel(QWidget):
    def __init__(self):
        super().__init__()
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)

        self.af_textbox = XQLineEdit("0000")
        self.bc_textbox = XQLineEdit("0000")
        self.de_textbox = XQLineEdit("0000")
        self.hl_textbox = XQLineEdit("0000")
        self.pc_textbox = XQLineEdit("0000")
        self.sp_textbox = XQLineEdit("0000")

        af_bc_layout = QHBoxLayout()
        af_bc_layout.addWidget(QLabel("AF"))
        af_bc_layout.addWidget(self.af_textbox)
        af_bc_layout.addWidget(QLabel("BC"))
        af_bc_layout.addWidget(self.bc_textbox)

        de_hl_layout = QHBoxLayout()
        de_hl_layout.addWidget(QLabel("DE"))
        de_hl_layout.addWidget(self.de_textbox)
        de_hl_layout.addWidget(QLabel("HL"))
        de_hl_layout.addWidget(self.hl_textbox)

        pc_sp_layout = QHBoxLayout()
        pc_sp_layout.addWidget(QLabel("PC"))
        pc_sp_layout.addWidget(self.pc_textbox)
        pc_sp_layout.addWidget(QLabel("SP"))
        pc_sp_layout.addWidget(self.sp_textbox)

        self.flags_textbox = XQLineEdit("0  0  0  0  0  0  0  0")
        self.flags_textbox.setFont(QFont("Roboto Mono", 12, QFont.Normal))
        self.flags_textbox.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.flags_label = QLabel("S  Z  -  A  -  P  -  C")
        self.flags_label.setFont(QFont("Roboto Mono", 12, QFont.Normal))
        self.flags_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._layout.addLayout(af_bc_layout)
        self._layout.addLayout(de_hl_layout)
        self._layout.addLayout(pc_sp_layout)
        self._layout.addWidget(self.flags_label)
        self._layout.addWidget(self.flags_textbox)

        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)

    def set_values(self, af: int, bc: int):
        self.af_textbox.setText(f"{af:04X}")
        self.bc_textbox.setText(f"{bc:04X}")

    def set_flags(self, flags: int):
        _flags_str = f"{flags:08b}"
        _separator = " " * 2
        self.flags_textbox.setText(_separator.join(_flags_str))

    def set_pc(self, pc: int):
        self.pc_textbox.setText(f"{pc:04X}")

    def set_sp(self, sp: int):
        self.sp_textbox.setText(f"{sp:04X}")

    def set_de(self, de: int):
        self.de_textbox.setText(f"{de:04X}")

    def set_hl(self, hl: int):
        self.hl_textbox.setText(f"{hl:04X}")


class Debugger(QWidget):

    refresh: pyqtSignal = pyqtSignal()

    def __init__(self, cpu: CPU):
        super().__init__()
        self.cpu = cpu
        self.resize(800, 600)

        QFontDatabase.addApplicationFont(resolve_path("fonts/RobotoMono-Regular.ttf"))

        self.font = QFont("Roboto Mono", 14, QFont.Normal)
        self.setFont(self.font)

        self.initialize_ui()

        self.toggle_interrupt = False

    def initialize_ui(self):
        layout = QHBoxLayout()
        self.setLayout(layout)

        self.list_view = QListWidget()
        self.list_view.setFont(self.font)
        self.list_view.setStyleSheet(
            """
            QListWidget {
                padding: 10px;
                background-color: #202020;
            }
            QListWidget::item:selected {
                background-color: #ffffff;
                color: #000000;
            }
            """
        )

        layout.addWidget(self.list_view)

        self._right_layout = QVBoxLayout()
        layout.addLayout(self._right_layout)

        self.registers = RightPanel()
        self.registers.setFixedWidth(250)
        self._right_layout.addWidget(self.registers)

        self.button_next = QPushButton("Next")
        self.button_next.clicked.connect(self.on_next_click)
        self._right_layout.addWidget(self.button_next)

        self.button_interrupt = QPushButton("Interrupt")
        self.button_interrupt.clicked.connect(self.on_exec_interrupt)
        self._right_layout.addWidget(self.button_interrupt)

        self.fill_list()
        self.update_labels()

    def on_next_click(self):
        cycles = 1000
        if self.cpu.cycles > cycles:
            interrupt = 0xCF if self.toggle_interrupt else 0xD7
            self.cpu.execute_interrupt(interrupt)
            self.toggle_interrupt = not self.toggle_interrupt
            self.cpu.cycles = 0
        else:
            self.cpu.execute_instruction()

        self.fill_list()
        self.update_labels()

        self.refresh.emit()
        self.setWindowTitle(f"Xpire - {self.cpu.cycles} cycles")

    def update_labels(self):
        af = self.cpu.registers.A << 8 | self.cpu.flags.get_flags()
        self.registers.set_values(af, self.cpu.registers.BC)

        self.registers.set_de(self.cpu.registers.DE)
        self.registers.set_hl(self.cpu.registers.HL)
        self.registers.set_pc(self.cpu.PC)
        self.registers.set_sp(self.cpu.SP)
        self.registers.set_flags(self.cpu.flags.get_flags())

    def on_exec_interrupt(self):
        if self.toggle_interrupt:
            self.cpu.execute_interrupt(0xCF)  # Interrupt on line 96
        else:
            self.cpu.execute_interrupt(0xD7)  # Interrupt on line 224

        self.toggle_interrupt = not self.toggle_interrupt
        self.fill_list()

    def fill_list(self):
        self.list_view.clear()
        addr = max(0x0000, self.cpu.PC - 0x1000)
        index = 0
        current_index = 0
        while True:

            instruction, size = get_decode_opcode(self.cpu.memory, addr)
            self.list_view.addItem(f"{addr:08X}\t\t{instruction}")

            if self.cpu.PC == addr:
                current_index = index

            index += 1
            addr += size

            if addr >= len(self.cpu.memory):
                break

            # if addr >= 0x2400:
            #     break

            if index >= 0x2000:
                break

        self.list_view.setCurrentRow(current_index)
        current_item = self.list_view.currentItem()
        self.list_view.scrollToItem(
            current_item, QListWidget.ScrollHint.PositionAtCenter
        )

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_F10:
            self.on_next_click()
        elif event.key() == Qt.Key.Key_F9:
            self.on_exec_interrupt()

        event.accept()


screen_frequency = 60
cpu_frequency = 2000000

frequency_ratio = cpu_frequency // screen_frequency
flipflop = FlipFlopD()


WHITE = (0xFF, 0xFF, 0xFF)
RED = (0xFF, 0x00, 0x00)
GREEN = (0x00, 0xFF, 0x00)
BLUE = (0x00, 0x00, 0xFF)
BLACK = (0x00, 0x00, 0x00)

BG_COLOR = (0x20, 0x22, 0x2E)


class GameScene:
    def __init__(self):
        self.is_finished = False

    def update(self) -> pygame.surface.Surface:
        """Update the game state."""

    def get_background_color(self) -> tuple[int, int, int]:
        return BLACK

    def get_ink_color(self) -> tuple[int, int, int]:
        return WHITE


class GameManager:

    def __init__(self, scene: GameScene):
        pygame.init()
        pygame.font.init()

        self.screen_size = (1024, 768)

        self.scene = scene
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(self.screen_size)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    pygame.display.toggle_fullscreen()

                elif event.key == pygame.K_d:
                    self.show_debugger()

    def show_debugger(self):
        app = QApplication(sys.argv)
        # debugger = Debugger(self.scene.cpu)
        # debugger.refresh.connect(self.refresh_screen)
        # debugger.show()
        debugger = DebuggerApp(self.scene.cpu)
        debugger.show()
        app.exec_()

    def refresh_screen(self):
        self.scene.clear_screen()
        for i in range(224):
            self.scene.draw_line(i)
        frame = self.scene.get_frame()
        self.render_frame(frame)

    def print_debug_info(self) -> None:
        my_font = pygame.font.Font("space_invaders.ttf", 20)
        offset = 500

        time_surface = my_font.render(
            f"FPS: {self.clock.get_fps():.0f}", False, (0xFF, 0xFF, 0xFF)
        )
        self.screen.blit(time_surface, (30, 0 + offset))

        time_surface = my_font.render(
            f"Time: {self.clock.get_time()}", False, (0xFF, 0xFF, 0xFF)
        )
        self.screen.blit(time_surface, (30, 50 + offset))

    def start(self):
        running = True
        while running:
            self.handle_events()

            self.clock.tick(60)
            self.screen.fill(BG_COLOR)

            frame: Surface = self.scene.update()
            self.render_frame(frame)
            running = not self.scene.is_finished

    def render_frame(self, frame: Surface) -> None:
        # surface = pygame.transform.scale(
        #     frame,
        #     (frame.get_width() * 2, frame.get_height() * 2),
        # )
        x_position = self.screen.get_width() // 2 - frame.get_width() // 2
        y_position = self.screen.get_height() // 2 - frame.get_height() // 2
        self.screen.blit(frame, (x_position, y_position))
        pygame.display.update()
