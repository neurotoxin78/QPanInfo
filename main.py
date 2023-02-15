import gc
import sys
from datetime import datetime

import psutil
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt, QTimer, QProcess
from PyQt5.QtWidgets import (QDesktopWidget, QMainWindow, QGraphicsDropShadowEffect)
from pulsectl import Pulse
from rich.console import Console

from tools import get_ip, extended_exception_hook, get_cputemp, get_config, get_size, loadStylesheet
from widgets.launcher import Launcher
from widgets.systemload import SystemLoad
from widgets.weather import Weather
from widgets.networkload import NetworkLoad
from widgets.volume import VolumeControl
from widgets.clock import Clock

con = Console()


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        # Load the UI Page
        self.config = get_config()
        uic.loadUi('main_form.ui', self)
        self.setWindowTitle("Blackout PC Launcher")
        self.setWindowFlags(Qt.FramelessWindowHint
                            | Qt.Tool | Qt.WindowStaysOnBottomHint
                            )
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.process = QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
        self.weathertimer = QTimer()
        self.systimer = QTimer()
        self.clocktimer = QTimer()
        self.sensortimer = QTimer()
        self.temptimer = QTimer()
        self.ipchecktimer = QTimer()
        self.nettimer = QTimer()
        self.io = psutil.net_io_counters(pernic=True)
        self.top_frame.setStyleSheet(loadStylesheet("systemload.qss"))
        self.middle_frame.setStyleSheet(loadStylesheet("systemload.qss"))
        self.bottom_frame.setStyleSheet(loadStylesheet("systemload.qss"))
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
        self.volume_dial_set()
        self.volumeControl.volume_dial.valueChanged.connect(self.volume_change)

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

    def initUI(self):
        stylesheet = "widget_form.qss"
        self.setStyleSheet(loadStylesheet(stylesheet))
        # creating a QGraphicsDropShadowEffect object
        shadow = QGraphicsDropShadowEffect()
        # setting blur radius
        shadow.setBlurRadius(15)
        self.clock.time_Label.setGraphicsEffect(shadow)
        # Timers
        self.weathertimer.timeout.connect(self.weatherRefresh)
        we_refresh = (int(self.config['intervals']['weather_fefresh_min']) * 1024) * 60
        self.weathertimer.start(we_refresh)
        self.systimer.timeout.connect(self.systemProcess)
        self.systimer.start(self.config['intervals']['sys_proc_refresh_ms'])
        self.sensortimer.timeout.connect(self.sysStat)
        self.sensortimer.start(self.config['intervals']['sensor_refresh_ms'])
        self.clocktimer.timeout.connect(self.Clock)
        self.clocktimer.start(self.config['intervals']['clock_refresh_ms'])
        self.ipchecktimer.timeout.connect(self.CheckIP)
        self.ipchecktimer.start(self.config['intervals']['network_refresh_ms'])
        self.temptimer.timeout.connect(self.tempStat)
        self.temptimer.start(self.config['intervals']['cpu_temp_refresh_ms'])
        self.nettimer.timeout.connect(self.netStat)
        self.nettimer.start(self.config['intervals']['net_interval_ms'])
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

    def weatherRefresh(self):
        try:
            self.weather.get_weather()
            self.statusBar.showMessage("Weather data refreshed", 1500)
        except:
            self.statusBar.showMessage("Weather: ERROR", 1500)


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

    def volume_dial_set(self):
        try:
            with Pulse('volume-get-value') as pulse:
                sink_input = pulse.sink_input_list()[0]  # first random sink-input stream
                volume = sink_input.volume
                volume_value = int(volume.value_flat * 100)  # average level across channels (float)
            self.volumeControl.volume_dial.setValue(volume_value)
            self.volumeControl.volume_label.setText(str(int(volume_value)) + '%')
        except:
            pass

    def volume_change(self):
        volume_value = self.volumeControl.volume_dial.value() / 100
        # print(volume_val)
        try:
            with Pulse('volume-changer') as pulse:
                sink_input = pulse.sink_input_list()[0]  # first random sink-input stream
                volume = sink_input.volume
                volume.value_flat = volume_value  # sets all volume.values to 0.3
                pulse.volume_set(sink_input, volume)  # applies the change
                self.volumeControl.volume_label.setText(str(int(volume_value * 100)) + '%')
        except:
            pass


    def CheckIP(self):
        self.networkLoad.ipLabel.setText('IP: ' + get_ip())

    def Clock(self):
        now = datetime.now()
        current_time = now.strftime(self.config['format']['time_format'])
        self.clock.time_Label.setText(current_time)  # u'\u2770' + + u'\u2771'

    def sysStat(self):
        self.systemLoad.ramBar.setValue(int(psutil.virtual_memory().percent))
        self.systemLoad.cpuBar.setMaximum(100)
        self.systemLoad.cpuBar.setValue(int(psutil.cpu_percent()))


    def tempStat(self):
        temp = get_cputemp(self.config['cpu_temp']['cpu_temp_sensor_path'])
        self.systemLoad.tempBar.setMaximum(100 * 100)
        self.systemLoad.tempBar.setValue(int(temp) * 100)
        self.systemLoad.tempBar.setFormat("%.01f °C" % temp)


    def netStat(self):
        io_2 = psutil.net_io_counters(pernic=True)
        iface = self.config['network']['interface']
        iface_io = self.io[iface]
        upload_speed, download_speed = io_2[iface].bytes_sent - iface_io.bytes_sent, \
            io_2[iface].bytes_recv - iface_io.bytes_recv
        self.networkLoad.interfaceLabel.setText("інтерфейс: " + iface)
        self.networkLoad.upLabel.setText(f"{get_size(upload_speed / self.config['intervals']['net_interval_ms'])}/s")
        self.networkLoad.dnLabel.setText(f"{get_size(download_speed / self.config['intervals']['net_interval_ms'])}/s")
        self.io = io_2


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
