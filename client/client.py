#! /usr/bin/python
import sys
sys.path.append(sys.path[0] + "/../")

from PyQt4.QtCore import pyqtSignal, QObject, QThread
from PyQt4.QtGui import QApplication, QInputDialog

from common.network import Message, Connection
from common.game import Player
from chat import Chat
from mainwindow import MainWindow
from connectdialog import ConnectDialog
from gamestate import GameState

class Client(QObject):
    sendReady = pyqtSignal(int, list)

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
        self.sendReady.connect(self.connection.sendMessage)
        self.connection.connectToHost(host, port)
        self.connection.moveToThread(thread)
        thread.start()
        self.send(Message.Join, [])

    def send(self, msg, args):
        self.sendReady.emit(msg, args)

    def handleMessage(self, msg, args):
        if msg == Message.Ping:
            self.send(Message.Pong, [])

        elif msg == Message.JoinSuccess:
            name = ""
            ok = False
            while not name or not ok:
                (name, ok) = QInputDialog.getText(None, "Username", "Name")
            self.send(Message.RequestName, [str(name)])

        elif msg == Message.NameTaken:
            name = ""
            ok = False
            while not name or not ok:
                (name, ok) = QInputDialog.getText(None, "Name Taken", "New name")
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
