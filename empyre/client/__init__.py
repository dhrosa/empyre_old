from PyQt4.QtCore import pyqtSignal, QObject, Qt
from PyQt4.QtGui import QApplication, QInputDialog, QMessageBox

from empyre.network import Message, Connection
from empyre import Player, State
from empyre.board import Card, Board, loadBoard
from chat import Chat, Line
from mainwindow import MainWindow
from connectdialog import ConnectDialog
from gamestate import GameState

import sys

class Client(QObject):
    sendReady = pyqtSignal(int, list)
    readyToConnect = pyqtSignal()

    def __init__(self, host, port, parent = None):
        QObject.__init__(self, parent)
        self.game = GameState()
        self.host = host
        self.port = port
        self.connection = Connection()
        self.connection.messageReceived.connect(self.handleMessage)
        self.connection.error.connect(self.handleError)
        self.sendReady.connect(self.connection.sendMessage)
        self.connection.connectToHost(self.host, self.port)
        while not self.connection.waitForConnected(10000):
            if not QMessageBox.Retry == QMessageBox.critical(None, "Connection Failed", "Failed to connect to %s on port %d" % (self.host, self.port), QMessageBox.Retry | QMessageBox.Cancel):
                sys.exit()
        self.send(Message.Join)
        QApplication.setQuitOnLastWindowClosed(False)

    def send(self, msg, args = []):
        self.sendReady.emit(msg, args)

    def handleError(self, err):
        QMessageBox.critical(None, "Network Error", self.connection.errorString())
        QApplication.quit()

    def handleMessage(self, msg, args):
        print Message.toString(msg), args
        if msg == Message.Ping:
            self.send(Message.Pong)

        elif msg == Message.StateChanged:
            self.handleStateChange(*args)

        elif msg == Message.ReceiveChat:
            (sender, text, timestamp) = args
            p = self.game.getPlayer(sender)
            if not p:
                color = (128, 128, 128)
            else:
                color = p.color
            self.mainWindow.chat.addLine(Line(Line.Chat, sender=sender, text=text, playerColor=color, timestamp = timestamp))

        elif msg == Message.ReceiveWhisper:
            (sender, target, text, timestamp) = args
            p = self.game.getPlayer(sender)
            self.mainWindow.chat.addLine(Line(Line.Whisper, sender=sender, target=target, text=text, playerColor=p.color, timestamp = timestamp))

        elif msg == Message.WhisperError:
            self.mainWindow.chat.addLine("No such player.")

        elif msg == Message.JoinSuccess:
            name = ""
            """
            if debug:
                global clientName
                name = clientName
            """
            while not name:
                (name, ok) = QInputDialog.getText(None, "Username", "Name")
                if not ok:
                    QApplication.quit()
                    break
            self.send(Message.RequestName, [name])
        
        elif msg == Message.NameTaken:
            name = ""
            while not name:
                (name, ok) = QInputDialog.getText(None, "Name Taken", "New name")
                if not ok:
                    QApplication.quit()
                    break
            self.send(Message.RequestName, [name])
        
        elif msg == Message.NameAccepted:
            (self.clientPlayerName, self.password) = args
            self.send(Message.RequestPlayerList)

        elif msg == Message.PlayerJoined:
            name = args[0]
            color = args[1:]
            player = self.game.addPlayer(name)
            player.color = color
            self.mainWindow.chat.addLine(Line(Line.PlayerJoined, target=name))
            self.mainWindow.playerInfo.addPlayer(name, color)

        elif msg == Message.GameInProgress:
            password = ""
            while not password:
                (password, ok) = QInputDialog.getText(None, "Game Already Inprogress", "Password")
                if not ok:
                    QApplication.quit()
                    break
            self.send(Message.Rejoin, [str(password)])

        elif msg == Message.IncorrectPassword:
            password = ""
            while not password:
                (password, ok) = QInputDialog.getText(None, "Incorrect Password", "Password")
                if not ok:
                    QApplication.quit()
                    break
            self.send(Message.Rejoin, [str(password)])

        elif msg == Message.RejoinSuccess:
            name = args[0]
            self.clientPlayerName = name
            self.send(Message.RequestPlayerList)

        elif msg == Message.PlayerRejoined:
            name = args[0]
            self.mainWindow.chat.addLine(Line(Line.PlayerRejoined, target=name))

        elif msg == Message.BeginPlayerList:
            pass

        elif msg == Message.PlayerInfo:
            name = args[0]
            color = args[1:]
            player = self.game.addPlayer(name)
            player.color = color

        elif msg == Message.EndPlayerList:
            self.send(Message.RequestBoardName)

        elif msg == Message.LoadBoard:
            boardName = args[0]
            board = loadBoard(boardName, images=True)
            if not board:
                QMessageBox.critical(None, "Board Missing", "You do not have the board \"%s\" required for this game." % (boardName), QMessageBox.Close)
                QApplication.quit()
            self.game.board = board
            self.game.clientPlayer = self.game.getPlayer(self.clientPlayerName)
            del self.clientPlayerName
            self.mainWindow = MainWindow(self.game)
            self.game.changed.connect(self.mainWindow.boardWidget.update)
            self.mainWindow.boardWidget.territoryClaimed.connect(self.sendClaimTerritory)
            self.mainWindow.boardWidget.drafted.connect(self.sendDraft)
            self.mainWindow.boardWidget.attacked.connect(self.sendAttack)
            self.mainWindow.boardWidget.fortified.connect(self.sendFortify)
            self.mainWindow.setWindowTitle("Risk %s:%d" % (self.host, self.port))
            self.mainWindow.chat.lineEntered.connect(self.sendChat)
            self.mainWindow.colorChanged.connect(self.sendColorChange)
            self.mainWindow.nameChanged.connect(self.sendNameChange)
            self.mainWindow.endAttackReleased.connect(self.sendEndAttack)
            self.mainWindow.endTurnReleased.connect(self.sendEndTurn)
            for p in self.game.players:
                self.mainWindow.playerInfo.addPlayer(p.name, p.color)
            self.mainWindow.show()
            try:
                _ = self.password
                self.mainWindow.chat.addLine("Welcome to the game!")
                self.mainWindow.chat.addLine("Your password is \"%s\"." % self.password)
                self.mainWindow.chat.addLine("Use this password to rejoin the game once it has started.")
                del self.password
                self.send(Message.ReadyToPlay)
            except AttributeError:
                self.mainWindow.chat.addLine("Welcome back to the game!")
                self.mainWindow.boardWidget.setEnabled(True)
            QApplication.setQuitOnLastWindowClosed(True)
            self.send(Message.RequestChatHistory)
            
        elif msg == Message.PlayerLeft:
            name = args[0]
            self.game.removePlayer(name)
            self.mainWindow.chat.addLine(Line(Line.PlayerLeft, target=name))
            self.mainWindow.playerInfo.removePlayer(name)

        elif msg == Message.PlayerLeftDuringGame:
            name = args[0]
            self.mainWindow.chat.addLine(Line(Line.PlayerLeft, target=name))

        elif msg == Message.ColorChanged:
            name = args[0]
            color = args[1:]
            self.game.setPlayerColor(name, color)
            self.mainWindow.chat.changePlayerColor(name, color)
            self.mainWindow.chat.addLine("%s has changed their color." % (name))
            self.mainWindow.playerInfo.changePlayerColor(name, color)

        elif msg == Message.NameChangeTaken:
            self.mainWindow.chat.addLine("That name is already taken.")

        elif msg == Message.NameChangeSuccess:
            name = args[0]
            self.game.setPlayerName(self.game.clientPlayer.name, name)

        elif msg == Message.NameChanged:
            before = args[0]
            after = args[1]
            self.game.setPlayerName(before, after)
            self.mainWindow.chat.changePlayerName(before, after)
            self.mainWindow.chat.addLine("%s changed their name to %s" % (before, after))
            self.mainWindow.playerInfo.changePlayerName(before, after)

        elif msg == Message.TurnChanged:
            name = args[0]
            self.game.setCurrentPlayer(name)
            if self.game.yourTurn():
                self.mainWindow.activateWindow()
            self.mainWindow.playerInfo.changeCurrentPlayer(name)

        elif msg == Message.BeginTiedPlayerList:
            self.tiedPlayers = []

        elif msg == Message.TiedPlayer:
            self.tiedPlayers.append(args[0])

        elif msg == Message.EndTiedPlayerList:
            names = ",".join(self.tiedPlayers[:-1])
            last = self.tiedPlayers[-1]
            self.mainWindow.chat.addLine("%s and %s have tied!" % (names, last))

        elif msg == Message.DiceRolled:
            (name, r1, r2, r3) = args
            roll = [r1, r2, r3]
            self.mainWindow.chat.addLine("%s rolled %s" % (name, [r for r in roll if r]))

        elif msg == Message.TerritoryUpdated:
            (name, owner, count) = args
            t = self.game.board.getTerritory(name)
            previousOwner = t.owner
            previousTroopCount = t.troopCount
            t.owner = self.game.getPlayer(owner)
            t.troopCount = count
            if t.owner != previousOwner:
                self.mainWindow.boardWidget.updateTerritoryOwner(name, owner)
            if t.troopCount != previousTroopCount:
                self.mainWindow.boardWidget.updateTerritoryTroopCount(name, count)
            self.game.changed.emit()

        elif msg == Message.RemainingTroopsChanged:
            troops = args[0]
            self.game.remainingTroops = troops

        elif msg == Message.Attacked:
            (attacker, source, target) = args
            self.mainWindow.boardWidget.attack(*args)

        elif msg == Message.ReceiveCard:
            (t, u) = args
            t = self.game.board.getTerritory(t)
            self.game.clientPlayer.cards.append(Card(t, u))
            self.game.changed.emit()

        elif msg == Message.CardAwarded:
            name = args[0]
            player = self.game.getPlayer(name)
            if player != self.game.clientPlayer:
                player.cards.append(Card())
            count = len(player.cards)
            self.mainWindow.playerInfo.setCardCount(name, count)

    def handleStateChange(self, old, new):
        self.mainWindow.cashCards.setEnabled(False)
        self.mainWindow.endAttack.setEnabled(False)
        self.mainWindow.endTurn.setEnabled(False)
        if old == State.Lobby:
            self.mainWindow.chat.addLine("The game has started!")
            self.mainWindow.boardWidget.setEnabled(True)
            self.mainWindow.changeName.setEnabled(False)
            self.mainWindow.changeColor.setEnabled(False)
        elif self.game.yourTurn():
            if new == State.Draft:
                self.mainWindow.cashCards.setEnabled(True)
            elif new == State.Attack:
                self.mainWindow.endAttack.setEnabled(True)
                self.mainWindow.endTurn.setEnabled(True)
            elif new == State.Fortify:
                self.mainWindow.endTurn.setEnabled(True)
        self.mainWindow.boardWidget.stateChange(old, new)
        self.game.state = new

    def sendChat(self, text):
        if not text:
            return
        parts = text.split(" ")
        if parts[0] == "/to":
            if len(parts) < 3:
                self.mainWindow.chat.addLine("Invalid command.")
                return
            target = parts[1]
            text = " ".join(parts[2:])
            self.send(Message.SendWhisper, [target, text])
        else:
            self.send(Message.SendChat, [text])

    def sendColorChange(self, color):
        self.send(Message.ChangeColor, color)

    def sendNameChange(self, name):
        self.send(Message.ChangeName, [name])

    def sendClaimTerritory(self, name):
        self.send(Message.ClaimTerritory, [name])

    def sendDraft(self, name, count):
        self.send(Message.Draft, [name, count])

    def sendAttack(self, source, target, n):
        self.send(Message.Attack, [source, target, n])

    def sendEndAttack(self):
        self.send(Message.EndAttack)

    def sendFortify(self, source, target, n):
        self.send(Message.Fortify, [source, target, n])

    def sendEndTurn(self):
        self.send(Message.EndTurn)
