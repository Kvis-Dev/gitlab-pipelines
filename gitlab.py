import sys
import time
from typing import List

import requests
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QSound
from PyQt5.QtWidgets import QApplication

from data import Job, Pipeline
from helpers import send_message
from settings import QUERY_TIME, GITLAB_URL, GITLAB_PROJECT_ID, USERNAME, API_KEY, BAD_STATUSES, GOOD_STATUSES, \
    RUNNING_STATUSES
from widgets import SystemTrayIcon

# http://gitlab.lean/api/v4/projects/11/jobs

# Sound:  https://notificationsounds.com/notification-sounds/hasty-ba-dum-tss-615

_NOTIFIED_PIPELINES: List[int] = []


class Updater(QtCore.QThread):
    is_running = False
    _force_update = False

    received_data_signal = QtCore.pyqtSignal(list)

    @QtCore.pyqtSlot()
    def force_update(self):
        self._force_update = True

    def get_pipeline_info(self):
        try:
            resp = requests.get(f"{GITLAB_URL}/api/v4/projects/{GITLAB_PROJECT_ID}/jobs", headers={
                'Private-Token': API_KEY
            })
            return resp.json()
        except Exception as e:
            print("Exception", e)
            return []

        # Left for debug purposes
        # with open('test.json') as file:
        #     return json.load(file)

    def run(self):

        i = QUERY_TIME

        while self.is_running:
            time.sleep(1)

            if i == QUERY_TIME or self._force_update:
                self._force_update = False
                pipeline_info = self.get_pipeline_info()

                self.received_data_signal.emit(pipeline_info)
                i = 0

            i += 1


class App:
    draw_menu_signal = QtCore.pyqtSignal(int)

    def __init__(self, app):
        self.app = app
        self.is_running = True
        self.force_update = False
        self.prev_pipelines = []
        self.pipelines = []

        self.notification_sound = QSound("notify.wav")

        self.window = QtWidgets.QWidget()
        self.icons = {
            'grey': QIcon("icons/gitlab_grey.svg"),
            'green': QIcon("icons/gitlab_green.svg"),
            'orange': QIcon("icons/gitlab_orange.svg"),
            'red': QIcon("icons/gitlab_red.svg"),
        }

        self.thread = Updater()
        self.tray_icon = SystemTrayIcon(self.icons['grey'], self, self.window)

        self.thread.is_running = True
        self.thread.received_data_signal.connect(self.got_data)
        self.thread.received_data_signal.connect(self.tray_icon.build_menu)
        self.thread.start()

    def got_data(self, pinfo):
        self.prev_pipelines = self.pipelines
        self.pipelines = self.parse_pipeline_info(pinfo)
        self.check_for_notification()
        self.set_icon()

    def parse_pipeline_info(self, pinfo):
        pipelines = {}

        for job in pinfo:
            pipe_id = job["pipeline"]["id"]
            if pipe_id not in pipelines:
                pipelines[pipe_id] = Pipeline(
                    id=pipe_id,
                    user=job['user']['username'],
                    status=job['pipeline']['status'],
                    web_url=job['pipeline']['web_url'],
                )

            pipeline = pipelines[pipe_id]

            pipeline.stages[job['stage']].append(Job(
                id=job["id"],
                status=job["status"],
                name=job["name"],
                allow_failure=job["allow_failure"],
            ))

        return list(pipelines.values())

    def set_icon(self):
        if not self.pipelines:
            self.tray_icon.setIcon(self.icons['grey'])

        good, bad = 0, 0
        for pipeline in self.pipelines:
            if pipeline.status in BAD_STATUSES:
                bad += 1

            if pipeline.status in GOOD_STATUSES:
                good += 1

        if bad:
            self.tray_icon.setIcon(self.icons['red'])
        elif good:
            self.tray_icon.setIcon(self.icons['green'])
        else:
            self.tray_icon.setIcon(self.icons['orange'])

    def check_for_notification(self):
        for pipeline in self.pipelines:
            should_notify_user = self.should_notify_user(pipeline)
            if not should_notify_user:
                continue

            if pipeline.status in BAD_STATUSES:
                if pipeline.id not in _NOTIFIED_PIPELINES:
                    self.make_notification("Pipeline alert", f"Pipeline {pipeline.id} is in status {pipeline.status}")
                    _NOTIFIED_PIPELINES.append(pipeline.id)

            if pipeline.status in RUNNING_STATUSES:
                if pipeline.id in _NOTIFIED_PIPELINES:
                    _NOTIFIED_PIPELINES.remove(pipeline.id)

    def should_notify_user(self, pipeline: Pipeline):
        if '__all__' in USERNAME or pipeline.user == USERNAME:
            return True
        return False

    def make_notification(self, title, message):
        send_message(title, message)
        self.notification_sound.play()

    def run(self):
        self.thread.start()
        self.tray_icon.show()
        sys.exit(self.app.exec_())


if __name__ == '__main__':
    App(QApplication(sys.argv)).run()
