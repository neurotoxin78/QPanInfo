
from PyQt5 import uic
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (QWidget, QGridLayout, QTextBrowser)
from tools import get_config
from chat import ChatBot


class BrowserHandler(QObject):
    running = False
    newTextAndColor = pyqtSignal(str, object)

    # method which will execute algorithm in another thread
    def run(self):
        config = get_config()
        refresh_interval = (int(config['intervals']['humor_fefresh_min']) * 1024) * 60
        chatbot = ChatBot()
        while True:
            try:
                # send signal with new text and color from aonther thread
                chatbot.setPrompt("Пожартуй весело та коротко на довільну тему. не більше 180 символів")
                response = chatbot.getResponce(max_tokens=1024, n=1, stop=None, temperature=0.65)
                humor_text = response[0].text
                self.newTextAndColor.emit(
                    '{}.'.format(humor_text),
                    QColor(255, 255, 255)
                )
            except:
                self.newTextAndColor.emit("Error! See log for details", QColor(255, 128, 128))

            QThread.msleep(refresh_interval)




class GPTChat(QWidget):
    def __init__(self, *args, **kwargs):
        super(GPTChat, self).__init__(*args, **kwargs)
        # Load the UI Page
        self.config = get_config()
        uic.loadUi('ui/humor_box.ui', self)
        self.mainwindow = args[0]
        font = QFont()
        font.setFamily("DejaVu Sans Mono for Powerline")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(100)
        self.answer_box.setFont(font)
        self.answer_box.setAcceptRichText(True)

        #self.humor_box.setOpenExternalLinks(True)
        #self.humor_box.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # create thread
        self.thread = QThread()
        # create object which will be moved to another thread
        self.browserHandler = BrowserHandler()
        # move object to another thread
        self.browserHandler.moveToThread(self.thread)
        # after that, we can connect signals from this object to slot in GUI thread
        self.browserHandler.newTextAndColor.connect(self.updateText)
        # connect started signal to run method of object in another thread
        self.thread.started.connect(self.browserHandler.run)
        # start thread
        self.thread.start()

    @pyqtSlot(str, object)
    def updateText(self, string, color):
        self.answer_box.setTextColor(color)
        self.answer_box.clear()
        c = self.answer_box.textCursor()
        p = c.position()
        hPos = self.answer_box.horizontalScrollBar().value()
        vPos = self.answer_box.verticalScrollBar().value()
        self.answer_box.append(string.lstrip())
        c.setPosition(p)
        self.answer_box.horizontalScrollBar().setValue(hPos)
        self.answer_box.verticalScrollBar().setValue(vPos)
        self.answer_box.setTextCursor(c)
        self.mainwindow.statusBar.showMessage("ChatGPT: Отримано нову відповідь", 3000)