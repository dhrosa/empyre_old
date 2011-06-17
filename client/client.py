#! /usr/bin/python
import sys
sys.path.append(sys.path[0] + "/../")

from PyQt4.QtCore import pyqtSignal, QObject, QThread
from PyQt4.QtGui import QApplication, QInputDialog

from common.network import Message, Connection
from chat import Chat
from mainwindow import MainWindow
from connectdialog import ConnectDialog

class Client(QObject):
    sendReady = pyqtSignal(int, list)

    def __init__(self, host, port, parent = None):
        QObject.__init__(self, parent)
        self.host = str(host)
        self.port = port
        thread = QThread(self)
        QApplication.instance().aboutToQuit.connect(thread.quit)
        QApplication.setQuitOnLastWindowClosed(False)
        self.connection = Connection()
        self.connection.messageReceived.connect(self.handleMessage)
        self.sendReady.connect(self.connection.sendMessage)
        self.connection.connectToHost(host, port)
        self.connection.moveToThread(thread)
        thread.start()
        self.sendReady.emit(Message.Join, [])

    def handleMessage(self, msg, args):
        if msg == Message.JoinSuccess:
            name = ""
            ok = False
            while not name or not ok:
                (name, ok) = QInputDialog.getText(None, "Choose your name", "Name")
            self.sendReady.emit(Message.RequestName, [str(name)])

        elif msg == Message.NameTaken:
            name = ""
            ok = False
            while not name or not ok:
                (name, ok) = QInputDialog.getText(None, "Your requested name was taken, please choose another", "Name")
            self.sendReady.emit(Message.RequestName, [str(name)])
        
        elif msg == Message.NameAccepted:
            self.playerName = str(args[0])
            self.mainWindow = MainWindow()
            self.mainWindow.setWindowTitle("Risk %s:%d" % (self.host, self.port))
            self.mainWindow.chat.lineEntered.connect(self.sendChat)
            self.mainWindow.show()
            QApplication.setQuitOnLastWindowClosed(True)

        elif msg == Message.PlayerJoined:
            pass

        elif msg == Message.ReceiveChat:
            (sender, text) = args
            print sender, text
            self.mainWindow.chat.addLine(sender, 0, text)

    def sendChat(self, text):
        self.sendReady.emit(Message.SendChat, [str(text)])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = ConnectDialog()
    if dialog.exec_():
        client = Client(dialog.hostEdit.text(), dialog.portEdit.value())
        sys.exit(app.exec_())
    sys.exit()
