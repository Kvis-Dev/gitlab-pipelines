import sys

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QPixmap, QColor, QDesktopServices
from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout, QGridLayout, QSystemTrayIcon, QWidgetAction

from data import Job, Pipeline
from helpers import load_svg_sized_pixmap
from settings import COLORS, ICON_SIZE, PIPELINE_ICON_SIZE


class JobWidget(QLabel):

    def __init__(self, job: Job):
        super(JobWidget, self).__init__()
        self.job = job
        self.setToolTip(f"{job.id} {job.name}")
        # self.setMaximumWidth(ICON_SIZE)
        pixmap = load_svg_sized_pixmap(f"icons/sprite_icons_status_{job.status}.svg")

        color_mask = QPixmap(pixmap.size())
        q_color = QColor(COLORS[job.status])

        color_mask.fill(q_color)
        color_mask.setMask(pixmap.createMaskFromColor(QColor(255, 255, 255, 0)))
        color_mask.setMask(pixmap.createMaskFromColor(QColor(255, 255, 255, 255)))

        resized = color_mask.scaled(
            ICON_SIZE, ICON_SIZE,
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation
        )

        self.setPixmap(resized)


class PipelineStatusWidget(QWidget):

    def __init__(self, pipeline: Pipeline, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pipeline = pipeline
        self.init_ui()

    def init_ui(self):
        hbox = QHBoxLayout()
        hbox.setSpacing(0)
        # {self.pipeline.status}
        hbox.addWidget(QLabel(f"#{self.pipeline.id}"))

        qlabel = QLabel()
        pixmap = load_svg_sized_pixmap(f"icons/sprite_icons_status_{self.pipeline.status}.svg")

        pixmap = pixmap.scaled(
            PIPELINE_ICON_SIZE, PIPELINE_ICON_SIZE,
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation
        )

        qlabel.setPixmap(pixmap)

        hbox.addWidget(qlabel)
        self.setLayout(hbox)


class PipelineWidget(QWidget):

    def __init__(self, pipeline: Pipeline, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pipeline = pipeline
        self.init_ui()

    def mouseReleaseEvent(self, QMouseEvent):
        QDesktopServices.openUrl(QUrl(self.pipeline.web_url))
        super(PipelineWidget, self).mouseReleaseEvent(QMouseEvent)

    def init_ui(self):
        # cols = max([len(s) for s in self.pipeline.stages.values()])
        rows = len(self.pipeline.stages)
        hbox = QHBoxLayout()
        hbox.addWidget(PipelineStatusWidget(self.pipeline))
        hbox.setSpacing(0)

        if rows > 1:
            grid = QGridLayout()
            i, j = 0, 0
            for stage in sorted(
                    self.pipeline.stages.values(), key=lambda s: min(j.id for j in s)
            ):
                j = 0
                for job in sorted(stage, key=lambda j: j.id):
                    grid.addWidget(JobWidget(job), j, i)
                    j += 1
                i += 1
            w = QWidget()
            w.setLayout(grid)
            hbox.addWidget(w)
        else:

            for stage in sorted(
                    self.pipeline.stages.values(), key=lambda s: max(j.id for j in s)
            ):
                for job in sorted(stage, key=lambda j: j.id):
                    hbox.addWidget(JobWidget(job))

            hbox.addStretch(1)

        self.setLayout(hbox)


class SystemTrayIcon(QSystemTrayIcon):

    def __init__(self, icon, app, parent=None):
        QSystemTrayIcon.__init__(self, icon, parent)
        self.app = app
        self.menu = QtWidgets.QMenu(None)
        # self.menu.aboutToShow.connect(self.app.thread.force_update)
        self.activated.connect(self.app.thread.force_update)
        self.setContextMenu(self.menu)
        self.build_menu()

    @QtCore.pyqtSlot()
    def build_menu(self):
        if self.app.prev_pipelines and self.app.pipelines and self.app.prev_pipelines == self.app.pipelines:
            return

        self.menu.clear()

        for pipeline in self.app.pipelines:
            widget_action = QWidgetAction(self.menu)
            widget_action.setDefaultWidget(PipelineWidget(
                pipeline
            ))
            self.menu.addAction(widget_action)
            self.menu.addSeparator()

        self.menu.addAction("Exit", self.exit)

        if self.menu.isVisible() and self.app.prev_pipelines != self.app.pipelines:
            pos = self.menu.pos()
            self.menu.hide()
            self.menu.popup(pos)

    def exit(self):
        # send_message("tit le", "m sg")
        self.app.is_running = False
        sys.exit(0)
