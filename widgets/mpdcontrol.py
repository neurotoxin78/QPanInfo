from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import (QWidget, QCompleter)
from tools import get_config


class MPDControl(QWidget):
    def __init__(self, *args, **kwargs):
        super(MPDControl, self).__init__(*args, **kwargs)
        # Load the UI Page
        self.config = get_config()
        uic.loadUi('ui/mpd.ui', self)