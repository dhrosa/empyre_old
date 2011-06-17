#! /usr/bin/python
import sys
sys.path.append(sys.path[0] + "/../")

from PyQt4.QtCore import pyqtSignal, QObject, QThread
from PyQt4.QtGui import QApplication, QInputDialog, QMessageBox

from common.network import Message, Connection
from common.game import Player
from chat import Chat
from mainwindow import MainWindow
from connectdialog import ConnectDialog
from gamestate import GameState

class Client(QObject):
    sendReady = pyqtSignal(int, list)
    readyToConnect = pyqtSignal(str, int)

    def __init__(self, host, port, parent = None):
        QObject.__init__(self, parent)
        self.game = GameState()
        self.host = str(host)
        self.port = port
        thread = QThread(self)
        QApplication.instance().aboutToQuit.connect(thread.quit)
        QApplication.setQuitOnLastWindowClosed(False)
        self.connection = Connection()
        self.connection.messageReceived.connect(self.handleMessage)
        self.connection.connected.connect(self.sendJoinMessage)
        self.connection.connectionFailed.connect(self.connectionFail)
        self.sendReady.connect(self.connection.sendMessage)
        self.readyToConnect.connect(self.connection.tryConnectToHost)
        self.connection.moveToThread(thread)
        thread.start()
        self.tryConnect()

    def send(self, msg, args):
        self.sendReady.emit(msg, args)

    def handleMessage(self, msg, args):
        if msg == Message.Ping:
            self.send(Message.Pong, [])

        elif msg == Message.JoinSuccess:
            name = ""
            while not name:
                (name, ok) = QInputDialog.getText(None, "Username", "Name")
                if not ok:
                    sys.exit()
            self.send(Message.RequestName, [str(name)])

        elif msg == Message.NameTaken:
            name = ""
            while not name:
                (name, ok) = QInputDialog.getText(None, "Name Taken", "New name")
                if not ok:
                    sys.exit()
            self.send(Message.RequestName, [str(name)])
        
        elif msg == Message.NameAccepted:
            name = str(args[0])
            self.game.clientPlayer = Player(name)
            self.game.players.append(self.game.clientPlayer)
            self.mainWindow = MainWindow(self.game)
            self.mainWindow.setWindowTitle("Risk %s:%d" % (self.host, self.port))
            self.mainWindow.chat.lineEntered.connect(self.sendChat)
            self.mainWindow.colorChanged.connect(self.sendColorChange)
            self.mainWindow.show()
            QApplication.setQuitOnLastWindowClosed(True)

        elif msg == Message.PlayerJoined:
            name = str(args[0])
            if not self.game.player(name):
                self.game.players.append(Player(name))

        elif msg == Message.ColorChanged:
            name = str(args[0])
            color = args[1:]
            if name == self.game.clientPlayer.name:
                self.game.clientPlayer.color = color
                self.mainWindow.changeColor(color)
            else:
                self.game.player(name).color = color
            self.mainWindow.chat.changePlayerColor(name, color)

        elif msg == Message.ReceiveChat:
            (sender, text) = args
            p = self.game.player(sender)
            self.mainWindow.chat.addLine(sender, p.color, text)

    def tryConnect(self):
        self.readyToConnect.emit(self.host, self.port)

    def connectionFail(self):
        if QMessageBox.critical(None,
                                "Connection Failed",
                                "Failed to connect to %s on port %d" % (self.host, self.port),
                                QMessageBox.Retry | QMessageBox.Cancel):
            self.tryConnect()
                                
    def sendJoinMessage(self):
        self.send(Message.Join, [])

    def sendChat(self, text):
        self.send(Message.SendChat, [str(text)])

    def sendColorChange(self, color):
        self.send(Message.ChangeColor, color)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = ConnectDialog()
    if dialog.exec_():
        client = Client(dialog.hostEdit.text(), dialog.portEdit.value())
        sys.exit(app.exec_())
    sys.exit()
