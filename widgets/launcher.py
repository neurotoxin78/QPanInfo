from PyQt5 import uic
from PyQt5.QtCore import Qt, QSize, QProcess, pyqtSlot
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (QDesktopWidget, QWidget, QCompleter, QFrame, QGridLayout, QPushButton)
from widgets.virtual_keyboard import AlphaNeumericVirtualKeyboard
from tools import get_config, get_apps_list, setShadow


class LaunchButton(QWidget):
    def __init__(self, *args, **kwargs):
        super(LaunchButton, self).__init__(*args, **kwargs)
        # Load the UI Page
        self.MainPanel = args[0]
        self.config = get_config()
        self.launcher = Launcher()
        self.process = QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
        self.launch_frame = QFrame()
        self.launch_frame.setMinimumSize(QSize(20, 100))
        self.launch_frame.setMaximumSize(QSize(20, 140))
        self.launch_frame.setFrameShape(QFrame.StyledPanel)
        self.launch_frame.setFrameShadow(QFrame.Raised)
        self.launch_frame.setObjectName("launch_frame")
        self.launch_frame_frameLayout = QGridLayout(self.launch_frame)
        self.launch_frame_frameLayout.setObjectName("launch_frameLayout")
        font = QFont()
        font.setFamily("Roboto Mono for Powerline")
        font.setPointSize(20)
        font.setBold(False)
        font.setUnderline(False)
        font.setWeight(50)
        runIco = u'\uE0B0'
        self.appBtn = QPushButton()
        self.appBtn.setFont(font)
        self.appBtn.setText(" Виконати " + runIco)
        self.appBtn.setIcon(QIcon.fromTheme("applications-other"))
        self.appBtn.setIconSize(QSize(32, 32))
        self.appBtn.setMaximumSize(240, 30)
        self.appBtn.clicked.connect(self.app_click)
        self.launcher.lineEdit.returnPressed.connect(lambda: self.AppLaunch(self.launcher.lineEdit.text()))
        self.launcher.launchBtn.clicked.connect(lambda: self.AppLaunch(self.launcher.lineEdit.text()))
        self.launch_frame_frameLayout.addWidget(self.appBtn, 0, 0)
        self.setLayout(self.launch_frame_frameLayout)
        setShadow(self.appBtn, 25)



    def app_click(self):
        monitor = QDesktopWidget().screenGeometry(self.config['display']['output_display'])
        #self.launcher.move(monitor.left(), monitor.top())
        self.launcher.show()
        #self.virtual_keyboard = AlphaNeumericVirtualKeyboard(self.MainPanel, x_pos=0, y_pos=0)
        #self.virtual_keyboard.move(monitor.left(), monitor.top())
        #self.virtual_keyboard.display(self.launcher.lineEdit)
        #self.virtual_keyboard.raise_()


    def AppLaunch(self, command : str):
        raw_cmd = command.split(sep=" ")
        cmd = raw_cmd[0]
        keys = raw_cmd[1:]
        self.process.start(cmd, keys)
        #self.process.started.connect(lambda: self.MainPanel.showMessage("Виконано", 1500))
        #self.process.finished.connect(lambda: self.MainPanel.showMessage("Закрито", 1500))
        #self.process.error.connect(lambda: self.MainPanel.showMessage("Не виконано", 1500))
        self.launcher.hide()


class Launcher(QWidget):
    def __init__(self, *args, **kwargs):
        super(Launcher, self).__init__(*args, **kwargs)
        # Load the UI Page
        self.config = get_config()
        uic.loadUi('ui/launcher.ui', self)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint) # | Qt.WindowModal)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.hideBtn.clicked.connect(self.on_click)
        apps = get_apps_list("/usr/bin")
        self.completer = QCompleter(apps)
        self.lineEdit.setCompleter(self.completer)

    @pyqtSlot()
    def on_click(self):
        self.hide()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            print("Enter")
