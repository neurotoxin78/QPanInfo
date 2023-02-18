import gc
import sys

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (QDesktopWidget, QMainWindow, QGraphicsDropShadowEffect)
from rich.console import Console

from tools import get_ip, extended_exception_hook, get_config, loadStylesheet
from widgets.clock import Clock
from widgets.launcher import LaunchButton
from widgets.mpdcontrol import MPDControl
from widgets.networkload import NetworkLoad
from widgets.systemload import SystemLoad
from widgets.volume import VolumeControl
from widgets.weather import Weather

con = Console()


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        # Load the UI Page
        self.config = get_config()
        uic.loadUi('ui/panel.ui', self)
        self.setWindowTitle("QPanInfo")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnBottomHint)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.systimer = QTimer()
        self.top_frame.setStyleSheet(loadStylesheet("stylesheets/systemload.qss"))
        self.middle_frame.setStyleSheet(loadStylesheet("stylesheets/networkload.qss"))
        self.bottom_frame.setStyleSheet(loadStylesheet("stylesheets/volumecontrol.qss"))
        self.weather_frame.setStyleSheet(loadStylesheet("stylesheets/weather.qss"))
        self.weather = Weather()
        self.systemLoad = SystemLoad()
        self.networkLoad = NetworkLoad()
        self.volumeControl = VolumeControl()
        self.clock = Clock()
        self.mediaControl = MPDControl()
        self.launchButton = LaunchButton()
        self.l_middle_frameLayout.addWidget(self.clock, 0, 0)
        self.top_frameLayout.addWidget(self.systemLoad, 0, 0)
        self.middle_frameLayout.addWidget(self.networkLoad, 0, 0)
        self.bottom_frameLayout.addWidget(self.volumeControl, 0, 0)
        self.l_bottom_frameLayout.addWidget(self.mediaControl, 0, 0, 1, 0)
        self.l_bottom_frameLayout.addWidget(self.launchButton, 1, 0, 1, 1)
        # self.right_frame.setStyleSheet("border: 1px solid green; border-radius: 20px;")
        self.initUI()
        self.systemProcess()
        try:
            #pass
            self.weather.get_weather()
        except:
            pass


    def initUI(self):
        stylesheet = "stylesheets/panel.qss"
        self.setStyleSheet(loadStylesheet(stylesheet))
        self.systimer.timeout.connect(self.systemProcess)
        self.systimer.start(self.config['intervals']['sys_proc_refresh_ms'])
        self.networkLoad.ipLabel.setText("Мережа не підключена")
        self.weather_frameLayout.addWidget(self.weather)
        self.shadowize(blurradius=50)


    def shadowize(self, blurradius=10):
        self.blurRadius = blurradius
        shadow_top = QGraphicsDropShadowEffect()
        shadow_top.setBlurRadius(self.blurRadius)
        shadow_middle = QGraphicsDropShadowEffect()
        shadow_middle.setBlurRadius(self.blurRadius)
        shadow_bottom = QGraphicsDropShadowEffect()
        shadow_bottom.setBlurRadius(self.blurRadius)
        shadow_weather = QGraphicsDropShadowEffect()
        shadow_weather.setBlurRadius(self.blurRadius)
        self.top_frame.setGraphicsEffect(shadow_top)
        self.middle_frame.setGraphicsEffect(shadow_middle)
        self.bottom_frame.setGraphicsEffect(shadow_bottom)
        self.weather_frame.setGraphicsEffect(shadow_weather)

    def systemProcess(self):
        gc.collect()
        self.statusBar.showMessage("Вивільнення пам'яті...", self.config['intervals']['statusbar_msg_time_ms'])


def main():
    config = get_config()
    sys._excepthook = sys.excepthook
    sys.excepthook = extended_exception_hook
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle(QtWidgets.QStyleFactory.create("fusion"))
    main_window = MainWindow()
    monitor = QDesktopWidget().screenGeometry(config['display']['output_display'])
    main_window.move(monitor.left(), monitor.top())
    main_window.showFullScreen()
    main_window.show()
    sys.exit(app.exec())


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
