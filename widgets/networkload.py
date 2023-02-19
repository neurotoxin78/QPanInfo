import psutil
from PyQt5.QtCore import Qt, QSize, QTimer, QRect
from PyQt5.QtGui import QFont, QBrush, QColor
from PyQt5.QtWidgets import (QFrame, QWidget, QGridLayout, QLabel)
from collections import deque
import pyqtgraph as pg
from pyqtgraph import PlotWidget
from tools import get_ip, get_config, get_size, loadStylesheet, setShadow


class NetworkLoad(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        stylesheet = "stylesheets/networkload.qss"
        self.setStyleSheet(loadStylesheet(stylesheet))
        self.config = get_config()
        self.io = psutil.net_io_counters(pernic=True)
        self.upload_graph_data = deque()
        self.download_graph_data = deque()
        self.graph_data_limit = 60
        self.nettimer = QTimer()
        self.nettimer.timeout.connect(self.netStat)
        self.nettimer.start(self.config['intervals']['net_interval_ms'])
        self.ipchecktimer = QTimer()
        self.ipchecktimer.timeout.connect(self.CheckIP)
        self.ipchecktimer.start(self.config['intervals']['network_refresh_ms'])
        self.net_frame = QFrame()
        self.net_frame.setMinimumSize(QSize(0, 100))
        self.net_frame.setMaximumSize(QSize(16777215, 140))
        self.net_frame.setFrameShape(QFrame.StyledPanel)
        self.net_frame.setFrameShadow(QFrame.Raised)
        self.net_frame.setObjectName("net_frame")
        self.net_frameLayout = QGridLayout(self.net_frame)
        self.net_frameLayout.setObjectName("net_frameLayout")
        self.interfaceLabel = QLabel(self.net_frame)
        self.interfaceLabel.setMinimumSize(QSize(0, 30))
        self.interfaceLabel.setMaximumSize(QSize(16777215, 30))
        font = QFont()
        font.setFamily("DejaVu Sans Mono for Powerline")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(100)
        font_ico = QFont()
        font_ico.setPointSize(20)
        font_ico.setBold(False)
        font_ico.setWeight(100)
        self.interfaceLabel.setFont(font)
        self.interfaceLabel.setStyleSheet("color: rgba(255, 255, 255, 200);")
        self.interfaceLabel.setAlignment(Qt.AlignCenter)
        self.interfaceLabel.setObjectName("interfaceLabel")
        self.interfaceLabel.setMinimumSize(QSize(120, 25))
        self.net_frameLayout.addWidget(self.interfaceLabel, 0, 0, 1, 3)
        # UPLOAD PLOT
        self.upload_plot = PlotWidget()
        self.upload_plot.setGeometry(QRect(0, 0, 10, 10))
        self.upload_plot.setStyleSheet("background-color: transparent; color: #FB9902;")
        self.upload_plot.setObjectName("upload_plot")
        background = QBrush()
        background.setColor(QColor(0x31363b))
        #l = pg.LegendItem((10, 10), offset=(60, 92))  # args are (size, offset)
        # l.setParentItem(self.network_plot.graphicsItem())   # Note we do NOT call plt.addItem in this case
        self.upload_plot.setBackground(background)
        # self.network_plot.addLegend()
        self.upload_plot.plotItem.showGrid(x=True, y=True, alpha=0.8)
        self.upload_plot.getPlotItem().addLegend()
        self.upload_plot.getPlotItem().enableAutoRange(axis='y', enable=True)
        self.upload_plot.getPlotItem().enableAutoRange(axis='x', enable=False)
        self.upload_plot.setLogMode(x=True, y=False)
        self.upload_curve = self.upload_plot.plot(
            pen=pg.mkPen('#009637', width=1, name="upload", symbolBrush=(0, 0, 200), symbolPen='w', symbol='o', symbolSize=14,
                         style=Qt.SolidLine))
        # l.addItem(self.curve, 'upload')
        self.upload_plot.getPlotItem().hideAxis('bottom')
        self.upload_plot.getPlotItem().hideAxis('left')
        # DOWNLOAD PLOT
        self.download_plot = PlotWidget()
        self.download_plot.setGeometry(QRect(0, 0, 10, 10))
        self.download_plot.setStyleSheet("background-color: transparent; color: #FB9902;")
        self.download_plot.setObjectName("upload_plot")
        background = QBrush()
        background.setColor(QColor(0x31363b))
        # l = pg.LegendItem((10, 10), offset=(60, 92))  # args are (size, offset)
        # l.setParentItem(self.network_plot.graphicsItem())   # Note we do NOT call plt.addItem in this case
        self.download_plot.setBackground(background)
        # self.network_plot.addLegend()
        self.download_plot.plotItem.showGrid(x=True, y=True, alpha=0.8)
        self.download_plot.getPlotItem().addLegend()
        self.download_plot.getPlotItem().enableAutoRange(axis='y', enable=True)
        self.download_plot.getPlotItem().enableAutoRange(axis='x', enable=False)
        self.download_plot.setLogMode(x=True, y=False)
        self.download_curve = self.download_plot.plot(
            pen=pg.mkPen('#009ceb', width=1, name="download", symbolBrush=(0, 0, 200), symbolPen='w', symbol='o',
                         symbolSize=14,
                         style=Qt.SolidLine))
        # l.addItem(self.curve, 'upload')
        self.download_plot.getPlotItem().hideAxis('bottom')
        self.download_plot.getPlotItem().hideAxis('left')
        # Add Plots to layout
        self.net_frameLayout.addWidget(self.upload_plot, 2, 0, 1, 1)
        self.net_frameLayout.addWidget(self.download_plot, 1, 0, 1, 1)
        # LABELS
        self.upLabel = QLabel(self.net_frame)
        self.upLabel.setMinimumSize(QSize(120, 25))
        self.upLabel.setFont(font)
        self.upLabel.setStyleSheet("color: rgba(101, 190, 0, 250);")
        self.upLabel.setAlignment(Qt.AlignLeft)
        self.upLabel.setObjectName("upLabel")
        self.net_frameLayout.addWidget(self.upLabel, 2, 0, 1, 1, Qt.AlignCenter)
        self.dnLabel = QLabel(self.net_frame)
        self.dnLabel.setMinimumSize(QSize(120, 25))
        self.dnLabel.setFont(font)
        self.dnLabel.setStyleSheet("color: rgba(83, 180, 255, 250);")
        self.dnLabel.setAlignment(Qt.AlignLeft)
        self.dnLabel.setObjectName("dnLabel")
        self.net_frameLayout.addWidget(self.dnLabel, 1, 0, 1, 1, Qt.AlignCenter)
        self.ipLabel = QLabel(self.net_frame)
        self.ipLabel.setMaximumSize(QSize(16777215, 30))
        self.ipLabel.setFont(font)
        self.ipLabel.setStyleSheet("color: rgba(255, 255, 255, 200);")
        self.ipLabel.setAlignment(Qt.AlignCenter)
        self.ipLabel.setObjectName("ipLabel")
        self.net_frameLayout.addWidget(self.ipLabel, 4, 0, 1, 3)
        self.setLayout(self.net_frameLayout)

        setShadow(self.dnLabel, 5)
        setShadow(self.upLabel, 5)
        setShadow(self.ipLabel, 5)
        setShadow(self.interfaceLabel, 5)
        self.CheckIP()

    def netStat(self):
        io_2 = psutil.net_io_counters(pernic=True)
        iface = self.config['network']['interface']
        iface_io = self.io[iface]
        upload_speed, download_speed = io_2[iface].bytes_sent - iface_io.bytes_sent, \
            io_2[iface].bytes_recv - iface_io.bytes_recv

        up_speed = upload_speed / self.config['intervals']['net_interval_ms']
        dn_speed = download_speed / self.config['intervals']['net_interval_ms']
        self.interfaceLabel.setText("інтерфейс: " + iface)
        self.upLabel.setText(f"\uf062 {get_size(up_speed)}/s")
        self.dnLabel.setText(f"\uf063 {get_size(dn_speed)}/s")

        if len(self.upload_graph_data) > self.graph_data_limit:
            self.upload_graph_data.popleft() #remove oldest

        self.upload_graph_data.append(upload_speed / self.config['intervals']['net_interval_ms'])
        self.upload_curve.setData(self.upload_graph_data)

        if len(self.download_graph_data) > self.graph_data_limit:
            self.download_graph_data.popleft() #remove oldest

        self.download_graph_data.append(download_speed / self.config['intervals']['net_interval_ms'])
        self.download_curve.setData(self.download_graph_data)

        self.io = io_2

    def CheckIP(self):
        self.ipLabel.setText('IP: ' + get_ip())
