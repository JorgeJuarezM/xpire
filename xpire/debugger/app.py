from PyQt5.QtCore import pyqtSignal, Qt, QSize
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
    QStyle,
    QToolBar,
    QAction,
    QMainWindow,
    QMessageBox,
    QTreeWidget,
    QTreeWidgetItem,
    QTreeView,
    QSizePolicy,
    QFrame,
)
from PyQt5.QtGui import QColor, QFont, QFontDatabase, QKeyEvent, QIcon
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtGui import QPainter, QPixmap
from xpire.cpus.cpu import CPU
from xpire import resolve_path
from xpire.dissasembler import get_decode_opcode


def svg_to_pixmap(svg_filename: str, width: int, height: int, color: QColor) -> QPixmap:
    renderer = QSvgRenderer(svg_filename)
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)  # this is the destination, and only its alpha is used!
    painter.setCompositionMode(painter.CompositionMode.CompositionMode_SourceIn)
    painter.fillRect(pixmap.rect(), color)
    painter.end()
    return pixmap


class OptionsPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.initialize_ui()
        self.setFixedHeight(150)

    def initialize_ui(self):
        self._layout = QHBoxLayout()
        self.setLayout(self._layout)


class LeftPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.initialize_ui()

    def initialize_ui(self):
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)

        self.list_view = QTreeWidget()
        self._layout.addWidget(self.list_view)
        self.list_view.setStyleSheet(
            """
            QTreeWidget {
                padding: 10px;
                background-color: #202020;
                color: #ffffff;
            }
            QTreeWidget::item:selected {
                background-color: #5dd62c;
                color: #000000;
            }
            """
        )

        self.options_panel = OptionsPanel()
        self._layout.addWidget(self.options_panel)

        # self.list_view.setColumnCount(4)

        QFontDatabase.addApplicationFont(resolve_path("fonts/RobotoMono-Regular.ttf"))
        font = QFont("Roboto Mono", 14, QFont.Normal)
        self.list_view.setFont(font)

        # self.list_view.setColumnWidth(0, 100)
        # self.list_view.setColumnWidth(1, 120)
        # self.list_view.setColumnWidth(2, 150)
        # self.list_view.setColumnWidth(3, 100)

        self.list_view.setHeaderHidden(True)

        # self.list_view.setEditTriggers(QTreeWidget.NoEditTriggers)
        # self.list_view.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        self.list_view.setIndentation(0)

        self.list_view.setRootIsDecorated(False)
        self.list_view.setUniformRowHeights(True)

        current_item = None
        # Add Tree Widget Items
        # for i in range(500):
        #     item = QTreeWidgetItem(self.list_view)
        #     item.setText(0, f"{i:04X}")
        #     item.setText(1, "21 02 20")
        #     item.setText(2, "LD   HL, $2002")

        #     item.setText(
        #         3,
        #         "{} {} {}".format(
        #             chr(0x21).strip() or ".",
        #             chr(0x02).strip() or ".",
        #             chr(0x20).strip() or ".",
        #         ),
        #     )
        #     if i == 120:
        #         current_item = item

        # # current_item.setSelected(True)
        # self.list_view.setCurrentIndex(self.list_view.model().index(120, 0))
        # self.list_view.scrollToItem(
        #     self.list_view.currentItem(), QTreeWidget.ScrollHint.PositionAtCenter
        # )
        # QTreeWidget.topLevelItem(self.list_view, 1).setFlags(Qt.ItemFlag.ItemIsEnabled)

        # item = QTreeWidgetItem(self.list_view)
        # item.setText(0, "21 02 20")
        # item = QTreeWidgetItem(self.list_view)
        # item.setText(0, "LD HL, $2002")

    # def dissasemble_memory(self, memory: bytearray, pc: int):
    #     self.list_view.clear()
    #     address = max(0, pc - 0x100)
    #     limit = min(0xFFFF, pc + 0x100)

    #     _index = 0
    #     for i in range(limit):
    #         if address == pc:
    #             _index = i
    #             print(f"0x{address:04X}: {pc:04X}, {_index}")

    #         opcode_decoded, size = get_decode_opcode(memory, address)
    #         opcode = memory[address]
    #         instruction_set = [opcode]
    #         if size == 2:
    #             instruction_set.append(memory[address + 1])
    #         elif size == 3:
    #             instruction_set.append(memory[address + 1])
    #             instruction_set.append(memory[address + 2])
    #         instruction_set_hex = " ".join([f"{arg:02X}" for arg in instruction_set])
    #         instruction_set_chr = " ".join(
    #             [
    #                 chr(arg) if (arg > 32 and arg < 127) else "."
    #                 for arg in instruction_set
    #             ]
    #         )

    #         item = QTreeWidgetItem(self.list_view)
    #         item.setText(0, f"{address:04X}")
    #         item.setText(1, instruction_set_hex)
    #         item.setText(2, opcode_decoded)
    #         item.setText(3, instruction_set_chr)
    #         address += size

    #     print(f"Current index: {_index}")
    #     self.list_view.setCurrentIndex(self.list_view.model().index(_index, 0))
    #     self.list_view.scrollToItem(
    #         self.list_view.currentItem(), QTreeWidget.ScrollHint.PositionAtCenter
    #     )


class RightPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.initialize_ui()
        self.setFixedWidth(250)

    def initialize_ui(self):
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)


class DebuggerPanel(QWidget):
    def __init__(self, cpu: CPU):
        super().__init__()

        self.cpu = cpu
        self.initialize_ui()

    def initialize_ui(self):
        self._layout = QHBoxLayout()
        self.setLayout(self._layout)

        self.left_panel = LeftPanel()
        self._layout.addWidget(self.left_panel)

        self.right_panel = RightPanel()
        self._layout.addWidget(self.right_panel)

        self.left_panel.layout().setContentsMargins(0, 0, 0, 0)
        self.right_panel.layout().setContentsMargins(0, 0, 0, 0)

        self.left_panel.dissasemble_memory(self.cpu.memory, self.cpu.PC)


class DebuggerApp2(QMainWindow):
    def __init__(self, cpu: CPU):
        super().__init__()
        self.cpu = cpu
        self.resize(800, 600)
        self.initialize_ui()

    def initialize_ui(self):

        self.debugger = DebuggerPanel(self.cpu)
        self.setCentralWidget(self.debugger)
        self.debugger.setContentsMargins(0, 0, 0, 0)
        self.debugger.layout().setContentsMargins(0, 0, 0, 0)

        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        self.toolbar.setIconSize(QSize(24, 24))
        self.toolbar.setStyleSheet(
            """
            QToolBar {
                background: #0f0f0f;
                color: white;
                border: none;
            }
            QToolBar::separator {
                width: 0px;
            }
            QToolButton {
                padding: 10px;
            }
            QToolButton:hover {
                background-color: #202020;
            }
            """
        )

        # icon = QIcon(resolve_path("icons/play-pause.png"))
        pixmap = svg_to_pixmap(
            resolve_path("icons/play-pause-2.svg"), 24, 24, QColor("#337418")
        )
        icon = QIcon(pixmap)
        action = QAction(icon=icon, text="Run", parent=self)
        action.triggered.connect(self.play_action)
        self.toolbar.addAction(action)

        pixmap2 = svg_to_pixmap(
            resolve_path("icons/play-pause.svg"), 24, 24, QColor("#337418")
        )
        icon2 = QIcon(pixmap2)
        action2 = QAction(icon=icon2, text="Stop", parent=self)
        action2.triggered.connect(self.play_action)
        self.toolbar.addAction(action2)

        self.setContentsMargins(0, 0, 0, 0)
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.setStyleSheet(
            """
            QMainWindow {
                margin: 0px;
                padding: 0px;
                background-color: #202020;
            }
            """
        )

    def play_action(self):
        self.cpu.execute_instruction()
        # QMessageBox.information(self, "Hello", f"CPU cycles: {self.cpu.cycles}")
        self.debugger.left_panel.dissasemble_memory(self.cpu.memory, self.cpu.PC)
        self.setWindowTitle(f"Xpire - {self.cpu.PC:04X}")


class XTreeWidget(QTreeWidget):
    def __init__(self):
        super().__init__()

        self._font = QFont("Roboto Mono", 14, QFont.Weight.Normal)
        self.setFont(self._font)

        self.setColumnCount(4)
        self.setColumnWidth(0, 100)
        self.setColumnWidth(1, 120)
        self.setColumnWidth(2, 150)
        self.setColumnWidth(3, 100)
        self.setHeaderHidden(True)


class XLabel(QFrame):
    def __init__(self, label_text: str, default_value: str):
        super().__init__()
        self._font = QFont("Roboto Mono", 14, QFont.Weight.Normal)

        self._layout = QHBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._layout)

        self.label = QLabel(label_text)
        self.label.setFont(self._font)
        self._layout.addWidget(self.label)

        self.text = QLineEdit(default_value)
        self.text.setFont(self._font)
        self.text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text.setTextMargins(3, 3, 3, 3)
        self.text.setReadOnly(True)
        self._layout.addWidget(self.text)


