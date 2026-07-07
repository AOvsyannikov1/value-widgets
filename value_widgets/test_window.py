from . import PointerDevice, TimerWidget, ValueWidget, Relay, Valve, StateWidget, Diagram, ErrorWidget
try:
    from PyQt6 import QtCore, QtWidgets, QtGui
except ImportError:
    from PyQt5 import QtCore, QtWidgets, QtGui
from math import *
from time import monotonic

class Win(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self.mano = PointerDevice(self, 50, 50, 200, min_value=-100, max_value=100, label="Какой-то синус", units="Pomidors")

        self.timer = TimerWidget(self, 20, 300, begin_value=0, end_value=100, normal_min=0, normal_max=4, name="Разгон", units="км/ч")

        self.val_wid = ValueWidget(self, 300, 20, scheme_number="А123", label="Название датчика", min_val=-15, max_val=10, units="кВ")

        self.val_wid_tmr = ValueWidget(self, 630, 20, scheme_number="А124", label="Измерение времени", min_val=0, max_val=400, units="км/ч")

        self.relay = Relay(self, 300, 100, label="Реле", controllable=True)

        self.valve = Valve(self, 420, 100, label="Кран", controllable=True)

        self.state = StateWidget(self, 300, 200, 250, 50)
        self.state.add_state("Значение 0", 0, "red")
        self.state.add_state("Значение 1", 1, "green")
        self.state.add_state("Значение 2", 2, "blue")

        self.diagram = Diagram(self, 50, 450, 1000, 300)
        self.diagram.set_number_of_sections(7)
        self.diagram.set_number_of_values(3)
        self.diagram.set_max_value(150)
        self.diagram.set_min_value(-150)
        self.diagram.set_label("Пример диаграммы")
        self.diagram.set_labels("Значение 1", "Значение 2", "Значение 3")
        self.diagram.set_section_names([f"Секция {i + 1}" for i in range(7)])

        self.error1 = ErrorWidget(self, 300, 270, "Нажми на реле!")
        self.error2 = ErrorWidget(self, 300, 300, "Нажми на кран!")

        self.val = 0

        self.tmr = QtCore.QTimer(self)
        self.tmr.timeout.connect(self.loop)
        self.tmr.start(25)

    def loop(self):
        t = monotonic()
        self.mano.set_value(50 * sin(0.6 * t) + 50 * sin(1.01 * t))
        self.val_wid.set_value(11 * sin(t))
        self.val_wid_tmr.set_value(self.val)

        if self.timer.measuring_in_progress():
            self.val += 1
        else:
            self.val = 0
        self.timer.set_controlled_value(self.val)

        val = sin(4 *  t)
        self.relay.set_value(2 if val < -0.5 else (0 if val < 0.25 else 1))
        if val < -0.5:
            self.valve.set_state(0)
        elif val < 0:
            self.valve.set_state(1)
        elif val < 0.5:
            self.valve.set_state(2)
        else:
            self.valve.set_state(3)

        self.state.set_state(0 if val < -0.25 else (1 if val < 0.75 else 2))

        values = [[100 * sin(0.5 * t + i), 100 * cos(0.5 * t + i), 100 * sin(0.6 * t + i)] for i in range(7)]
        self.diagram.set_values(values)

        self.error1.set_error(self.relay.get_control_state())
        self.error2.set_error(self.valve.get_control_state())


def show_test_widgets():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = Win()
    ui.show()
    sys.exit(app.exec())
