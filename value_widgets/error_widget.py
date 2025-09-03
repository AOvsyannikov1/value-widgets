from PyQt6.QtGui import QFont
from PyQt6.QtCore import QTimer, pyqtSlot as Slot
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSizePolicy
from .utils import is_app_dark


class ErrorWidget(QWidget):

    def __init__(self, widget, x, y, error_name, dark=False):
        super().__init__()
        self.setParent(widget)
        super().setGeometry(x, y, 100, 20)
        self.__error = True
        self.__dark = False

        self.__indicator = QLabel()
        self.__indicator.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.__indicator.setMinimumHeight(15)
        self.__indicator.setMinimumWidth(15)
        self.__label = QLabel()
        self.__label.setText(error_name)
        self.__label.setFont(QFont("Bahnschrift, Arial", 12))
        self.__label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)

        self.__layout = QHBoxLayout(self)
        self.__layout.addWidget(self.__indicator)
        self.__layout.addWidget(self.__label)

        self.__tmr = QTimer(self)
        self.__tmr.timeout.connect(self.__check_theme)
        self.__tmr.start(100)

        self.adjustSize()

        self.set_error(False)

    def setGeometry(self, x, y):
        super().setGeometry(x, y, 100, 20)
        self.adjustSize()

    @Slot()
    def __check_theme(self):
        if self.__dark != is_app_dark():
            self.set_dark(is_app_dark())

    def set_error(self, error: bool):
        if self.__error != error:
            self.__indicator.setStyleSheet(
                f"""
                QLabel {{
                    border-radius: 7px;
                    background-color: {'red' if error else 'rgb(128, 128, 128)'};
                }}
                """
            )
            if self.__dark:
                self.__label.setStyleSheet(f"color: {'white' if error else 'rgb(128, 128, 128)'};")
            else:
                self.__label.setStyleSheet(f"color: {'black' if error else 'rgb(128, 128, 128)'};")
        self.__error = error

    def set_dark(self, dark: bool):
        if self.__dark != dark:
            if dark:
                self.__label.setStyleSheet(f"color: {'white' if self.__error else 'rgb(128, 128, 128)'};")
            else:
                self.__label.setStyleSheet(f"color: {'black' if self.__error else 'rgb(128, 128, 128)'};")
        self.__dark = dark
