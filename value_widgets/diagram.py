from .utils import choose_contrast_color
from .color_generator import ColorGenerator

from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QFontMetrics
from PyQt6.QtCore import Qt, QPointF, QRectF, QLineF, pyqtSlot as Slot, QTimer
from PyQt6.QtWidgets import QWidget


class Diagram(QWidget):
    def __init__(self, widget, x, y, w, h, redraw_period=15):
        super().__init__()
        self.setParent(widget)
        self.__offset_x = 50
        self.__offset_y = 25
        self.__h = h
        self.__w = w

        self.__min_val = 0
        self.__max_val = 1

        self.__colors = []
        gen = ColorGenerator()
        for _ in range(len(gen)):
            self.__colors.append(gen.get_color())

        self.__n_items = 1
        self.__n_sections = 1
        self.__label = "Untitled"
        self.__legend = ["Untitled"]
        self.__values = list()
        self.__dark = False
        self.__section_names = list()

        self.__redraw_required = True

        self.setGeometry(x, y, w, h)

        self.__tmr = QTimer(self)
        self.__tmr.timeout.connect(self.__redraw_process)
        self.__tmr.start(redraw_period)
        self.show()

    def paintEvent(self, a0):
        self.__redraw()

    @Slot()
    def __redraw_process(self):
        if self.__redraw_required:
            self.update()
            self.__redraw_required = False

    def set_dark(self, dark: bool):
        self.__dark = dark
        
    def set_label(self, label: str) -> None:
        self.__label = label
        
    def set_section_names(self, names):
        self.__section_names = names
        
    def set_min_value(self, val: float):
        self.__min_val = val
        
    def set_max_value(self, val: float):
        self.__max_val = val

    def set_number_of_values(self, n: int):
        self.__n_items = n
        self.__values = [[0] * self.__n_items] * self.__n_sections

    def set_labels(self, *labels):
        self.__legend = list()
        for lbl in labels:
            self.__legend.append(lbl)

    def set_color(self, n_value: int, color):
        if n_value >= self.__n_items:
            return
        self.__colors[n_value] = color

    def set_number_of_sections(self, n: int):
        self.__n_sections = n
        self.__values = [[0] * self.__n_items] * self.__n_sections

    def set_values(self, values):
        self.__values = values
        self.__redraw_required = True

    def setGeometry(self, x, y, w, h):
        self.__w = w
        self.__h = h
        super().setGeometry(x - self.__offset_x, y - self.__offset_y, w + self.__offset_x * 2, h + self.__offset_y * 2)

    def __real_to_window_y(self, y):
        return self.__offset_y + self.__h / (self.__max_val - self.__min_val) * (self.__max_val - y)

    def __redraw(self):
        if not self.isVisible():
            return
        qp = QPainter()

        qp.begin(self)
        qp.setRenderHint(QPainter.RenderHint.Antialiasing)
        y = self.__real_to_window_y(0)

        pen = QPen()

        DEFAULT_COLOR = QColor(210, 210, 210) if self.__dark else QColor(0, 0, 0)
        
        pen.setColor(DEFAULT_COLOR)
        qp.setPen(pen)

        qp.setFont(QFont("bahnschrift", 14))
        qp.drawText(self.__offset_x, 0, self.__w, 20, Qt.AlignmentFlag.AlignCenter, self.__label)

        section_width = self.__w / self.__n_sections
        pen.setWidthF(0.75)
        pen.setStyle(Qt.PenStyle.DotLine)
        qp.setPen(pen)

        step = 5
        wrect = (section_width - step) / self.__n_items - step
        rect_lists = [[QRectF() for _ in range(self.__n_sections)] for _ in range(self.__n_items)]

        for i in range(self.__n_sections):
            if i > 0:
                pen.setWidthF(0.75)
                pen.setStyle(Qt.PenStyle.DotLine)
                qp.setPen(pen)
                x = self.__offset_x + i * section_width
                qp.drawLine(QLineF(x, self.__offset_y + self.__h, x, self.__offset_y))

            if i < len(self.__section_names):
                qp.setFont(QFont("consolas", 12))
                qp.setBrush(DEFAULT_COLOR)
                qp.drawText(QRectF(self.__offset_x + i * section_width, self.__offset_y + self.__h + 5, section_width, 15),
                            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                            self.__section_names[i])

            
            sector_x0 = self.__offset_x + i * section_width
            for j in range(self.__n_items):
                value = self.__values[i][j]

                if value < self.__min_val:
                    value = self.__min_val
                if value > self.__max_val:
                    value = self.__max_val

                window_val = self.__real_to_window_y(value)
                h = y - window_val
                x = (j + 1) * step + sector_x0 + j * wrect
                rect_lists[j][i] = QRectF(x, window_val, wrect, h)

        qp.setClipRect(self.__offset_x, self.__offset_y, self.__w, self.__h)
        for i in range(self.__n_items):
            qp.setPen(QColor(0, 0, 0, 0))
            qp.setBrush(QColor(self.__colors[i]))
            qp.drawRects(rect_lists[i])

            font = QFont("consolas", 16)
            qp.setFont(font)
            for j in range(self.__n_sections):
                y = rect_lists[i][j].y()
                x = rect_lists[i][j].x()
                h = rect_lists[i][j].height()
                
                text = f"{round(self.__values[j][i])}"
                bounding_rect = QFontMetrics(font).boundingRect(text)

                qp.setPen(choose_contrast_color(QColor(self.__colors[j][i])))
                if bounding_rect.width() > wrect - 5:
                    qp.save()
                    qp.translate(x, y + wrect)
                    qp.rotate(-90)
                    qp.drawText(QRectF(-h + self.__offset_y, 0, h, wrect), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, text)
                    qp.restore()
                else:   
                    rect = QRectF(x, y + 5, wrect, bounding_rect.height())
                    qp.drawText(rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, text)
        qp.setClipRect(0, 0, self.width(), self.height())

        pen.setStyle(Qt.PenStyle.SolidLine)
        pen.setColor(DEFAULT_COLOR)
        qp.setPen(pen)

        qp.drawLine(QLineF(self.__offset_x, self.__offset_y + self.__h, self.__offset_x + self.__w, self.__offset_y + self.__h))
        qp.drawLine(QLineF(self.__offset_x, self.__offset_y + self.__h, self.__offset_x, self.__offset_y))

        y = self.__offset_y
        i = 0
        val = self.__max_val
        step = (self.__max_val - self.__min_val) / 4
        while y <= self.__offset_y + self.__h:
            if i % 2 == 0:
                d = 5
            else:
                d = 3
            qp.drawLine(QLineF(self.__offset_x, y, self.__offset_x - d, y))
            qp.setFont(QFont("bahnschrift", 10))
            qp.drawText(QRectF(self.__offset_x - 50, y - 10, 40, 20), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, f"{round(val)}")

            y += self.__h / 4
            val -= step

        if len(self.__legend):
            y0 = self.__offset_y
            h = 13
            step = 5
            x0 = self.__offset_x + self.__w - h - step
            radius = h / 2

            font = QFont("Bahnschrift, Arial", 11)
            qp.setFont(font)
            metrics = QFontMetrics(font)
            max_width = max(metrics.horizontalAdvance(lbl) for lbl in self.__legend)
            wrect = max_width + h + 4* step
            hrect = metrics.height() * len(self.__legend) + step * (len(self.__legend) - 1)
            x0 = self.__offset_x + self.__w - wrect
            
            qp.setPen(QColor(0, 0, 0, 0))
            qp.setBrush(QColor(200, 200, 200, 100))
            qp.drawRoundedRect(QRectF(x0, y0, wrect, hrect), radius, radius)

            x0 += 5
            y0 += 5

            for i in range(len(self.__legend)):
                qp.setPen(QColor(0, 0, 0, 0))
                qp.setBrush(QColor(self.__colors[i]))
                
                qp.drawRoundedRect(QRectF(x0, y0, h, h), radius, radius)

                qp.setPen(QColor(self.__colors[i]))
                qp.drawText(QPointF(x0 + h + 5, y0 + h), self.__legend[i])
                y0 += h + 4

        qp.end()
