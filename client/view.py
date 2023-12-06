import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import _thread

from controller import *


class MySignalEmitter(QObject):
    # Define a custom signal with a value
    custom_signal = pyqtSignal(str, str)

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.model = None
        self.title = 'Komunikator'
        self.left = 100
        self.top = 100
        self.width = 800
        self.height = 600
        self.initUI()
        self.controller = Controller()
        self.controller.setApp(self)
        # self.model.setApp(self)
        self.currentlyOpenedChat = -1
        # Create an instance of the signal emitter
        self.signal_emitter = MySignalEmitter()
        _thread.start_new_thread(self.controller.controllerStart, ())

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        layout = QGridLayout(self)
        self.setLayout(layout)

        # Edytor Wiadomości
        self.textEditor = QLineEdit(self)
        # self.textEditor.move(20, 20)
        self.textEditor.resize(280, 40)
        layout.addWidget(self.textEditor, 0, 0, 1, 1)
        # layout.addWidget(self.textEditor, 0, 0)

        # tu będą wiadodmości
        self.chatBox = QPlainTextEdit(self)
        self.chatBox.setDisabled(True)
        # self.chatBox.move(20, 120)
        self.chatBox.resize(1280, 640)
        layout.addWidget(self.chatBox, 1, 0, 2, 2)
        # layout.addWidget(self.chatBox, 0, 1)

        # Create a sendButton in the window
        self.sendButton = QPushButton('Wyślij', self)
        # self.sendButton.move(20, 80)
        # layout.addWidget(self.sendButton, 0, 1, 1, 1)
        layout.addWidget(self.sendButton, 0, 1)

        # connect sendButton to function sendButtonClicked
        self.sendButton.clicked.connect(self.sendButtonClicked)

        # lista użytkowników
        self.onlineUsersListWidget = QListWidget(self)
        self.onlineUsersListWidget.clicked.connect(self.onlineUsersListWidgetClicked)
        layout.addWidget(self.onlineUsersListWidget, 0, 2, -1, 1)
        # layout.addWidget(self.onlineUsersListWidget, 0, 2)


        self.show()

    def onlineUsersListWidgetClicked(self, qmodelindex):
        item = self.onlineUsersListWidget.currentItem()
        self.currentlyOpenedChat = item.text()
        self.controller.setInterlocutorId(item.text())
        self.displayMessageHistory()

    def addMultipleOnlineUsers(self, onlineUsers):
        listOfUsers = onlineUsers[1:-1].split(', ')
        for user in listOfUsers:
            # self.onlineUsersListWidget.addItem(user)
            self.addOnlineUser(user[1:-1])


    def addOnlineUser(self, user):
        self.onlineUsersListWidget.addItem(user)

    def displayMessageHistory(self):
        messageHistory = self.model.getUserChatHistory(self.currentlyOpenedChat)
        # print(messageHistory)
        self.chatBox.clear()
        for messageInfo in messageHistory:
            text = str(messageInfo)                         # tutaj sparsować dicta
                                                            #TODO: w displayMessage wysyłać dicta??
            self.displayMessage(text, 0)

    def sendButtonClicked(self):
        textEditorValue = self.textEditor.text()
        self.textEditor.setText("")
        self.controller.sendMessage(textEditorValue)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.sendButtonClicked()

    def closeEvent(self, event):
        self.controller.endController()

    def displayMessage(self, msg, userName):
        self.signal_emitter.custom_signal.emit(msg, str(userName))



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()


    def displayMessageBoruSlot(msg, userName):
        if userName == "-1":
            ex.chatBox.insertPlainText("\ninfo od serwera:\n\t")

        if userName == ex.currentlyOpenedChat or userName == "-1" or userName == "0":
            ex.chatBox.insertPlainText("\n" + msg)

    ex.signal_emitter.custom_signal.connect(displayMessageBoruSlot)
    sys.exit(app.exec_())
