from statistics import mean
import importlib.resources as pkg_resources
from pathlib import Path
from PyQt6.QtGui import QColor


def choose_contrast_color(color: QColor):
        if mean((color.red(), color.green(), color.blue())) >= 128:
            return QColor(0, 0, 0)
        else:
            return QColor(255, 255, 255)
        

def get_image_path(filename: str) -> str:
    """Получить путь к изображению из пакета"""
    try:
        return str(pkg_resources.files("value_widgets.images") / filename)
    except AttributeError:
        with pkg_resources.path("value_widgets.images", filename) as path:
            return str(Path(path))
    except:
        return filename
        