import gc
import sys

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtWidgets import (QDesktopWidget, QMainWindow)
from rich.console import Console

from tools import extended_exception_hook, get_config, loadStylesheet, setShadow
from widgets.clock import Clock
from widgets.launcher import LaunchButton
from widgets.mpdcontrol import MPDControl
from widgets.networkload import NetworkLoad
from widgets.systemload import SystemLoad
from widgets.volume import VolumeControl
from widgets.weather import Weather
from widgets.chatgpt import GPTChat

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
        self.systimer.timeout.connect(self.systemProcess)
        self.systimer.start(self.config['intervals']['sys_proc_refresh_ms'])
        self.top_frame.setStyleSheet(loadStylesheet("stylesheets/systemload.qss"))
        self.middle_frame.setStyleSheet(loadStylesheet("stylesheets/networkload.qss"))
        self.bottom_frame.setStyleSheet(loadStylesheet("stylesheets/volumecontrol.qss"))
        self.r_top_frame.setStyleSheet(loadStylesheet("stylesheets/weather.qss"))
        self.weather = Weather(self)
        self.systemLoad = SystemLoad()
        self.networkLoad = NetworkLoad()
        self.volumeControl = VolumeControl()
        self.clock = Clock()
        self.mediaControl = MPDControl()
        self.launchButton = LaunchButton(self)
        self.ChatBox = GPTChat(self)
        self.l_middle_frameLayout.addWidget(self.clock, 0, 0)
        self.top_frameLayout.addWidget(self.systemLoad, 0, 0)
        self.middle_frameLayout.addWidget(self.networkLoad, 0, 0)
        self.bottom_frameLayout.addWidget(self.volumeControl, 0, 0)
        self.l_bottom_frameLayout.addWidget(self.ChatBox, 1, 0)
        self.l_bottom_frameLayout.addWidget(self.launchButton, 0, 0, 1, 1)
        self.r_top_frameLayout.addWidget(self.weather, 0, 0, 1, 1, Qt.AlignHCenter)
        #self.r_top_frame.setMaximumSize(QSize(600, 160))
        self.initUI()
        self.systemProcess()
        self.middle_frame.setMaximumSize(QSize(0, 175))
        try:
            #pass
            self.weather.get_weather()
        except:
            pass
        #self.humorBox.refresh()


    def initUI(self):
        stylesheet = "stylesheets/panel.qss"
        self.setStyleSheet(loadStylesheet(stylesheet))
        self.networkLoad.ipLabel.setText("Мережа не підключена")
        # Decorations
        setShadow(self.top_frame, 20)
        setShadow(self.middle_frame, 20)
        setShadow(self.r_top_frame, 20)
        setShadow(self.bottom_frame, 20)


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
