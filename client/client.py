#! /usr/bin/python
import sys
sys.path.append(sys.path[0] + "/../")

from PyQt4.QtCore import pyqtSignal, QObject, QThread
from PyQt4.QtGui import QApplication

from common.network import Message, Connection
from chat import Chat
from mainwindow import MainWindow
from connectdialog import ConnectDialog

class Client(QObject):
    sendReady = pyqtSignal(int, list)

    def __init__(self, host, port, playerName, parent = None):
        QObject.__init__(self, parent)
        thread = QThread(self)
        QApplication.instance().aboutToQuit.connect(thread.quit)
        self.connection = Connection()
        self.connection.connectToHost(host, port)
        self.connection.messageReceived.connect(self.handleMessage)
        self.connection.moveToThread(thread)
        self.sendReady.connect(self.connection.sendMessage)
        self.playerName = str(playerName)
        self.mainWindow = MainWindow()
        self.mainWindow.setWindowTitle("Risk %s:%d" % (host, port))
        self.mainWindow.chat.lineEntered.connect(self.sendChat)
        self.mainWindow.show()
        thread.start()

    def handleMessage(self, msg, args):
        if msg == Message.Chat:
            (sender, text) = args
            self.mainWindow.chat.addLine(sender, 0, text)

    def sendChat(self, text):
        self.sendReady.emit(Message.Chat, [self.playerName, str(text)])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = ConnectDialog()
    if dialog.exec_():
        client = Client(dialog.hostEdit.text(), dialog.portEdit.value(), dialog.nameEdit.text())
        sys.exit(app.exec_())
    sys.exit()
