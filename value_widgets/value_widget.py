from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QFontMetrics
from PyQt6.QtCore import Qt, QRectF, QLineF, QTimer, pyqtSlot as Slot
from PyQt6.QtWidgets import QWidget
import numpy as np
from .utils import is_app_dark, background_color


class ValueWidget(QWidget):

    def __init__(self, base_widget, x, y, w=260, h=60, scheme_number="", label="", min_val=0, max_val=1, 
                 units="МПа", dark=False, draw_ref_value=False, color=None, redraw_period=20):
        super().__init__()
        self.setParent(base_widget)
        self.__x = x
        self.__y = y
        self.__w = w
        self.__h = h
        self.__offset_x = 0
        self.__offset_y = 10
        super().setGeometry(x - self.__offset_x, y - self.__offset_y, self.__w + self.__offset_x, self.__h + 2 * self.__offset_y)
        self.__scheme_number = scheme_number
        self.__label = label
        self.__max_value = max_val
        self.__min_value = min_val
        self.__units = units

        self.__vertical = False
        self.__draw_ticks = False

        self.__qp = QPainter()
        self.__value = 0
        self.__ref_value = 0
        self.__draw_ref_value = draw_ref_value
        self.__dark = dark

        if color:
            self.__color = color
        else:
            if self.__dark:
                self.__color = QColor(86, 114, 179, 250)
            else:
                self.__color = QColor(45, 154, 254, 200)

        self.__redraw_required = True

        self.__tmr = QTimer(self)
        self.__tmr.timeout.connect(self.__redraw_process)
        self.__tmr.start(redraw_period)
        self.show()

    def set_dark(self, dark: bool):
        self.__dark = dark

    def set_maximum(self, val: float):
        self.__max_value = val

    def set_minimum(self, val: float):
        self.__min_value = val

    def set_units(self, units: str):
        self.__units = units
        
    def set_vertical(self, vertical):
        self.__vertical = vertical
        
    def set_min_value(self, val):
        self.__min_value = val

    def set_max_value(self, val):
        self.__max_value = val

    @Slot()
    def __redraw_process(self):
        if self.__dark != is_app_dark():
            self.set_dark(is_app_dark())
            self.__redraw_required = True
        if self.__redraw_required:
            self.update()
            self.__redraw_required = False

    def set_value(self, val: float):
        if val != self.__value:
            self.__value = val
            self.__redraw_required = True

    def set_reference_value(self, val: float):
        self.__draw_ref_value = True
        if val != self.__ref_value:
            self.__ref_value = val
            self.__redraw_required = True

    def setGeometry(self, x, y, w, h):
        super().setGeometry(x - self.__offset_x, y - self.__offset_y, w + self.__offset_x, h + 2 * self.__offset_y)
        self.__x = x
        self.__y = y
        self.__w = w
        self.__h = h

    def set_color(self, clr):
        self.__color = QColor(clr)

    def __calc_font_size(self):
        if self.__vertical:
            return round(self.__w / 6)
        else:
            return 12

    def __is_error_value(self, value):
        return self.__min_value > value or value > self.__max_value
    
    def __draw_number_and_background(self):
        # белый прямоугольник
        col = QColor(255, 255, 255)
        if self.__dark:
            col.setRgb(45, 52, 65)
        else:
            col.setRgb(255, 255, 255)
        self.__qp.setBrush(col)
        self.__qp.setPen(QColor(0, 0, 0, 0))

        font_size = self.__calc_font_size()
        font = QFont('bahnschrift', font_size)
        self.__qp.setFont(font)

        metrics = QFontMetrics(font)
        w_text = metrics.horizontalAdvance(self.__scheme_number)
        adder = 10 if w_text > 0 else 0
        if w_text + adder > self.__offset_x:
            self.__offset_x = w_text + adder
            self.setGeometry(self.__x, self.__y, self.__w, self.__h)
        x0 = self.__offset_x

        rect_width =  self.__w
        self.__qp.drawRect(x0, self.__offset_y, rect_width, self.__h - (22 if not self.__vertical else 0))

        if self.__dark:
            self.__qp.setPen(QColor(128, 128, 128))
        else:
            self.__qp.setPen(QColor(0, 0, 0))

        if self.__scheme_number:
            self.__qp.drawText(0, self.__offset_y + 25, f"{self.__scheme_number}")
        return x0

    def __real_to_window_y(self, val):
        return self.__offset_y + self.__h / (self.__max_value - self.__min_value) * (self.__max_value - val)
    
    def __draw_label(self, x0):
        if self.__dark:
            self.__qp.setPen(QColor(0xFFFFFF))
        else:
            self.__qp.setPen(QColor(0))

        font = QFont('bahnschrift', 10)
        self.__qp.setFont(font)

        if self.__vertical:
            height = QFontMetrics(font).height()
            if self.__offset_y < height + 5:
                self.__offset_y = height + 5
                self.setGeometry(self.__x, self.__y, self.__w, self.__h)
            self.__qp.drawText(self.__offset_x, self.__offset_y - 5, self.__label + f", {self.__units}")
        else:
            self.__qp.drawText(x0, self.__offset_y + self.__h - 5, self.__label)

    def draw_ticks(self, draw: bool):
        self.__draw_ticks = draw

    def __draw_axes(self, x0):
        if not self.__draw_ticks:
            return
        
        if self.__vertical:
            font = QFont("bahnschrift", 10)
            self.__qp.setFont(font)
            Y = np.arange(0, self.__h + self.__h / 4, self.__h / 4) + self.__offset_y
            for i, y in enumerate(Y):
                val = y
                self.__qp.drawLine(x0 - 3, round(val), x0 - 8, round(val))

                if i % 2 == 0:
                    txt = f"{self.__max_value - i * (self.__max_value - self.__min_value) / 4}"
                    text_width = QFontMetrics(font).horizontalAdvance(txt)
                    if self.__offset_x < text_width + 10:
                        self.__offset_x = text_width + 10
                        self.setGeometry(self.__x, self.__y, self.__w, self.__h)
                    self.__qp.drawText(0, round(y) - 7, self.__offset_x - 10, 15, Qt.AlignmentFlag.AlignRight, txt)
        else:
            xk = x0 + self.__w - 50
            X = np.arange(x0,  xk + 5, (xk - x0) // 8)
            for i, x in enumerate(X):
                x = int(x)
                if i % 2 == 0:
                    self.__qp.drawLine(x, - 8, x, - 3)
                else:
                    self.__qp.drawLine(x, - 8, x, - 6)

    def __draw_values(self, value, fixed_value, x0):
        if self.__is_error_value(value):
            return
        self.__qp.setBrush(self.__color)
        if self.__vertical:
            yval = self.__real_to_window_y(value)
            y0 = self.__real_to_window_y(0)
            self.__qp.setPen(QColor(0, 0, 0, 0))
            
            self.__qp.drawRect(QRectF(x0, y0, self.__w, yval - y0))

            if self.__draw_ref_value and self.__min_value <= fixed_value <= self.__max_value:
                yval = self.__real_to_window_y(fixed_value)
                self.__qp.setPen(QPen(QColor(6, 214, 160), 2))
                self.__qp.drawLine(QLineF(x0, yval, x0 + self.__w, yval))
        else:
            xk = self.__w
            sizeX_val = ((value / (self.__max_value - self.__min_value)) * (xk - x0))
            x0_val = (abs(self.__min_value) / (self.__max_value - self.__min_value) * (xk - x0)) + x0

            if x0_val != x0:
                self.__qp.setPen(QColor(150, 150, 150))
                self.__qp.drawLine(QLineF(x0_val, self.__offset_y + 5, x0_val, self.__h - 22 - 5))

            self.__qp.setPen(QColor(0, 0, 0, 0))
            self.__qp.drawRect(QRectF(x0_val, self.__offset_y, sizeX_val, self.__h - 22))

            if self.__draw_ref_value and self.__min_value <= fixed_value <= self.__max_value:
                xk = self.__offset_x + self.__w
                sizeX_val = (fixed_value / (self.__max_value - self.__min_value)) * (xk - x0)
                x0_val = abs(self.__min_value) / (self.__max_value - self.__min_value) * (xk - x0) + x0
                self.__qp.setPen(QPen(QColor(6, 214, 160), 2))
                self.__qp.drawLine(QLineF(x0_val + sizeX_val, self.__offset_y + 2, x0_val + sizeX_val, self.__h - 14))

    def __draw_value_text(self, value, x0):
        if not self.__is_error_value(value):
            self.__qp.setPen(QColor(0, 0, 0))
            self.__qp.setFont(QFont('cascadia code', 13))
            if self.__max_value <= 1:
                tmp = f"{value:.3f}"
            elif self.__max_value <= 100:
                tmp = f"{value:.2f}"
            elif self.__max_value <= 1000:
                tmp = f"{value:.1f}"
            else:
                tmp = str(value)

            if not self.__vertical:
                tmp += f" [{self.__units}]"

            if self.__dark:
                self.__qp.setPen(QColor(255, 255, 255))
            else:
                self.__qp.setPen(QColor(0, 0, 0))
            if self.__min_value < 0 and value >= 0:
                tmp = " " + tmp
            self.__qp.drawText(x0, self.__offset_y + 5, self.__w, self.__h - 30, Qt.AlignmentFlag.AlignCenter, tmp)
        else:
            self.__qp.setPen(QColor(255, 0, 0))
            self.__qp.setFont(QFont('bahnschrift', 14))
            self.__qp.drawText(x0, self.__offset_y, self.__w, self.__h - 22, Qt.AlignmentFlag.AlignCenter, "Ошибка")

    def __draw_value(self):
        if not self.isVisible():
            return
        self.__qp.begin(self)
        self.__qp.setRenderHint(QPainter.RenderHint.Antialiasing)

        x0 = self.__draw_number_and_background()

        self.__draw_values(self.__value, self.__ref_value, x0)
        self.__draw_value_text(self.__value, x0)
        self.__draw_label(x0)

        self.__draw_axes(x0)

        self.__qp.end()

    def paintEvent(self, a0):
        self.__draw_value()