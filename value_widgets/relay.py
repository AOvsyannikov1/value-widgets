from PyQt6.QtGui import QPainter, QColor, QFont, QPen
from PyQt6.QtCore import Qt, QLineF, QTimer, pyqtSlot as Slot
from .controllable_widget import ControllableWidget
from .utils import is_app_dark


class Relay(ControllableWidget):
    def __init__(self, widget, x, y, label="", w=100, h=70, dark=False, controllable=False, redraw_period=20):
        super().__init__(widget, x, y, w, h, active=controllable)
        self.__label = label
        self.__qp = QPainter()
        self.__label = label
        self.__value = False
        self.__dark = dark
        self.__redraw_required = True

        self.__tmr = QTimer(self)
        self.__tmr.timeout.connect(self.__redraw_process)
        self.__tmr.start(redraw_period)

    @Slot()
    def __redraw_process(self):
        if self.__dark != is_app_dark():
            self.set_dark(is_app_dark())
            self.__redraw_required = True
        if self.__redraw_required:
            self.update()
            self.__redraw_required = False

    def __draw_rect(self, value):
        if value == 1:
            if self.__dark:
                color = QColor(6, 214, 160, alpha=255)
            else:
                color = QColor(0, 176, 0, alpha=255)
        elif value == 0:
            if self.__dark:
                color = QColor(255, 209, 108)
            else:
                color = QColor(230, 230, 0)
        else:
            if self.__dark:
                color = QColor(229, 89, 52)
            else:
                color = QColor(255, 0, 0)
        self.__qp.setPen(color)
        if not self.__dark:
            self.__qp.setPen(QColor(0, 0, 0))

        if not self.underMouse():
            color.setAlpha(90)
        else:
            color.setAlpha(200)
        if self.mouse_pressed:
            color = color.lighter(120)
        self.__qp.setBrush(color)
        r = 5
        self.__qp.drawRoundedRect(0, 0, self.width(), self.height(), r, r)

    def __draw_value(self):
        if not self.isVisible():
            return
        self.__qp.begin(self)
        self.__qp.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.__draw_rect(self.__value)
        pen = QPen(QColor(0, 0, 0), 2)
        self.__qp.setPen(pen)
        self.__qp.setBrush(QColor(0, 0, 0, alpha=255))
        self.__qp.drawLine(QLineF(2, self.height() / 2, self.width() / 3, self.height() / 2))
        if self.__value < 2:
            self.__qp.drawLine(QLineF(self.width() / 3, self.height() / 2, 2 * self.width() / 3 + 2, self.height() / 2 - 20))
        self.__qp.drawLine(QLineF(2 * self.width() / 3, self.height() / 2, self.width() - 2, self.height() / 2))

        if self.__value == 1:
            self.__qp.drawLine(QLineF(2 * self.width() / 3, self.height() / 2, 2 * self.width() / 3, self.height() / 2 - 25))
        self.__qp.setFont(QFont("bahnschrift", 9))
        if self.__dark:
            self.__qp.setPen(QPen(QColor(255, 255, 255), 1))
        else:
            self.__qp.setPen(QPen(QColor(0, 0, 0), 1))
        self.__qp.drawText(0, self.height() - 25, self.width(), 20, Qt.AlignmentFlag.AlignCenter, self.__label)

        if self.controllable:

            if not self.get_control_state():
                color = QColor(255, 209, 108) if self.__dark else QColor(230, 230, 0)
            else:
                color = QColor(6, 214, 160) if self.__dark else QColor(0, 176, 0)
            self.__qp.setPen(color)
            self.__qp.setBrush(color)

            self.__qp.drawRoundedRect(5, 5, 10, 10, 2, 2)

        self.__qp.end()

    def paintEvent(self, a0):
        self.__draw_value()

    def set_value(self, value: bool):
        if self.__value != value:
            self.__value = value
            self.__redraw_required = True

    def set_dark(self, dark: bool):
        self.__dark = dark
