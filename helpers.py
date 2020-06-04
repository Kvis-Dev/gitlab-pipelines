import subprocess

from PyQt5.QtGui import QImage, QPainter, QPixmap
from PyQt5.QtSvg import QSvgRenderer


def send_message(title, message):
    subprocess.Popen(['notify-send', title, message])
    return


def load_svg_sized_pixmap(path, w=100, h=100):
    svg_renderer = QSvgRenderer(path)
    image = QImage(w, h, QImage.Format_ARGB32)
    painter = QPainter(image)
    painter.eraseRect(0, 0, w, h)
    svg_renderer.render(painter)
    painter.end()
    return QPixmap.fromImage(image)
