from .kkm_widget import KKM
from .state_widget import StateWidget
from .diagram import Diagram
from .relay import Relay
from .valve import Valve
from .value_widget import ValueWidget
from .error_widget import ErrorWidget
from .pointer_device import PointerDevice
from .timer_widget import TimerWidget


def _get_hook_dirs():
    """Возвращает пути к директориям с хуками PyInstaller"""
    import os
    return [os.path.join(os.path.dirname(__file__), 'hooks')]

