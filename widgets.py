import requests
from PyQt5 import uic
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import (QFrame, QWidget, QCompleter, QPushButton, QGridLayout,
                             QLabel, QGraphicsDropShadowEffect)

from tools import get_config


class VLine(QFrame):
    # a simple VLine, like the one you get from designer
    def __init__(self):
        super(VLine, self).__init__()
        self.setFrameShape(self.VLine | self.Sunken)

class Launcher(QWidget):
    def __init__(self, *args, **kwargs):
        super(Launcher, self).__init__(*args, **kwargs)
        # Load the UI Page
        self.config = get_config()
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
        self.config = get_config()
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.we_condition = QPushButton()
        self.we_condition.setStyleSheet("QPushButton { background-color: transparent }")
        self.we_condition.setFlat(True)
        self.we_condition_description = QLabel()
        self.current_temperature = QLabel()
        self.current_humidity = QLabel()
        self.current_pressure = QLabel()
        self.setupUI()

    def setupUI(self):
        stylesheet = "weather.qss"
        shadow1 = QGraphicsDropShadowEffect()
        shadow1.setBlurRadius(10)
        shadow2 = QGraphicsDropShadowEffect()
        shadow2.setBlurRadius(10)
        shadow3 = QGraphicsDropShadowEffect()
        shadow3.setBlurRadius(10)
        shadow4 = QGraphicsDropShadowEffect()
        shadow4.setBlurRadius(10)
        self.layout.addWidget(self.we_condition, 0, 0)
        self.we_condition.setIconSize(QSize(96, 96))
        self.we_condition.setGraphicsEffect(shadow4)
        self.we_condition.clicked.connect(self.refresh)
        self.layout.addWidget(self.current_temperature, 1, 0)
        self.layout.addWidget(self.current_humidity, 1, 1)
        self.layout.addWidget(self.current_pressure, 1, 2)
        self.layout.addWidget(self.we_condition_description, 0, 1)
        self.layout.setRowStretch(1, 0)
        self.we_condition_description.setFont(QFont('Noto Sans', 20))
        self.we_condition_description.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        self.we_condition_description.setGeometry(0, 0, 40, 100)
        self.current_temperature.setFont(QFont('Noto Sans', 24))
        self.current_humidity.setFont(QFont('Noto Sans', 24))
        self.current_pressure.setFont(QFont('Noto Sans', 24))
        self.current_temperature.setAlignment(Qt.AlignCenter)
        self.current_humidity.setAlignment(Qt.AlignCenter)
        self.current_pressure.setAlignment(Qt.AlignCenter)
        self.current_temperature.setGraphicsEffect(shadow1)
        self.current_humidity.setGraphicsEffect(shadow2)
        self.current_pressure.setGraphicsEffect(shadow3)
        self.loadStylesheet(stylesheet)

    def loadStylesheet(self, sshFile):
        with open(sshFile, "r") as fh:
            self.setStyleSheet(fh.read())
    def refresh(self):
        try:
            self.get_weather()
        except:
            pass

    def get_weather(self):
        api_key = self.config['weather']['api_key']

        # base_url variable to store url
        base_url = self.config['weather']['url']

        # Give city name
        city_name = self.config['weather']['city']

        complete_url = base_url + "appid=" + api_key + "&q=" + city_name + "&lang=UA"
        print(complete_url)

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
            weather_code = z[0]["id"]
            print(weather_description)
            self.we_condition_description.setText(weather_description)
            self.current_temperature.setText("<b>" + str(current_temperature) + ' <sup>°C</sup></b>')
            self.current_humidity.setText("<b>" + str(current_humidity) + ' <sup>%</sup><</b>')
            self.current_pressure.setText("<b>" + str(current_pressure) + ' <sup>hPa</sup><</b>')
            self.set_we_description(weather_code)


        else:
            print(" City Not Found ")


    def set_we_description(self, code):
        match code:
            case num if num in range(200, 233):
                self.we_condition.setIcon(QIcon.fromTheme("weather-storm"))

            case num if num in range(300, 322):
                self.we_condition.setIcon(QIcon.fromTheme("weather-severe-alert"))

            case num if num in range(500, 532):
                self.we_condition.setIcon(QIcon.fromTheme("weather-showers-scattered"))

            case num if num in range(600, 623):
                self.we_condition.setIcon(QIcon.fromTheme("weather-snow"))

            case num if num in range(700, 782):
                self.we_condition.setIcon(QIcon.fromTheme("weather-fog"))

            case 800:
                self.we_condition.setIcon(QIcon.fromTheme("weather-clear"))

            case num if num in range(801, 805):
                self.we_condition.setIcon(QIcon.fromTheme("weather-overcast"))

            case _:
                print(code)