class DebuggerApp(QMainWindow):
    def __init__(self, cpu: CPU):
        super().__init__()

        QFontDatabase.addApplicationFont(resolve_path("fonts/RobotoMono-Regular.ttf"))

        self.cpu = cpu
        self.toggle_interrupt = False

        self.resize(800, 600)
        self.initialize_ui()
        self.dissasemble_memory()
        self.set_register_values()

    def _get_toolbar(self):
        toolbar = QToolBar()
        action = QAction("Run", self)
        action.triggered.connect(self.play)

        toolbar.addAction(action)
        return toolbar

    def initialize_ui(self):
        self.addToolBar(self._get_toolbar())

        self._main = QWidget()
        self.setCentralWidget(self._main)

        self._layout = QVBoxLayout(self._main)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._top_layout = QHBoxLayout()
        self._top_layout.setContentsMargins(0, 0, 0, 0)
        self._top_layout.setSpacing(0)
        self._layout.addLayout(self._top_layout)

        self._left_layout = QVBoxLayout()
        self._left_layout.setContentsMargins(0, 0, 0, 0)
        self._left_layout.setSpacing(0)
        self._top_layout.addLayout(self._left_layout)

        self._right_layout = QVBoxLayout()
        self._right_layout.setContentsMargins(0, 0, 0, 0)
        self._right_layout.setSpacing(0)
        # --------
        self._right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        # --------
        self._top_layout.addLayout(self._right_layout)

        self._list_view = XTreeWidget()
        self._left_layout.addWidget(self._list_view)

        self._right_row_1_layout = QHBoxLayout()
        self._right_row_1_layout.setContentsMargins(10, 10, 10, 0)
        self._right_row_1_layout.setSpacing(10)
        self._right_layout.addLayout(self._right_row_1_layout)

        self._af_label = XLabel("AF", "0000")
        self._af_label.setFixedWidth(100)
        self._right_row_1_layout.addWidget(self._af_label)

        self._bc_label = XLabel("BC", "0000")
        self._bc_label.setFixedWidth(100)
        self._right_row_1_layout.addWidget(self._bc_label)

        self._right_row_2_layout = QHBoxLayout()
        self._right_row_2_layout.setContentsMargins(10, 10, 10, 0)
        self._right_row_2_layout.setSpacing(10)
        self._right_layout.addLayout(self._right_row_2_layout)

        self._de_label = XLabel("DE", "0000")
        self._de_label.setFixedWidth(100)
        self._right_row_2_layout.addWidget(self._de_label)

        self._hl_label = XLabel("HL", "0000")
        self._hl_label.setFixedWidth(100)
        self._right_row_2_layout.addWidget(self._hl_label)

        self._right_row_3_layout = QHBoxLayout()
        self._right_row_3_layout.setContentsMargins(10, 10, 10, 0)
        self._right_row_3_layout.setSpacing(10)
        self._right_layout.addLayout(self._right_row_3_layout)

        self._pc_label = XLabel("PC", "0000")
        self._pc_label.setFixedWidth(100)
        self._right_row_3_layout.addWidget(self._pc_label)

        self._sp_label = XLabel("SP", "0000")
        self._sp_label.setFixedWidth(100)
        self._right_row_3_layout.addWidget(self._sp_label)

    def set_register_values(self):
        flags = self.cpu.flags.get_flags()
        af = self.cpu.registers.A << 8 | flags

        self._af_label.text.setText(f"{af:04X}")
        self._bc_label.text.setText(f"{self.cpu.registers.BC:04X}")
        self._de_label.text.setText(f"{self.cpu.registers.DE:04X}")
        self._hl_label.text.setText(f"{self.cpu.registers.HL:04X}")
        self._pc_label.text.setText(f"{self.cpu.PC:04X}")
        self._sp_label.text.setText(f"{self.cpu.SP:04X}")

    def dissasemble_memory(self):
        self._list_view.clear()

        address = max(0, self.cpu.PC - 0x100)
        _index = 0
        for i in range(0x200):
            if address == self.cpu.PC:
                _index = i

            if address > 0xFFFF:
                break

            opcode_decoded, size = get_decode_opcode(self.cpu.memory, address)
            opcode = self.cpu.memory[address]
            instruction_set = [opcode]
            if size == 2:
                instruction_set.append(self.cpu.memory[address + 1])
            elif size == 3:
                instruction_set.append(self.cpu.memory[address + 1])
                instruction_set.append(self.cpu.memory[address + 2])
            instruction_set_hex = " ".join([f"{arg:02X}" for arg in instruction_set])
            instruction_set_chr = " ".join(
                [
                    chr(arg) if (arg > 32 and arg < 127) else "."
                    for arg in instruction_set
                ]
            )

            item = QTreeWidgetItem(self._list_view)
            item.setText(0, f"{address:04X}")
            item.setText(1, instruction_set_hex)
            item.setText(2, opcode_decoded)
            item.setText(3, instruction_set_chr)
            address += size

        print(f"Current index: {_index}")
        self._list_view.setCurrentIndex(self._list_view.model().index(_index, 0))
        self._list_view.scrollToItem(
            self._list_view.currentItem(), QTreeWidget.ScrollHint.PositionAtCenter
        )

    def play(self):
        if self.cpu.cycles > 1000:
            interrupt = 0xCF if self.toggle_interrupt else 0xD7
            self.cpu.execute_interrupt(interrupt)
            self.toggle_interrupt = not self.toggle_interrupt
            self.cpu.cycles = 0
        else:
            self.cpu.execute_instruction()
        self.dissasemble_memory()
        self.set_register_values()
