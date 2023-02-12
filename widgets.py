from PyQt5.QtWidgets import (QFrame, QWidget, QCompleter, QPushButton, QGridLayout,
                             QLabel)
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSlot

class VLine(QFrame):
    # a simple VLine, like the one you get from designer
    def __init__(self):
        super(VLine, self).__init__()
        self.setFrameShape(self.VLine | self.Sunken)

class Launcher(QWidget):
    def __init__(self, *args, **kwargs):
        super(Launcher, self).__init__(*args, **kwargs)
        # Load the UI Page
        uic.loadUi('launcher.ui', self)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint) # | Qt.WindowModal)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.hideBtn.clicked.connect(self.on_click)
        names = ["qterminal", "calc", "firefox", "smplayer"]
        self.completer = QCompleter(names)
        self.lineEdit.setCompleter(self.completer)

    @pyqtSlot()
    def on_click(self):
        self.hide()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            print("Enter")


class Weather(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QGridLayout()
        self.we_condition = QPushButton()
        self.current_temperature = QLabel()
        self.current_humidity = QLabel()
        self.layout.addWidget(self.we_condition)
        self.layout.addWidget(self.current_temperature)
        self.layout.addWidget(self.current_humidity)
        self.current_temperature.setText("0 °C")
        self.current_humidity.setText("0 %")
        self.setLayout(self.layout)