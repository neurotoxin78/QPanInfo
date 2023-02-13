from PyQt5 import uic
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import (QFrame, QWidget, QCompleter, QPushButton, QGridLayout,
                             QLabel)

import requests, json

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
        self.setLayout(self.layout)
        self.we_condition = QPushButton()
        self.we_condition.setStyleSheet("QPushButton { background-color: transparent }")
        self.we_condition.setFlat(True)
        self.current_temperature = QLabel()
        self.current_humidity = QLabel()
        self.current_pressure = QLabel()
        self.setupUI()
        self.current_temperature.setText("25 °C")
        self.current_humidity.setText("42 %")
        self.current_pressure.setText("1000 hP")

    def setupUI(self):
        stylesheet = "weather.qss"
        self.layout.addWidget(self.we_condition, 0, 0)
        #self.we_condition.setGeometry(0, 0, 100, 100)
        self.we_condition.setIcon(QIcon.fromTheme("weather-clear-night"))
        self.we_condition.setIconSize(QSize(96, 96))
        self.we_condition.clicked.connect(self.refresh)
        self.layout.addWidget(self.current_temperature, 0, 1)
        self.layout.addWidget(self.current_humidity, 0, 2)
        self.layout.addWidget(self.current_pressure, 0, 3)
        self.layout.setRowStretch(1, 0)
        self.current_temperature.setFont(QFont('Noto Sans', 18))
        self.current_humidity.setFont(QFont('Noto Sans', 18))
        self.current_pressure.setFont(QFont('Noto Sans', 18))
        self.loadStylesheet(stylesheet)

    def loadStylesheet(self, sshFile):
        with open(sshFile, "r") as fh:
            self.setStyleSheet(fh.read())
    def refresh(self):
        print("Refresh")

    def get_weather(self, city : str):
        api_key = "e7a63eca33717887514a746f7ab259f6"

        # base_url variable to store url
        base_url = "http://api.openweathermap.org/data/2.5/weather?units=metric&"

        # Give city name
        city_name = city

        complete_url = base_url + "appid=" + api_key + "&q=" + city_name

        response = requests.get(complete_url)
        x = response.json()
        if x["cod"] != "404":

            # store the value of "main"
            # key in variable y
            y = x["main"]

            # store the value corresponding
            # to the "temp" key of y
            current_temperature = y["temp"]

            # store the value corresponding
            # to the "pressure" key of y
            current_pressure = y["pressure"]

            # store the value corresponding
            # to the "humidity" key of y
            current_humidity = y["humidity"]

            # store the value of "weather"
            # key in variable z
            z = x["weather"]

            # store the value corresponding
            # to the "description" key at
            # the 0th index of z
            weather_description = z[0]["description"]

            self.current_temperature.setText(str(current_temperature) + ' °C')
            self.current_humidity.setText(str(current_humidity) + ' %')
            self.current_pressure.setText(str(current_pressure) + 'hPa')


        else:
            print(" City Not Found ")