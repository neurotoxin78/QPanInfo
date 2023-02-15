import psutil
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QFrame, QWidget, QGridLayout, QLabel)

from tools import get_config, get_size, loadStylesheet


class NetworkLoad(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        stylesheet = "stylesheets/networkload.qss"
        self.setStyleSheet(loadStylesheet(stylesheet))
        self.config = get_config()
        self.io = psutil.net_io_counters(pernic=True)
        self.nettimer = QTimer()
        self.nettimer.timeout.connect(self.netStat)
        self.nettimer.start(self.config['intervals']['net_interval_ms'])
        self.net_frame = QFrame()
        self.net_frame.setMinimumSize(QSize(0, 100))
        self.net_frame.setMaximumSize(QSize(16777215, 140))
        self.net_frame.setFrameShape(QFrame.StyledPanel)
        self.net_frame.setFrameShadow(QFrame.Raised)
        self.net_frame.setObjectName("net_frame")
        self.net_frameLayout = QGridLayout(self.net_frame)
        self.net_frameLayout.setObjectName("net_frameLayout")
        self.interfaceLabel = QLabel(self.net_frame)
        self.interfaceLabel.setMinimumSize(QSize(0, 30))
        self.interfaceLabel.setMaximumSize(QSize(16777215, 30))
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.interfaceLabel.setFont(font)
        self.interfaceLabel.setStyleSheet("color: rgba(255, 255, 255, 200);")
        self.interfaceLabel.setAlignment(Qt.AlignCenter)
        self.interfaceLabel.setObjectName("interfaceLabel")
        self.net_frameLayout.addWidget(self.interfaceLabel, 0, 0, 1, 3)
        self.upLabel = QLabel(self.net_frame)
        self.upLabel.setMinimumSize(QSize(0, 30))
        self.upLabel.setFont(font)
        self.upLabel.setStyleSheet("color: rgb(85, 255, 127);")
        self.upLabel.setAlignment(Qt.AlignCenter)
        self.upLabel.setObjectName("upLabel")
        self.net_frameLayout.addWidget(self.upLabel, 2, 2, 1, 1)
        self.ipLabel = QLabel(self.net_frame)
        self.ipLabel.setMaximumSize(QSize(16777215, 30))
        self.ipLabel.setFont(font)
        self.ipLabel.setStyleSheet("color: rgba(255, 255, 255, 200);")
        self.ipLabel.setAlignment(Qt.AlignCenter)
        self.ipLabel.setObjectName("ipLabel")
        self.net_frameLayout.addWidget(self.ipLabel, 4, 0, 1, 3)
        self.label = QLabel(self.net_frame)
        self.label.setMinimumSize(QSize(0, 30))
        self.label.setFont(font)
        self.label.setStyleSheet("color: rgb(85, 255, 127);")
        self.label.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.label.setText("Відвантаження")
        self.net_frameLayout.addWidget(self.label, 2, 0, 1, 1)
        self.label_2 = QLabel(self.net_frame)
        self.label_2.setMinimumSize(QSize(0, 30))
        self.label_2.setFont(font)
        self.label_2.setStyleSheet("color: rgba(170, 170, 255, 255);")
        self.label_2.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.label_2.setText("Завантаження")
        self.net_frameLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.dnLabel = QLabel(self.net_frame)
        self.dnLabel.setMinimumSize(QSize(0, 30))
        self.dnLabel.setFont(font)
        self.dnLabel.setStyleSheet("color: rgba(170, 170, 255, 255);")
        self.dnLabel.setAlignment(Qt.AlignCenter)
        self.dnLabel.setObjectName("dnLabel")
        self.net_frameLayout.addWidget(self.dnLabel, 1, 2, 1, 1)
        self.setLayout(self.net_frameLayout)

    def netStat(self):
        io_2 = psutil.net_io_counters(pernic=True)
        iface = self.config['network']['interface']
        iface_io = self.io[iface]
        upload_speed, download_speed = io_2[iface].bytes_sent - iface_io.bytes_sent, \
            io_2[iface].bytes_recv - iface_io.bytes_recv
        self.interfaceLabel.setText("інтерфейс: " + iface)
        self.upLabel.setText(f"{get_size(upload_speed / self.config['intervals']['net_interval_ms'])}/s")
        self.dnLabel.setText(f"{get_size(download_speed / self.config['intervals']['net_interval_ms'])}/s")
        self.io = io_2