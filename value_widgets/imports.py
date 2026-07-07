try:
    from PyQt6.QtGui import QFont, QIcon, QFontMetrics, QPainter, QColor, QPen, QGuiApplication, QPainterPath, QPolygonF
    from PyQt6.QtCore import Qt, pyqtSlot as Slot, QTimer, QLineF, QRectF, QPointF
    from PyQt6.QtWidgets import QPushButton, QFrame, QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy, QLabel, QWidget
except ImportError:
    from PyQt5.QtGui import QFont, QIcon, QFontMetrics, QPainter, QColor, QPen, QGuiApplication, QPainterPath, QPolygonF
    from PyQt5.QtCore import Qt, pyqtSlot as Slot, QTimer, QLineF, QRectF, QPointF
    from PyQt5.QtWidgets import QPushButton, QFrame, QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy, QLabel, QWidget