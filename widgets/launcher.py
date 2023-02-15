from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import (QWidget, QCompleter)

from tools import get_config, get_apps_list


class Launcher(QWidget):
    def __init__(self, *args, **kwargs):
        super(Launcher, self).__init__(*args, **kwargs)
        # Load the UI Page
        self.config = get_config()
        uic.loadUi('ui/launcher.ui', self)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint) # | Qt.WindowModal)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.hideBtn.clicked.connect(self.on_click)
        apps = get_apps_list("/usr/bin")
        self.completer = QCompleter(apps)
        self.lineEdit.setCompleter(self.completer)

    @pyqtSlot()
    def on_click(self):
        self.hide()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            print("Enter")
