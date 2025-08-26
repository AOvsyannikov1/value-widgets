from PyQt6.QtGui import QPainter, QColor, QFont, QPen
from PyQt6.QtCore import Qt, QRectF, QLineF, QTimer, pyqtSlot as Slot
from PyQt6.QtWidgets import QWidget
import numpy as np
from math import sin, cos, radians

import time


class PointerDevice(QWidget):
    def __init__(self, widget, x, y, d, min_value=0.0, max_value=1.0, label="", units="", dark=False, redraw_period=15):
        super().__init__()
        self.setParent(widget)
        self.__offset = 40

        self.__x = x
        self.__y = y
        self.__d = d
        self.__R = d / 2
        super().setGeometry(x - self.__offset, y - self.__offset, d + self.__offset * 2, d + self.__offset * 2)
        self.__value = 0.0
        self.__max_val = max_value
        self.__min_val = min_value
        self.__real_width = (max_value - min_value)
        self.__start_angle = 180 + 45
        self.__stop_angle = -45
        self.__start_radians = radians(self.__start_angle - 90)
        self.__angle = self.__stop_angle - self.__start_angle
        self.__needle_width = self.__d / 110
        self.__display_nums = True
        self.__frame = False
        self.__draw_arc = False
        self.__major_step = (max_value - min_value) / 10
        self.__minor_step = (max_value - min_value) / 50
        self.__second_needle = False
        self.__second_value = 0.0
        self.__qp = QPainter()

        self.__dark = dark

        self.__label = label
        self.__unit = units
        self.__n_digits = 3

        self.__redraw_required = True

        self.__tmr = QTimer(self)
        self.__tmr.timeout.connect(self.__redraw_process)
        self.__tmr.start(redraw_period)

        self.show()

    def setGeometry(self, x, y, d):
        super().setGeometry(x - self.__offset, y - self.__offset, d + self.__offset * 2, d + self.__offset * 2)
        self.__x = x
        self.__y = y
        self.__d = d
        self.__R = d / 2

    @Slot()
    def __redraw_process(self):
        if self.__redraw_required:
            self.update()
            self.__redraw_required = False

    def set_major_step(self, step: float):
        self.__major_step = step

    def set_minor_step(self, step: float):
        self.__minor_step = step

    def draw_frame(self, draw: bool):
        self.__frame = draw

    def draw_arc(self, draw: bool):
        self.__draw_arc = draw

    def display_value(self, display: bool):
        self.__display_nums = display

    def __value_to_angle(self, val: float):
        return radians((val - self.__min_val) / self.__real_width * self.__angle + self.__start_angle + 135)

    def __angle_to_coords_with_offset(self, angle: float, offset: int):
        coords = [0.0, 0.0]
        tmp = -(self.__R - offset)
        coords[0] = tmp * sin(angle + self.__start_radians) + self.__R + self.__offset
        coords[1] = tmp * cos(angle + self.__start_radians) + self.__R + self.__offset
        return coords

    def __draw_frame(self):
        if self.__dark:
            self.__qp.setBrush(QColor(45, 52, 65))
        else:
            self.__qp.setBrush(QColor(255, 255, 255))
        pen = QPen(QColor(0, 0, 0, 0))
        self.__qp.setPen(pen)
        self.__qp.drawEllipse(QRectF(self.__x - 1.3 * self.__d / 2, self.__y - 1.3 * self.__d / 2, 1.3*self.__d, 1.3*self.__d))

    def __draw_scale(self):
        self.__qp.setBrush(QColor(0, 0, 0))
        pen = QPen(QColor(0, 0, 0), 1.5)
        self.__qp.setPen(pen)
        self.__qp.setFont(QFont('bahnschrift light', self.__d // 20))

        # основные деления
        X = np.arange(self.__min_val, self.__max_val + self.__major_step, self.__major_step)
        lines = list()

        offset_minor = self.__d / 30
        offset_major = self.__d / 14
        offset_text = -self.__d / 15

        for tick in X:
            for minor_tick_num in range(1, round(self.__major_step / self.__minor_step)):
                val = tick + minor_tick_num * self.__minor_step
                if val > self.__max_val or val < self.__min_val:
                    break
                angle = self.__value_to_angle(val)
                X1 = self.__angle_to_coords_with_offset(angle, 0)
                X2 = self.__angle_to_coords_with_offset(angle, offset_minor)
                lines.append(QLineF(X1[0], X1[1], X2[0], X2[1]))

            angle = self.__value_to_angle(tick)
            Xtxt = self.__angle_to_coords_with_offset(angle, offset_text)
            X1 = self.__angle_to_coords_with_offset(angle, 0)
            X2 = self.__angle_to_coords_with_offset(angle, offset_major)
            rounded_value = round(tick, 2)
            disp = rounded_value if abs(rounded_value) < 10 else round(rounded_value)
            if self.__display_nums:
                if self.__dark:
                    pen = QPen(QColor(255, 255, 255), 2)
                    self.__qp.setPen(pen)
                self.__qp.drawText(QRectF(Xtxt[0] - 20, Xtxt[1] - 10, 40, 20), Qt.AlignmentFlag.AlignHCenter, f"{disp}")
            lines.append(QLineF(X1[0], X1[1], X2[0], X2[1]))

            if self.__draw_arc:
                pen = QPen(QColor(0, 0, 0), 2)
                self.__qp.setPen(pen)
                self.__qp.drawArc(QRectF(self.__offset + self.__R - self.__d / 2, self.__offset, self.__d, self.__d),
                                self.__start_angle * 16, (self.__stop_angle - self.__start_angle) * 16)

        if self.__dark:
            pen = QPen(QColor(128, 128, 128), 2)
        else:
            pen = QPen(QColor(0, 0, 0), 2)
        self.__qp.drawLines(lines)

    def __display_value(self, val):
        pen = QPen(QColor(0, 0, 0), 1)
        self.__qp.setPen(pen)
        val = round(val, 3)
        if val > self.__max_val or val < self.__min_val:
            tmp = "Ошибка"
        else:
            if (self.__max_val - self.__min_val) < 10:
                tmp = "{:.3f}".format(val)
            elif (self.__max_val - self.__min_val) < 100:
                tmp = "{:.2f}".format(val)
            else:
                tmp = "{:.1f}".format(val)
            if val > 0:
                tmp = ' ' + tmp
        self.__qp.setFont(QFont('bahnschrift', self.__d // 12))
        self.__qp.drawText(int(self.__offset + self.__R - 50), int(self.__offset + self.__R + self.__d // 3.5), 100, 20, Qt.AlignmentFlag.AlignCenter, tmp)

    def __draw_needle(self, val, val2=0.0):
        if self.__second_needle:

            if self.__dark:
                color = QColor(86, 114, 179)
            else:
                color = QColor(0, 0, 255)
            pen = QPen(color, self.__needle_width)
            self.__qp.setPen(pen)
            tmp_val = min(self.__max_val, max(val2, self.__min_val))
            tmp = self.__value_to_angle(tmp_val)
            X1 = self.__angle_to_coords_with_offset(tmp, self.__d / 27)
            self.__qp.drawLine(QLineF(self.__offset + self.__R, self.__offset + self.__R, X1[0], X1[1]))

        color = QColor(255, 0, 0) if not self.__dark else QColor(233, 96, 79)
        pen = QPen(color, self.__needle_width)
        self.__qp.setPen(pen)
        tmp_val = min(self.__max_val, max(val, self.__min_val))
        tmp = self.__value_to_angle(tmp_val)
        X1 = self.__angle_to_coords_with_offset(tmp, self.__d / 27)

        self.__qp.drawLine(QLineF(self.__offset + self.__R, self.__offset + self.__R, X1[0], X1[1]))
        pen = QPen(QColor(0, 0, 0), 1)
        self.__qp.setPen(pen)
        self.__qp.drawEllipse(QRectF(self.__offset + self.__R - self.__d / 80, self.__offset + self.__R - self.__d / 80, self.__d / 40, self.__d / 40))
        if self.__display_nums:
            self.__display_value(val)

    def set_value(self, val: float):
        if val != self.__value:
            self.__value = val
            self.__redraw_required = True

    def set_second_value(self, val: float):
        self.__second_needle = True
        if val != self.__second_value:
            self.__second_value = val
            self.__redraw_required = True

    def paintEvent(self, a0):
        self.__redraw()

    def __redraw(self):
        if not self.isVisible():
            return
        self.__qp.begin(self)
        self.__qp.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if self.__frame:
            self.__draw_frame()
        self.__draw_scale()
        self.__draw_needle(self.__value, self.__second_value)
        self.__qp.end()

    def set_n_digits(self, n):
        self.__n_digits = n

    def __display_value(self, val):
        pen = QPen(QColor(255 if val > self.__max_val else 0, 0, 0), 1)
        self.__qp.setPen(pen)
        val = np.round(val, 4)
        if val > self.__max_val or val < self.__min_val:
            tmp = "Ошибка"
        else:
            if (self.__max_val - self.__min_val) < 10:
                tmp = f"{{:.{self.__n_digits}f}}".format(val)
                # tmp = f"{round(val, self.n_digits)}"
            elif (self.__max_val - self.__min_val) < 100:
                tmp = "{:.2f}".format(val)
            else:
                tmp = "{:.1f}".format(val)
            if val > 0:
                tmp = ' ' + tmp
        self.__qp.setBrush(QColor(255, 0, 0, alpha=0))
        self.__qp.setFont(QFont('bahnschrift', self.__d // 14))

        if self.__dark:
            pen = QPen(QColor(128, 128, 128), 1)
        else:
            pen = QPen(QColor(0, 0, 0), 1)
        self.__qp.setPen(pen)
        self.__qp.drawText(QRectF(self.__offset + self.__R - 50, self.__offset + self.__R - self.__R / 2, 100, self.__d / 10), Qt.AlignmentFlag.AlignCenter,
                         f"{self.__unit}")

        if self.__dark:
            color = QColor(0xFFFFFF)
        else:
            color = QColor(255 if val > self.__max_val else 0, 0, 0)
        pen = QPen(color, 1)
        self.__qp.setPen(pen)
        self.__qp.setFont(QFont('cascadia code', self.__d // 16))
        self.__qp.drawText(QRectF(self.__offset + self.__R - 50, self.__offset + self.__R + self.__d / 5, 100, self.__R / 4), Qt.AlignmentFlag.AlignCenter,
                         f"{tmp}")

        if self.__dark:
            pen = QPen(QColor(0xFFFFFF), 1)
        else:
            pen = QPen(QColor(0), 1)
        self.__qp.setPen(pen)
        self.__qp.setFont(QFont('bahnschrift', self.__d // 16))
        y0 = self.__offset + int(self.__R + self.__d // 2.2)
        self.__qp.drawText(self.__offset, y0, self.__d, self.__d // 10, Qt.AlignmentFlag.AlignCenter, self.__label)
