import sys
from datetime import datetime

import psutil
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (QDesktopWidget, QMainWindow, QLabel)
from PyQt5.QtGui import QStandardItemModel
from pulsectl import Pulse
from rich.console import Console

from tools import get_ip, extended_exception_hook, get_cputemp, get_config, get_size
from widgets import VLine

con = Console()


class MainWindow(QMainWindow):
    P_PID, P_NAME, P_CPU, P_MEM = range(4)
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        # Load the UI Page
        self.config = get_config()
        uic.loadUi('widget_form.ui', self)
        self.setWindowTitle("Power Consumption")
        self.setWindowFlags(Qt.FramelessWindowHint
                            | Qt.Tool
                            )
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.ipLabel = QLabel("Label: ")
        self.clocktimer = QTimer()
        self.sensortimer = QTimer()
        self.temptimer = QTimer()
        self.ipchecktimer = QTimer()
        self.nettimer = QTimer()
        self.volume_dial_set()
        self.volume_dial.valueChanged.connect(self.volume_change)
        self.io = psutil.net_io_counters(pernic=True)
        self.initUI()

    def initUI(self):
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
        self.statusBar.addPermanentWidget(VLine())  # <---
        self.statusBar.addPermanentWidget(self.ipLabel)
        self.ipLabel.setText("Network not connected!")


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
        self.ipLabel.setText(get_ip())

    def Clock(self):
        now = datetime.now()
        current_time = now.strftime(self.config['format']['time_format'])
        self.time_Label.setText(current_time)  # u'\u2770' + + u'\u2771'

    def sysStat(self):
        # dict(psutil.virtual_memory()._asdict())
        # psutil.virtual_memory().available * 100 / psutil.virtual_memory().total
        self.ramBar.setValue(int(psutil.virtual_memory().percent))
        # cpu string
        self.cpuBar.setMaximum(100)
        self.cpuBar.setValue(int(psutil.cpu_percent()))
        # self.cpu_progressBar.setFormat("%.1f %%" % psutil.cpu_percent())
        # cpu temp

    def tempStat(self):
        temp = get_cputemp(self.config['cpu_temp']['cpu_temp_sensor_path'])
        self.tempBar.setMaximum(100 * 100)
        self.tempBar.setValue(int(temp) * 100)
        self.tempBar.setFormat("%.01f °C" % temp)
        # gc.collect()

    def netStat(self):
        io_2 = psutil.net_io_counters(pernic=True)
        # initialize the data to gather (a list of dicts)
        data = []
        for iface, iface_io in self.io.items():
            # new - old stats gets us the speed
            upload_speed, download_speed = io_2[iface].bytes_sent - iface_io.bytes_sent, io_2[
                iface].bytes_recv - iface_io.bytes_recv
            data.append({
                "iface": iface, "Download": get_size(io_2[iface].bytes_recv),
                "Upload": get_size(io_2[iface].bytes_sent),
                "Upload Speed": f"{get_size(upload_speed / self.config['intervals']['net_interval_ms'])}/s",
                "Download Speed": f"{get_size(download_speed / self.config['intervals']['net_interval_ms'])}/s",
            })

        # update the I/O stats for the next iteration
        ife = data[self.config['network']['interface_num']]
        self.interfaceLabel.setText("Interface: " + ife['iface'])
        self.upLabel.setText(ife['Upload Speed'])
        self.dnLabel.setText(ife['Download Speed'])
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
