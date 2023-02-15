import requests
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtWidgets import (QWidget, QPushButton, QGridLayout, QLabel, QGraphicsDropShadowEffect)
from tools import get_config, loadStylesheet


class Weather(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        stylesheet = "weather.qss"
        self.setStyleSheet(loadStylesheet(stylesheet))
        self.config = get_config()
        self.weathertimer = QTimer()
        self.weathertimer.timeout.connect(self.refresh)
        we_refresh = (int(self.config['intervals']['weather_fefresh_min']) * 1024) * 60
        self.weathertimer.start(we_refresh)
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.we_condition = QPushButton()
        self.we_condition.setStyleSheet("QPushButton { background-color: transparent }")
        self.we_condition.setFlat(True)
        self.we_condition_description = QLabel()
        self.temp_img = QLabel()
        self.humi_img = QLabel()
        self.pres_img = QLabel()
        self.current_temperature = QLabel()
        self.current_humidity = QLabel()
        self.current_pressure = QLabel()
        self.temp_img.setPixmap(QPixmap('images/temperature-32.png'))
        self.humi_img.setPixmap(QPixmap('images/humidity-32.png'))
        self.pres_img.setPixmap(QPixmap('images/pressure-32.png'))
        self.setupUI()

    def setupUI(self):
        self.layout.addWidget(self.we_condition, 0, 5, 1, 1, Qt.AlignCenter)
        self.we_condition.setIconSize(QSize(96, 96))
        self.we_condition.clicked.connect(self.refresh)
        self.layout.addWidget(self.temp_img, 1, 0)
        self.layout.addWidget(self.current_temperature, 1, 1)
        self.layout.addWidget(self.humi_img, 1, 2)
        self.layout.addWidget(self.current_humidity, 1, 3)
        self.layout.addWidget(self.pres_img, 1, 4)
        self.layout.addWidget(self.current_pressure, 1, 5)
        self.layout.addWidget(self.we_condition_description, 0, 2, 1, 3, Qt.AlignCenter)
        self.we_condition_description.setFont(QFont('Noto Sans', 24))
        self.we_condition_description.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        self.we_condition_description.setGeometry(0, 0, 20, 150)
        self.current_temperature.setFont(QFont('Noto Sans', 26))
        self.current_humidity.setFont(QFont('Noto Sans', 26))
        self.current_pressure.setFont(QFont('Noto Sans', 26))
        self.current_temperature.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        self.current_humidity.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        self.current_pressure.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        self.shadowize(blurradius=20)
        self.colorize()

    def shadowize(self, blurradius=10):
        shadow1 = QGraphicsDropShadowEffect()
        shadow1.setBlurRadius(blurradius)
        shadow2 = QGraphicsDropShadowEffect()
        shadow2.setBlurRadius(blurradius)
        shadow3 = QGraphicsDropShadowEffect()
        shadow3.setBlurRadius(blurradius)
        shadow4 = QGraphicsDropShadowEffect()
        shadow4.setBlurRadius(blurradius)
        shadow5 = QGraphicsDropShadowEffect()
        shadow5.setBlurRadius(blurradius)
        shadow6 = QGraphicsDropShadowEffect()
        shadow6.setBlurRadius(blurradius)
        shadow7 = QGraphicsDropShadowEffect()
        shadow7.setBlurRadius(blurradius)
        shadow8 = QGraphicsDropShadowEffect()
        shadow8.setBlurRadius(blurradius)
        self.we_condition_description.setGraphicsEffect(shadow8)
        self.current_temperature.setGraphicsEffect(shadow1)
        self.current_humidity.setGraphicsEffect(shadow2)
        self.current_pressure.setGraphicsEffect(shadow3)
        self.we_condition.setGraphicsEffect(shadow4)
        self.temp_img.setGraphicsEffect(shadow5)
        self.humi_img.setGraphicsEffect(shadow6)
        self.pres_img.setGraphicsEffect(shadow7)

    def colorize(self):
        self.current_temperature.setStyleSheet("color: " + self.config['colors']['we_temperature_color'] + ";")
        self.current_humidity.setStyleSheet("color: " + self.config['colors']['we_humidity_color'] + ";")
        self.current_pressure.setStyleSheet("color: " + self.config['colors']['we_pressure_color'] + ";")
        self.we_condition_description.setStyleSheet("color: " + self.config['colors']['we_condition_color'] + ";")
    def refresh(self):
        try:
            self.get_weather()
        except:
            pass

    def get_weather(self):
        api_key = self.config['weather']['api_key']
        base_url = self.config['weather']['url']
        city_name = self.config['weather']['city']
        complete_url = base_url + "appid=" + api_key + "&q=" + city_name + "&lang=UA"
        print(complete_url)
        response = requests.get(complete_url)
        x = response.json()
        if x["cod"] != "404":
            y = x["main"]
            current_temperature = y["temp"]
            current_pressure = y["pressure"]
            current_humidity = y["humidity"]
            z = x["weather"]
            weather_description = z[0]["description"]
            weather_code = z[0]["id"]
            print(weather_description)
            self.we_condition_description.setText(weather_description)
            self.current_temperature.setText("<b>" + str(current_temperature) + ' <sup>°C</sup></b>  ')
            self.current_humidity.setText("<b>" + str(current_humidity) + ' <sup>%</sup><</b>  ')
            self.current_pressure.setText("<b>" + str(current_pressure) + ' <sup>hPa</sup><</b>  ')
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