
import openai
from PyQt5 import uic
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (QWidget)
from decouple import config

from tools import get_config, get_random_question


class ChatBot():
    def __init__(self):
        self.config = get_config()
        self.api_key = config('OPENAI_API_KEY')
        self.model_engine = self.config['openai']['model_engine']
        self._prompt = ""
        openai.api_key = self.api_key

    @property
    def prompt(self):
        return self._prompt
    @prompt.setter
    def prompt(self, prompt: str):
        self._prompt = prompt


    def getResponce(self, max_tokens=1024, n=1, stop=None, temperature=0.5):
        # Generate a response
        try:
            completion = openai.Completion.create(
                engine=self.model_engine,
                prompt=self._prompt,
                max_tokens=max_tokens,
                n=n,
                stop=stop,
                temperature=temperature,
            )
            return completion.choices

        except openai.error.Timeout as e:
            # Handle timeout error, e.g. retry or log
            return f"OpenAI API request timed out: {e}"

        except openai.error.APIError as e:
            # Handle API error, e.g. retry or log
            return f"OpenAI API returned an API Error: {e}"

        except openai.error.APIConnectionError as e:
            # Handle connection error, e.g. check network or log
            return f"OpenAI API request failed to connect: {e}"

        except openai.error.InvalidRequestError as e:
            # Handle invalid request error, e.g. validate parameters or log
            print(f"OpenAI API request was invalid: {e}")

        except openai.error.AuthenticationError as e:
            # Handle authentication error, e.g. check credentials or log
            return f"OpenAI API request was not authorized: {e}"

        except openai.error.PermissionError as e:
            # Handle permission error, e.g. check scope or log
            return f"OpenAI API request was not permitted: {e}"

        except openai.error.RateLimitError as e:
            # Handle rate limit error, e.g. wait or log
            return f"OpenAI API request exceeded rate limit: {e}"




class BrowserHandler(QObject):
    running = False
    newTextAndColor = pyqtSignal(str, object)
    config = get_config()
    refresh_interval = (int(config['intervals']['chatbot_fefresh_min']) * 1024) * 60
    chatbot = ChatBot()
    # method which will execute algorithm in another thread
    def run(self):

        while True:
            # send signal with new text and color from aonther thread
            question = get_random_question()
            print(question)
            self.chatbot.prompt = question
            response = self.chatbot.getResponce(max_tokens=1024, n=1, stop=None, temperature=0.5)
            try:
                response_text = response[0].text
            except:
                response_text = response
            self.newTextAndColor.emit('{}'.format(response_text), QColor(255, 255, 255))
            QThread.msleep(self.refresh_interval)


class GPTChat(QWidget):
    def __init__(self, *args, **kwargs):
        super(GPTChat, self).__init__(*args, **kwargs)
        # Load the UI Page
        self.config = get_config()
        uic.loadUi('ui/chat_box.ui', self)
        self.mainwindow = args[0]
        font = QFont()
        font.setFamily("DejaVu Sans Mono for Powerline")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(100)
        self.answer_box.setFont(font)
        self.answer_box.setAcceptRichText(True)
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