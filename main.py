import gc
import sys

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt, QTimer, QProcess
from PyQt5.QtWidgets import (QDesktopWidget, QMainWindow, QGraphicsDropShadowEffect)
from rich.console import Console

from tools import get_ip, extended_exception_hook, get_config, loadStylesheet
from widgets.clock import Clock
from widgets.launcher import Launcher
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
        self.setWindowFlags(Qt.FramelessWindowHint
                            | Qt.Tool | Qt.WindowStaysOnBottomHint
                            )
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.process = QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
        self.systimer = QTimer()
        self.ipchecktimer = QTimer()


        self.top_frame.setStyleSheet(loadStylesheet("stylesheets/systemload.qss"))
        self.middle_frame.setStyleSheet(loadStylesheet("stylesheets/systemload.qss"))
        self.bottom_frame.setStyleSheet(loadStylesheet("stylesheets/systemload.qss"))
        self.launcher = Launcher()
        self.weather = Weather()
        self.systemLoad = SystemLoad()
        self.networkLoad = NetworkLoad()
        self.volumeControl = VolumeControl()
        self.clock = Clock()
        self.l_middle_frameLayout.addWidget(self.clock, 0, 0)
        self.top_frameLayout.addWidget(self.systemLoad, 0, 0)
        self.middle_frameLayout.addWidget(self.networkLoad, 0, 0)
        self.bottom_frameLayout.addWidget(self.volumeControl, 0, 0)
        #self.right_frame.setStyleSheet("border: 1px solid green; border-radius: 20px;")
        self.initUI()
        self.shadowize(blurradius=50)
        self.systemProcess()

    def initUI(self):
        stylesheet = "stylesheets/panel.qss"
        self.setStyleSheet(loadStylesheet(stylesheet))
        self.systimer.timeout.connect(self.systemProcess)
        self.systimer.start(self.config['intervals']['sys_proc_refresh_ms'])
        self.ipchecktimer.timeout.connect(self.CheckIP)
        self.ipchecktimer.start(self.config['intervals']['network_refresh_ms'])
        self.appBtn.clicked.connect(self.app_click)
        self.networkLoad.ipLabel.setText("Мережа не підключена")
        self.launcher.lineEdit.returnPressed.connect(lambda: self.AppLaunch(self.launcher.lineEdit.text()))
        self.launcher.launchBtn.clicked.connect(lambda: self.AppLaunch(self.launcher.lineEdit.text()))
        self.weather_frameLayout.addWidget(self.weather)
        try:
            #pass
            self.weather.get_weather()
        except:
            pass

    def shadowize(self, blurradius=10):
        self.blurRadius = blurradius
        shadow_top = QGraphicsDropShadowEffect()
        shadow_top.setBlurRadius(self.blurRadius)
        shadow_middle = QGraphicsDropShadowEffect()
        shadow_middle.setBlurRadius(self.blurRadius)
        shadow_bottom = QGraphicsDropShadowEffect()
        shadow_bottom.setBlurRadius(self.blurRadius)
        self.top_frame.setGraphicsEffect(shadow_top)
        self.middle_frame.setGraphicsEffect(shadow_middle)
        self.bottom_frame.setGraphicsEffect(shadow_bottom)

    def AppLaunch(self, command : str):
        raw_cmd = command.split(sep=" ")
        cmd = raw_cmd[0]
        keys = raw_cmd[1:]
        self.process.start(cmd, keys)
        self.process.started.connect(lambda: self.statusBar.showMessage("Виконано", 1500))
        self.process.finished.connect(lambda: self.statusBar.showMessage("Закрито", 1500))
        self.process.error.connect(lambda: self.statusBar.showMessage("Не виконано", 1500))
        self.launcher.hide()


    def launch(self, data):
        print(data)

    def app_click(self):
        monitor = QDesktopWidget().screenGeometry(self.config['display']['output_display'])
        self.launcher.move(monitor.left(), monitor.top())

        self.launcher.show()

    def systemProcess(self):
        gc.collect()
        self.statusBar.showMessage("Вивільнення пам'яті...", self.config['intervals']['statusbar_msg_time_ms'])


    def CheckIP(self):
        self.networkLoad.ipLabel.setText('IP: ' + get_ip())


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
