#! /usr/bin/python
import sys
sys.path.append(sys.path[0] + "/../")

from PyQt4.QtCore import pyqtSignal, QObject, QThread, Qt
from PyQt4.QtGui import QApplication, QInputDialog, QMessageBox

from common.network import Message, Connection
from common.game import Player
from common.board import Board, loadBoard
from chat import Chat
from mainwindow import MainWindow
from connectdialog import ConnectDialog
from gamestate import GameState

class Client(QObject):
    sendReady = pyqtSignal(int, list)
    readyToConnect = pyqtSignal()

    def __init__(self, host, port, parent = None):
        QObject.__init__(self, parent)
        self.game = GameState()
        self.host = str(host)
        self.port = port
        thread = QThread(self)
        QApplication.instance().aboutToQuit.connect(thread.quit)
        QApplication.setQuitOnLastWindowClosed(False)
        self.connection = Connection()
        self.connection.moveToThread(thread)
        self.connection.host = host
        self.connection.port = port
        self.connection.messageReceived.connect(self.handleMessage)
        self.connection.connected.connect(self.sendJoinMessage)
        self.connection.connectionFailed.connect(self.connectionFail)
        self.sendReady.connect(self.connection.sendMessage)
        self.readyToConnect.connect(self.connection.tryConnectToHost)
        thread.started.connect(self.connection.tryConnectToHost)
        thread.start()

    def send(self, msg, args = []):
        self.sendReady.emit(msg, args)

    def handleMessage(self, msg, args):
        if msg == Message.Ping:
            self.send(Message.Pong)

        elif msg == Message.ReceiveChat:
            (sender, text) = args
            p = self.game.getPlayer(sender)
            if not p:
                color = (128, 128, 128)
            else:
                color = p.color
            self.mainWindow.chat.addLine(sender, color, text)

        elif msg == Message.JoinSuccess:
            name = ""
            while not name:
                (name, ok) = QInputDialog.getText(None, "Username", "Name")
                if not ok:
                    self.connection.thread().quit()
                    sys.exit()
            self.send(Message.RequestName, [str(name)])
        
        elif msg == Message.NameTaken:
            name = ""
            while not name:
                (name, ok) = QInputDialog.getText(None, "Name Taken", "New name")
                if not ok:
                    self.connection.thread().quit()
                    sys.exit()
            self.send(Message.RequestName, [str(name)])
        
        elif msg == Message.NameAccepted:
            self.clientPlayerName = str(args[0])
            self.password = str(args[1])
            self.send(Message.RequestPlayerList)

        elif msg == Message.PlayerJoined:
            name = str(args[0])
            self.game.addPlayer(name)
            self.mainWindow.chat.addInfoLine((0, 170, 0), "%s has joined." % (name))

        elif msg == Message.GameInProgress:
            password = ""
            while not password:
                (password, ok) = QInputDialog.getText(None, "Game Already Inprogress", "Password")
                if not ok:
                    self.connection.thread().quit()
                    sys.exit()
            self.send(Message.Rejoin, [str(password)])

        elif msg == Message.IncorrectPassword:
            password = ""
            while not password:
                (password, ok) = QInputDialog.getText(None, "Incorrect Password", "Password")
                if not ok:
                    self.connection.thread().quit()
                    sys.exit()
            self.send(Message.Rejoin, [str(password)])

        elif msg == Message.RejoinSuccess:
            name = str(args[0])
            self.clientPlayerName = name
            self.send(Message.RequestPlayerList)

        elif msg == Message.PlayerRejoined:
            name = str(args[0])
            self.mainWindow.chat.addInfoLine((0, 170, 0), "%s has rejoined." % (name))

        elif msg == Message.BeginPlayerList:
            pass

        elif msg == Message.PlayerInfo:
            name = str(args[0])
            color = args[1:]
            player = self.game.addPlayer(name)
            player.color = color

        elif msg == Message.EndPlayerList:
            self.send(Message.RequestBoardName)

        elif msg == Message.LoadBoard:
            boardName = str(args[0])
            board = loadBoard(boardName, images=True)
            if not board:
                QMessageBox.critical(None, "Board Missing", "You do not have the board \"%s\" required for this game." % (boardName), QMessageBox.Close)
                self.connection.thread().quit()
                sys.exit()
            self.game.board = board
            self.game.clientPlayer = self.game.getPlayer(self.clientPlayerName)
            del self.clientPlayerName
            self.mainWindow = MainWindow(self.game)
            self.mainWindow.setWindowTitle("Risk %s:%d" % (self.host, self.port))
            self.mainWindow.chat.lineEntered.connect(self.sendChat)
            self.mainWindow.colorChanged.connect(self.sendColorChange)
            self.mainWindow.nameChanged.connect(self.sendNameChange)
            self.mainWindow.show()
            try:
                self.mainWindow.chat.addInfoLine((0, 0, 170), "Welcome to the game! Your password is \"%s\". Use this password to rejoin the game once it has started." % (self.password))
                del self.password
            except AttributeError:
                self.mainWindow.chat.addInfoLine((0, 0, 170), "Welcome back to the game!")
                self.mainWindow.boardWidget.setEnabled(True)
            QApplication.setQuitOnLastWindowClosed(True)
            self.send(Message.RequestChatHistory)
            
        elif msg == Message.PlayerLeft:
            name = str(args[0])
            self.game.removePlayer(name)
            self.mainWindow.chat.addInfoLine((170, 0, 0), "%s has left." % (name))

        elif msg == Message.PlayerLeftDuringGame:
            name = str(args[0])
            self.mainWindow.chat.addInfoLine((170, 0, 0), "%s has left." % (name))

        elif msg == Message.ColorChanged:
            name = str(args[0])
            color = args[1:]
            if name == self.game.clientPlayer.name:
                self.game.clientPlayer.color = color
                self.mainWindow.changeColor(color)
            else:
                self.game.getPlayer(name).color = color
            self.mainWindow.chat.changePlayerColor(name, color)
            self.mainWindow.chat.addInfoLine((0, 0, 170), "%s has changed their color." % (name))

        elif msg == Message.NameChangeTaken:
            self.mainWindow.nameEdit.setText(self.game.clientPlayer.name)
            self.mainWindow.chat.addInfoLine((170, 0, 0), "That name is already taken.")

        elif msg == Message.NameChangeSuccess:
            name = str(args[0])
            self.mainWindow.nameEdit.setText(name)
            self.game.clientPlayer.name = name
            self.mainWindow.chat.addInfoLine((0, 0, 170), "You successfully changed your name.")

        elif msg == Message.NameChanged:
            before = str(args[0])
            after = str(args[1])
            player = self.game.getPlayer(before)
            if player:
                player.name = after
            self.mainWindow.chat.changePlayerName(before, after)
            self.mainWindow.chat.addInfoLine((0, 0, 170), "%s changed their name to %s" % (before, after))

        elif msg == Message.GameStarted:
            self.mainWindow.boardWidget.setEnabled(True)
            self.mainWindow.chat.addInfoLine((0, 170, 0), "The game has started!")
                

    def connectionFail(self):
        if QMessageBox.Retry == QMessageBox.critical(None,
                                "Connection Failed",
                                "Failed to connect to %s on port %d" % (self.host, self.port),
                                QMessageBox.Retry | QMessageBox.Cancel):
            self.readyToConnect.emit()
        else:
            self.connection.thread().quit()
            sys.exit()
                                
    def sendJoinMessage(self):
        self.send(Message.Join)

    def sendChat(self, text):
        self.send(Message.SendChat, [str(text)])

    def sendColorChange(self, color):
        self.send(Message.ChangeColor, color)

    def sendNameChange(self, name):
        self.send(Message.ChangeName, [str(name)])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = ConnectDialog()
    if dialog.exec_():
        client = Client(dialog.hostEdit.text(), dialog.portEdit.value())
        sys.exit(app.exec_())
    sys.exit()
