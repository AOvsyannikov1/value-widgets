from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt, pyqtSlot as Slot, QTimer
from PyQt6.QtWidgets import QPushButton, QFrame, QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy, QLabel

from .timer import Timer
from .utils import get_image_path, is_app_dark


class TimerWidget(QFrame):
    def __init__(self, widget, x, y, begin_value=None, end_value=None, normal_min=0, normal_max=100,
                 name=None, units=None, dark=False, redraw_period=5):
        super().__init__()
        self.setParent(widget)
        super().setGeometry(x, y, 250, 90)
        self.__begin_value = begin_value
        self.__end_value = end_value
        self.__normal_min = normal_min
        self.__normal_max = normal_max
        self.__name = name
        self.__units = units
        self.__paused = False
        self.__tmp_counter = 0
        self.__controlled_value = 0.0
        self.__value_ok = True

        self.__counter = 0.0
        self.__fsm = 0
        self.__tmr = Timer(100)

        self.__startButton = QPushButton(self)
        self.__startButton.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.__startButton.setIcon(QIcon(get_image_path("play.png")))
        self.__startButton.setWhatsThis("Старт/пауза")
        if self.__begin_value is None:
            self.__startButton.clicked.connect(self.__pause_timer)
            self.__paused = True
        else:
            self.__startButton.clicked.connect(self.__start_timer)
        
        buttonSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.__pauseButton = QPushButton(self)
        self.__pauseButton.setIcon(QIcon(get_image_path("restart.png")))
        self.__pauseButton.clicked.connect(self.__clear_timer)
        self.__pauseButton.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.__pauseButton.setWhatsThis("Сброс таймера")

        self.__layout = QVBoxLayout(self)
        self.__name_label = QLabel()
        self.__name_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.__name_label.setFont(QFont("Consolas, Courier New", 11))
        
        buf = self.__name
        if self.__begin_value is not None:
            buf += f" c {self.__begin_value:.2f} по {self.__end_value:.2f}"
        if self.__units is not None:
            buf += f" {self.__units}"
        self.__name_label.setText(buf)

        self.__time_label = QLabel()
        self.__time_label.setText("0.00 с")
        self.__time_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.__time_label.setFont(QFont("Consolas, Courier New", 14))
        self.__layout.addWidget(self.__name_label)
        self.__layout.addWidget(self.__time_label)
        spacerItem = QSpacerItem(10, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        
        self.__layout.addSpacerItem(spacerItem)
        self.__button_layout = QHBoxLayout()
        self.__button_layout.addSpacerItem(buttonSpacer)
        self.__button_layout.addWidget(self.__startButton)
        self.__button_layout.addWidget(self.__pauseButton)
        self.__layout.addLayout(self.__button_layout)

        self.__dark = not dark
        self.set_dark(dark)
        self.__time_label.setStyleSheet(f"color: {'rgb(6, 214, 160)' if self.__dark else 'rgb(0, 100, 50)'}")

        self.__qtmr = QTimer(self)
        self.__qtmr.timeout.connect(self.__redraw_process)
        self.__qtmr.start(redraw_period)
        self.__redraw_required = True
        self.show()

    @Slot()
    def __redraw_process(self):
        if self.__dark != is_app_dark():
            self.set_dark(is_app_dark())
            self.__redraw_required = True
        if self.__redraw_required:
            self.update()
            self.__redraw_required = not self.__paused

    def paintEvent(self, a0):
        self.__redraw()

    @Slot()
    def __start_timer(self):
        self.__fsm = 1
        self.__tmr.restart()
        self.__counter = 0
        self.__tmp_counter = 0
        self.__paused = False
        self.__redraw_required = True

    @Slot()
    def __pause_timer(self):
        if self.__paused:
            self.__fsm = 1
            self.__tmr.restart()
            self.__paused = False
            self.__startButton.setIcon(QIcon(get_image_path("pause.png")))
        else:
            self.__paused = True
            self.__fsm = 0
            self.__tmp_counter = self.__counter
            self.__startButton.setIcon(QIcon(get_image_path("play.png")))
        self.__redraw_required = True

    @Slot()
    def __clear_timer(self):
        self.__startButton.setIcon(QIcon(get_image_path("play.png")))
        self.__paused = True
        self.__fsm = 0
        self.__counter = 0
        self.__tmr.restart()
        self.__tmp_counter = 0
        self.__redraw_required = True

    def __draw_rect(self):
        if not self.isVisible():
            return
        if self.__normal_min <= self.__counter <= self.__normal_max:
            if not self.__value_ok:
                self.__time_label.setStyleSheet(f"color: {'rgb(6, 214, 160)' if self.__dark else 'rgb(0, 100, 50)'}")
                self.__value_ok = True
        else:
            if self.__value_ok:
                self.__time_label.setStyleSheet(f"color: {'rgb(229, 89, 52)' if self.__dark else 'rgb(230, 0, 0)'}")
                self.__value_ok = False
        self.__time_label.setText(f"{self.__counter:05.2f} с")

    def set_controlled_value(self, val: float):
        self.__controlled_value = val

    def set_dark(self, dark: bool):
        if dark != self.__dark:
            self.setStyleSheet(f"""
                                QFrame {{
                                    background-color: {'rgb(45, 52, 65)' if dark else 'rgb(255, 255, 255)'}; 
                                    border-radius: 10px;
                                }}
                                """)
            self.__name_label.setStyleSheet(f"color: {'rgb(210, 210, 210)' if dark else 'rgb(0, 0, 100)'}")
            self.__time_label.setStyleSheet(f"color: {'rgb(6, 214, 160)' if dark else 'rgb(0, 100, 50)'}")

            button_style = f"""
                            QPushButton {{
                                background-color : {'rgba(255, 255, 255, 0.7)' if not dark else 'rgba(180, 180, 180, 0.8)'}; 
                                width: 25px;
                                height: 25px;
                                border-radius: 5px;
                                border: 1px solid black;
                            }}
                            QPushButton::hover
                            {{
                                background-color : lightblue;
                                border-style : outset;
                                border-color: rgba(0, 0, 0, 0);
                            }}
                            QPushButton::pressed
                            {{
                                background-color : lightblue;
                                border-style : inset;
                                border-width : 2px;
                                border-color : #777777;
                            }}
                            """
            self.__startButton.setStyleSheet(button_style)
            self.__pauseButton.setStyleSheet(button_style)
        self.__dark = dark

    def __redraw(self):
        match self.__fsm:
            case 0:
                pass
            case 1:
                if self.__begin_value is None:
                    self.__fsm = 2
                    self.__tmr.restart()
                elif ((self.__begin_value > self.__end_value and self.__controlled_value < self.__begin_value) or
                        (self.__begin_value < self.__end_value and self.__controlled_value > self.__begin_value)):
                    self.__fsm = 2
                    self.__tmr.restart()
            case 2:
                if self.__begin_value is None:
                    self.__counter = self.__tmr.get() / 1000 + self.__tmp_counter
                else:
                    if ((self.__begin_value < self.__end_value and self.__controlled_value >= self.__end_value) or
                            (self.__begin_value > self.__end_value and self.__controlled_value <= self.__end_value)):
                        self.__fsm = 0
                    else:
                        self.__counter = self.__tmr.get() / 1000 + self.__tmp_counter

        self.__draw_rect()

    def setGeometry(self, x, y, w, h):
        super().setGeometry(x, y, w, h)
