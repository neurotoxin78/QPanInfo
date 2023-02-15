from datetime import datetime

from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QWidget, QGridLayout, QLabel, QGraphicsDropShadowEffect)

from tools import get_config, loadStylesheet


class Clock(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        stylesheet = "stylesheets/weather.qss"
        self.setStyleSheet(loadStylesheet(stylesheet))
        self.config = get_config()
        self.clocktimer = QTimer()
        self.clocktimer.timeout.connect(self.Clock)
        self.clocktimer.start(self.config['intervals']['clock_refresh_ms'])
        self.config = get_config()
        self.layout = QGridLayout()
        self.time_Label = QLabel()
        self.time_Label.setMinimumSize(QSize(0, 0))
        self.time_Label.setMaximumSize(QSize(680, 16777215))
        font = QFont()
        font.setFamily("DSEG14 Classic")
        font.setPointSize(80)
        #font.setBold(True)
        #font.setItalic(False)
        #font.setWeight(75)
        self.time_Label.setFont(font)
        self.time_Label.setStyleSheet("color: " + self.config['colors']['clock_color'] + ";")
        self.time_Label.setAlignment(Qt.AlignCenter)
        self.time_Label.setObjectName("time_Label")
        self.layout.addWidget(self.time_Label, 0, 5, 1, 1, Qt.AlignCenter)
        self.setLayout(self.layout)
        shadow = QGraphicsDropShadowEffect()
        # setting blur radius
        shadow.setBlurRadius(15)
        self.time_Label.setGraphicsEffect(shadow)

    def Clock(self):
        now = datetime.now()
        current_time = now.strftime(self.config['format']['time_format'])
        self.time_Label.setText(current_time)  # u'\u2770' + + u'\u2771'