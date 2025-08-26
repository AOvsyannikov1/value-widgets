from PyQt6 import QtCore, QtGui
from PyQt6.QtGui import QPen, QColor, QFont
from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtWidgets import QLabel

from .utils import choose_contrast_color


class StateWidget(QLabel):

    def __init__(self, widget, x, y, w, h):
        super().__init__()
        self.setParent(widget)
        self.setGeometry(x, y, w, h) 
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFont(QFont("Bahnschrift, Arial", 12))
        self.__state: int | None = None
        self.__states = dict()

    def add_state(self, name: str, value: int, color):
        self.__states[value] = name, color
        if self.__state is None:
            self.set_state(value)

    def set_state(self, state: int):
        if self.__state != state:
            self.__state = state
            name, color = self.__states[state]
            self.setText(name)
            self.setStyleSheet(
                f"""
                background-color: {color};
                border-radius: 5px;
                color: {choose_contrast_color(QColor(color)).name()}
                """
            )

