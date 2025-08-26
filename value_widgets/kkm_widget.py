from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QPolygonF, QPainterPath, QFontMetrics, QStyleHints
from PyQt6.QtCore import Qt, QPointF, QRectF, QLineF, QTimer, pyqtSlot as Slot
from PyQt6.QtWidgets import QWidget
import numpy as np
from .timer import Timer


class KKM(QWidget):

    def __init__(self, widget, x, y, scale, redraw_period=20):
        super().__init__()
        self.setParent(widget)
        self.__x = x
        self.__y = y
        self.__scale = scale
        self.__qp = QPainter()

        self.__radius = int(160 * scale)
        self.__arc_offset = int(50 * scale)
        self.setGeometry(x, y, int(60 * scale), int(60 * scale))
        self.__step = 40 / 3
        self.__handle_length = int(200 * scale)

        self.__position = 0
        self.__new_position = 0

        self.__blink_tmr = Timer(250)
        self.visible = True

        self.angles = (3 * self.__step, 2 * self.__step, self.__step, 0, -self.__step, -2 * self.__step, -3 * self.__step)
        self.current_angle = self.angles[0]
        self.target_angle = self.current_angle

        self.__redraw_required = True

        self.__tmr = QTimer(self)
        self.__tmr.timeout.connect(self.__redraw_process)
        self.__tmr.start(redraw_period)
        self.show()

    @Slot()
    def __redraw_process(self):
        if self.__redraw_required:
            self.update()
            # self.__redraw_required = False

    def paintEvent(self, a0):
        self.__redraw()

    def set_position(self, pos: int):
        self.__new_position = pos

    def pos_to_str(self, pos: int):
        if pos < 1 or pos > 7:
            return "?"
        match pos:
            case 1:
                return "I"
            case 2:
                return "II"
            case 3:
                return "III"
            case 4:
                return "IV"
            case 5:
                return "VA"
            case 6:
                return "V"
            case 7:
                return "VI"

    def __draw_handle(self, angle, visible):
        if not visible:
            return
        angle = np.deg2rad(angle)
        leg_x = round(self.__radius * np.sin(angle))
        leg_y = round(self.__radius * np.cos(angle))
        leg_x1 = round((self.__handle_length + self.__radius) * np.sin(angle))
        leg_y1 = round((self.__handle_length + self.__radius) * np.cos(angle))

        self.__qp.setPen(QPen(QColor(0, 0, 0), int(self.__scale * 25)))
        self.__qp.setBrush(QColor(0, 0, 0, alpha=0))
        self.__qp.drawLine(self.x() - leg_x, self.y() - leg_y + self.__arc_offset, self.x() - leg_x1,
                         self.y() - leg_y1 + self.__arc_offset)
        self.__qp.setBrush(QColor(0, 0, 0))

        center = QPointF(self.x() - leg_x1, self.y() - leg_y1 + self.__arc_offset)
        self.__qp.drawEllipse(center, int(75 * self.__scale/2), int(75 * self.__scale/2))

    def __draw_animated_handle(self, pos):
        if pos > 0 and pos != self.__position:
            self.target_angle = self.angles[pos - 1]
            self.__position = pos
            self.visible = True
        elif pos == 0:
            self.target_angle = self.angles[3]
            self.current_angle = self.target_angle
            self.__position = pos

        if pos == 0:
            if self.__blink_tmr.expired():
                self.__blink_tmr.restart()
                self.visible = not self.visible

        self.__draw_handle(self.current_angle, self.visible)
        if self.target_angle < self.current_angle - 1:
            self.current_angle -= self.__step / 5
        elif self.target_angle > self.current_angle + 1:
            self.current_angle += self.__step / 5

    def __redraw(self):
        self.__qp.begin(self)
        self.__qp.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.__draw_animated_handle(self.__new_position)

        self.__qp.setPen(QPen(QColor(0, 0, 0), int(self.__scale) * 2))

        x = self.x() - int(self.__scale * 170)
        y = int(self.y() - 2 * self.__arc_offset - 10 * self.__scale)
        w = 2 * int(self.__scale * 170)
        h = 6 * self.height()

        point = QPointF(x, y)

        path = QPainterPath(point)
        boundingRect = QRectF(x, y, w, h)
        path.moveTo(boundingRect.center())
        path.arcTo(boundingRect, 20, 150)
        path.closeSubpath()
        self.__qp.setPen(QPen(QColor(0, 0, 0), 3))
        self.__qp.setBrush(QColor(255, 255, 255))
        self.__qp.drawPath(path)

        self.__qp.setBrush(QColor(0, 0, 0))
        self.__qp.drawRoundedRect(self.x() - int(self.__scale * 170), self.y() - self.height(), 2 * int(self.__scale * 170), int(2.3 * self.height()),
                                10, 10)
        for i in range(7):
            angle = np.deg2rad(self.angles[i])
            leg_x = round(self.__radius * np.sin(angle))
            leg_y = round(self.__radius * np.cos(angle))
            leg_x1 = round((self.__radius - 10 * self.__scale) * np.sin(angle))
            leg_y1 = round((self.__radius - 10 * self.__scale) * np.cos(angle))
            self.__qp.drawLine(self.x() - leg_x, self.y() + self.__arc_offset - leg_y, self.x() - leg_x1,
                             self.y() + self.__arc_offset - leg_y1)

        self.__qp.setPen(QColor(255, 255, 255))
        self.__qp.setFont(QFont("consolas", int(60 * self.__scale)))
        self.__qp.drawText(self.x() - int(self.__scale * 170), self.y() - self.height(), 2 * int(self.__scale * 170),
                         int(2.3 * self.height()), Qt.AlignmentFlag.AlignCenter, self.pos_to_str(self.__new_position))
        self.__qp.end()
