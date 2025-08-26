from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QPolygonF
from PyQt6.QtCore import Qt, QPointF, QTimer, QLineF, pyqtSlot as Slot

from .controllable_widget import ControllableWidget


class Valve(ControllableWidget):
    def __init__(self, widget, x, y, size_x=120, size_y=80, label="", dark=False, controllable=False, redraw_period=20):
        super().__init__(widget, x, y, size_x, size_y, active=controllable, on_release=False)

        self.__x = x
        self.__y = y
        self.__w = size_x
        self.__h = size_y
        self.__label = label
        self.__dark = dark
        self.__qp = QPainter()

        self.__state = 0

        self.__offset_x = self.__w / 6
        self.__offset_y = self.__h / 5
        self.__triangle_x = [0.0] * 5
        self.__triangle_y = [0.0] * 5

        self.__triangle_x[0] = self.__offset_x
        self.__triangle_x[1] = self.__offset_x
        self.__triangle_x[2] = size_x / 3 + self.__offset_x
        self.__triangle_x[3] = size_x * 2 / 3 + self.__offset_x
        self.__triangle_x[4] = size_x * 2 / 3 + self.__offset_x

        self.__triangle_y[0] = self.__offset_y
        self.__triangle_y[1] = size_y / 2 + self.__offset_y
        self.__triangle_y[2] = size_y / 4 + self.__offset_y
        self.__triangle_y[3] = self.__offset_y
        self.__triangle_y[4] = size_y / 2 + self.__offset_y

        self.__redraw_required = True

        self.__tmr = QTimer(self)
        self.__tmr.timeout.connect(self.__redraw_process)
        self.__tmr.start(redraw_period)

    @Slot()
    def __redraw_process(self):
        if self.__redraw_required:
            self.update()
            self.__redraw_required = False

    def set_dark(self, dark: bool):
        self.__dark = dark

    def setGeometry(self, x, y, w, h):
        self.__x = x
        self.__y = y
        self.__w = w
        self.__h = h

        self.__offset_x = self.__w / 6
        self.__offset_y = self.__h / 5
        self.__triangle_x = [0] * 5
        self.__triangle_y = [0] * 5

        self.__triangle_x[0] = self.__offset_x
        self.__triangle_x[1] = self.__offset_x
        self.__triangle_x[2] = w / 3 + self.__offset_x
        self.__triangle_x[3] = w * 2 / 3 + self.__offset_x
        self.__triangle_x[4] = w * 2 / 3 + self.__offset_x

        self.__triangle_y[0] = self.__offset_y
        self.__triangle_y[1] = h / 2 + self.__offset_y
        self.__triangle_y[2] = h / 4 + self.__offset_y
        self.__triangle_y[3] = self.__offset_y
        self.__triangle_y[4] = h / 2 + self.__offset_y

        super().setGeometry(x, y, w, h)

    def __draw_arrow(self):
        if self.__dark:
            self.__qp.setPen(QPen(QColor(128, 128, 128), 1))
        else:
            self.__qp.setPen(QPen(QColor(0, 0, 0), 1))

        self.__qp.drawLine(QLineF(self.__triangle_x[0] + self.__w / 6, self.__offset_y / 2 + 5,
                         self.__triangle_x[3] - self.__w / 6, self.__offset_y / 2 + 5))

        self.__qp.drawLine(QLineF(self.__triangle_x[3] - self.__w / 6, self.__offset_y / 2 + 5,
                         self.__triangle_x[3] - self.__w / 4, self.__offset_y / 2))
        self.__qp.drawLine(QLineF(self.__triangle_x[3] - self.__w / 6, self.__offset_y / 2 + 5,
                         self.__triangle_x[3] - self.__w / 4, self.__offset_y / 2 + 10))

    def __draw_icon(self, state):
        self.__qp.setPen(QColor(0, 0, 0, alpha=0))
        self.__qp.setBrush(QColor(200, 200, 200, alpha=0))
        self.__qp.drawRoundedRect(0, 0, self.__w, self.__h, 10, 10)

        self.__qp.setPen(QPen(QColor(0, 0, 0), 1))

        if state == 1:
            if self.__dark:
                color = QColor(255, 209, 108)
            else:
                color = QColor(230, 230, 0)
        elif state == 2:
            self.__draw_arrow()
            if self.__dark:
                color = QColor(6, 214, 160)
            else:
                color = QColor(0, 176, 0)
        elif state == 3:
            if self.__dark:
                color = QColor(229, 89, 52)
            else:
                color = QColor(255, 0, 0)
        else:
            color = QColor(255, 255, 255, alpha=0)

        self.__qp.setPen(color)
        if not self.__dark:
            self.__qp.setPen(QColor(0, 0, 0))

        if not self.underMouse():
            color.setAlpha(128)
        if self.mouse_pressed:
            color = color.lighter(120)
        self.__qp.setBrush(color)

        if state == 0:
            if self.__dark:
                self.__qp.setPen(QColor(128, 128, 128))
            self.__qp.setBrush(QColor(255, 255, 255, alpha=0))

        poly = QPolygonF()
        for i in range(3):
            poly.append(QPointF(self.__triangle_x[i], self.__triangle_y[i]))
        self.__qp.drawPolygon(poly)
        poly = QPolygonF()
        for i in range(2, 5):
            poly.append(QPointF(self.__triangle_x[i], self.__triangle_y[i]))
        self.__qp.drawPolygon(poly)
        self.__qp.drawLine(QLineF(2, self.__triangle_y[2], self.__offset_x, self.__triangle_y[2]))
        self.__qp.drawLine(QLineF(self.__triangle_x[3], self.__triangle_y[2], self.__triangle_x[3] + self.__offset_x - 2, self.__triangle_y[2]))
        self.__qp.setFont(QFont("bahnschrift", 9))

        if self.__dark:
            self.__qp.setPen(QPen(QColor(255, 255, 255), 1))
        else:
            self.__qp.setPen(QPen(QColor(0, 0, 0), 1))
        self.__qp.drawText(0, self.__h - 25, self.__w, 35, Qt.AlignmentFlag.AlignCenter, self.__label)

        if not self.controllable:
            return

        if not self.get_control_state():
            color = QColor(255, 209, 108) if self.__dark else QColor(230, 230, 0)
        else:
            color = QColor(6, 214, 160) if self.__dark else QColor(0, 176, 0)
        self.__qp.setPen(color)
        self.__qp.setBrush(color)
        self.__qp.drawRoundedRect(2, 2, 10, 10, 2, 2)

    def __draw_state(self):
        if not self.isVisible():
            return
        self.__qp.begin(self)
        self.__qp.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.__draw_icon(self.__state)
        self.__qp.end()

    def paintEvent(self, a0):
        self.__draw_state()

    def set_state(self, state):
        if 0 <= state <= 3 and self.__state != state:
            self.__state = state
            self.__redraw_required = True
