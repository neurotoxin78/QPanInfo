import gc
import sys
from datetime import datetime

import psutil
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (QDesktopWidget, QMainWindow, QLabel, QMenu,  QGraphicsDropShadowEffect)
from pulsectl import Pulse
from rich.console import Console

from tools import get_ip, extended_exception_hook, get_cputemp, get_config, get_size
from widgets import Launcher

con = Console()


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        # Load the UI Page
        self.config = get_config()
        uic.loadUi('widget_form.ui', self)
        self.setWindowTitle("Blackout PC Launcher")
        self.setWindowFlags(Qt.FramelessWindowHint
                            | Qt.Tool | Qt.WindowStaysOnBottomHint
                            )
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        #self.ipLabel = QLabel("Label: ")
        self.systimer = QTimer()
        self.clocktimer = QTimer()
        self.sensortimer = QTimer()
        self.temptimer = QTimer()
        self.ipchecktimer = QTimer()
        self.nettimer = QTimer()
        self.volume_dial_set()
        self.volume_dial.valueChanged.connect(self.volume_change)
        self.io = psutil.net_io_counters(pernic=True)
        self.launcher = Launcher()
        self.initUI()

    def initUI(self):
        # creating a QGraphicsDropShadowEffect object
        shadow = QGraphicsDropShadowEffect()
        # setting blur radius
        shadow.setBlurRadius(15)
        self.time_Label.setGraphicsEffect(shadow)
        # Timers
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
        self.ipLabel.setText("Network not connected!")

    def launch(self, data):
        print(data)

    def app_click(self):
        monitor = QDesktopWidget().screenGeometry(self.config['display']['output_display'])
        self.launcher.move(monitor.left(), monitor.top())

        self.launcher.show()

    def systemProcess(self):
        gc.collect()
        self.statusBar.showMessage("Freeing memory...", 1000)

    def volume_dial_set(self):
        try:
            with Pulse('volume-get-value') as pulse:
                sink_input = pulse.sink_input_list()[0]  # first random sink-input stream
                volume = sink_input.volume
                volume_value = int(volume.value_flat * 100)  # average level across channels (float)
            self.volume_dial.setValue(volume_value)
            self.volume_label.setText("Volume " + str(int(volume_value)) + '%')
        except:
            pass

    def volume_change(self):
        volume_value = self.volume_dial.value() / 100
        # print(volume_val)
        try:
            with Pulse('volume-changer') as pulse:
                sink_input = pulse.sink_input_list()[0]  # first random sink-input stream
                volume = sink_input.volume
                volume.value_flat = volume_value  # sets all volume.values to 0.3
                pulse.volume_set(sink_input, volume)  # applies the change
                self.volume_label.setText("Volume " + str(int(volume_value * 100)) + '%')
        except:
            pass


    def CheckIP(self):
        self.ipLabel.setText('IP: ' + get_ip())

    def Clock(self):
        now = datetime.now()
        current_time = now.strftime(self.config['format']['time_format'])
        self.time_Label.setText(current_time)  # u'\u2770' + + u'\u2771'

    def sysStat(self):
        self.ramBar.setValue(int(psutil.virtual_memory().percent))
        self.cpuBar.setMaximum(100)
        self.cpuBar.setValue(int(psutil.cpu_percent()))


    def tempStat(self):
        temp = get_cputemp(self.config['cpu_temp']['cpu_temp_sensor_path'])
        self.tempBar.setMaximum(100 * 100)
        self.tempBar.setValue(int(temp) * 100)
        self.tempBar.setFormat("%.01f °C" % temp)


    def netStat(self):
        io_2 = psutil.net_io_counters(pernic=True)
        iface = self.config['network']['interface']
        iface_io = self.io[iface]
        upload_speed, download_speed = io_2[iface].bytes_sent - iface_io.bytes_sent, \
            io_2[iface].bytes_recv - iface_io.bytes_recv
        self.interfaceLabel.setText("Interface: " + iface)
        self.upLabel.setText(f"{get_size(upload_speed / self.config['intervals']['net_interval_ms'])}/s")
        self.dnLabel.setText(f"{get_size(download_speed / self.config['intervals']['net_interval_ms'])}/s")
        self.io = io_2


def main():
    config = get_config()
    sys._excepthook = sys.excepthook
    sys.excepthook = extended_exception_hook
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    monitor = QDesktopWidget().screenGeometry(config['display']['output_display'])
    main_window.move(monitor.left(), monitor.top())
    main_window.showFullScreen()
    main_window.show()
    sys.exit(app.exec())


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
