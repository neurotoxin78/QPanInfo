from PyQt5.QtCore import Qt, QSize, QCoreApplication, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QFrame, QWidget, QGridLayout, QLabel, QProgressBar, QGraphicsDropShadowEffect)
from tools import loadStylesheet, get_config, get_cputemp, setShadow, get_power_consumption

class PowerMonitor(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        stylesheet = "stylesheets/systemload.qss"
        self.setStyleSheet(loadStylesheet(stylesheet))
        self.config = get_config()
        self.sensortimer = QTimer()
        self.sensortimer.timeout.connect(self.refresh)
        self.sensortimer.start(self.config['intervals']['sensor_refresh_ms'])
        font = QFont()
        font.setFamily("DejaVu Sans Mono for Powerline")
        font.setPointSize(16)
        font.setBold(True)
        font.setUnderline(False)
        font.setWeight(100)
        self.sensor_frame = QFrame()
        self.sensor_frame.setMinimumSize(QSize(0, 135))
        self.sensor_frame.setMaximumSize(QSize(16777215, 135))
        self.sensor_frame.setStyleSheet("background-color: rgba(85, 85, 127, 160);")
        # self.sensor_frame.setFrameShape(QFrame.NoFrame)
        # self.sensor_frame.setFrameShadow(QFrame.Raised)
        self.sensor_frame.setObjectName("sensor_frame")
        self.sensor_frameLayout = QGridLayout(self.sensor_frame)
        self.sensor_frameLayout.setObjectName("sensor_frameLayout")
        self.setLayout(self.sensor_frameLayout)
        self.voltage = QLabel()
        self.voltage.setFont(font)
        self.voltage.setMinimumSize(QSize(39, 39))
        self.voltage.setObjectName("voltage")
        self.sensor_frameLayout.addWidget(self.voltage, 0, 0, 1, 1)
        self.current = QLabel()
        self.current.setFont(font)
        self.current.setMinimumSize(QSize(39, 39))
        self.current.setObjectName("current")
        self.sensor_frameLayout.addWidget(self.current, 0, 2, 1, 1)
        self.power = QLabel()
        self.power.setFont(font)
        self.power.setMinimumSize(QSize(39, 39))
        self.power.setObjectName("power")
        self.sensor_frameLayout.addWidget(self.power, 0, 3, 1, 1)
        setShadow(self.voltage, 20)
        setShadow(self.current, 20)
        setShadow(self.power, 20)

    def refresh(self):
        raw_voltage = get_power_consumption("/sys/class/hwmon/hwmon2/in1_input") / 1000
        raw_current = get_power_consumption("/sys/class/hwmon/hwmon2/curr1_input") / 10
        decor = "%.1f" % raw_voltage 
        self.voltage.setText(decor + "V")
        current = "%.0f" % raw_current
        self.current.setText(current + "mA")
        power = (raw_voltage * raw_current)  / 1000
        decor = "%.1f" % power
        self.power.setText(decor + "W")
