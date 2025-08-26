from PyQt6.QtWidgets import QWidget


class ControllableWidget(QWidget):

    def __init__(self, widget, x, y, w, h, active=True, on_release=True):
        super().__init__(widget)
        self.setGeometry(x, y, w, h)

        self.setMouseTracking(True)

        self.__mouse_pressed = False
        self.__control_state = False
        self.__on_release = on_release
        self.__active = active

        self.show()

    @property
    def mouse_pressed(self):
        if not self.__active:
            return False
        return self.__mouse_pressed

    @property
    def controllable(self):
        return self.__active

    def underMouse(self):
        if not self.__active:
            return False
        return super().underMouse()
    
    def enterEvent(self, event):
        if self.__active:
            self.update()
    
    def leaveEvent(self, a0):
        if self.__active:
            self.update()

    def get_control_state(self):
        if not self.__active:
            return False
        return self.__control_state

    def set_control_state(self, state: bool):
        self.__control_state = state

    def mousePressEvent(self, a0):
        self.__mouse_pressed = True
        self.update()
        if not self.__on_release:
            self.__control_state = not self.__control_state

    def mouseReleaseEvent(self, a0):
        self.__mouse_pressed = False
        self.update()
        if self.__on_release:
            self.__control_state = not self.__control_state

    def paintEvent(self, a0):
        pass
