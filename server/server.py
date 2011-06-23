#! /usr/bin/python
import sys
sys.path.append(sys.path[0] + "/../")
import sip
sip.setapi('QString', 2)

import random
import string

from sm import SM
from common.game import State, Action
from common.network import Message, Connection
from common.board import loadBoard

from PyQt4.QtNetwork import QTcpServer, QTcpSocket
from PyQt4.QtCore import QCoreApplication, pyqtSignal, QSocketNotifier, QDateTime, QTimer

class Server(QTcpServer):
    sendReady = pyqtSignal(int, list)
    sendReadySpecific = pyqtSignal(int, list, int)
    resetting = pyqtSignal()

    predefinedColors = [
        [255, 0, 0],
        [0, 255, 0],
        [0, 0, 255],
        [255, 255, 0],
        [0, 255, 255],
        [255, 0, 255],
    ]

    def __init__(self, boardName, board, parent = None):
       QTcpServer.__init__(self, parent)
       self.boardName = boardName
       self.connections = []
       self.sm = SM(board)
       self.sm.stateChanged.connect(self.sendStateChange)
       self.sm.diceRolled.connect(self.sendDiceRoll)
       self.sm.turnChanged.connect(self.sendTurnChange)
       self.sm.territoryUpdated.connect(self.sendTerritoryUpdate)
       self.sm.remainingTroopsChanged.connect(self.sendRemainingTroopsChange)
       self.sm.attacked.connect(self.sendAttack)
       self.chatHistory = []
       self.colors = self.predefinedColors
       timer = QTimer(self)
       timer.setInterval(3000)
       timer.timeout.connect(self.sendPing)
       timer.start()

    def send(self, msg, args = []):
        self.sendReady.emit(msg, args)

    def sendTo(self, id, msg, args = []):
        self.sendReadySpecific.emit(msg, args, id)

    def sendExcept(self, id, msg, args = []):
        for c in self.connections:
            if c and c.id != id:
                self.sendTo(c.id, msg, args)

    def incomingConnection(self, socketDescriptor):
        c = Connection(socketDescriptor)
        c.error.connect(self.handleError)
        self.connections.append(c)
        c.messageReceived.connect(self.handleMessage)
        c.disconnected.connect(self.handleDisconnect)
        self.sendReady.connect(c.sendMessage)
        self.sendReadySpecific.connect(c.sendMessage)
        self.resetting.connect(c.abort)

        timer = QTimer(c)
        timer.setInterval(10000)
        timer.timeout.connect(self.handleTimeout)
        c.messageReceived2.connect(timer.start)
        timer.start() 

    def handleTimeout(self):
        conn = self.sender().parent()
        if conn.player:
            print "%s has timed out." % conn.player.name
        conn.abort()

    def handleError(self, err):
        print self.sender().errorString()
        self.sender().abort()

    def handleDisconnect(self):
        conn = self.sender()
        if conn.player:
            print "%s has disconnected." % (conn.player)
            self.sm.next(Action.RemovePlayer, [conn.player.name])
            if self.sm.substate == State.Lobby:
                self.send(Message.PlayerLeft, [conn.player.name])
            else:
                self.send(Message.PlayerLeftDuringGame, [conn.player.name])
        else:
            print "Anonymous client disconnected."
        self.connections.remove(conn)
        conn.deleteLater()

    def handleMessage(self, msg, args):
        conn = self.sender()
        if not conn.player:
            if msg == Message.Join:
                print "%s connected." % (conn.peerAddress().toString())
                if self.sm.substate != State.Lobby:
                    self.sendTo(conn.id, Message.GameInProgress)
                else:
                    self.sendTo(conn.id, Message.JoinSuccess)

            elif msg == Message.RequestName:
                name = args[0]
                print "%s requested the name \"%s\"." % (conn.peerAddress().toString(), name)
                if not self.sm.next(Action.AddPlayer, [name]):
                    print "Name taken."
                    self.sendTo(conn.id, Message.NameTaken)
                else:
                    password = "".join([random.choice(string.ascii_lowercase) for i in range(8)])
                    conn.player = self.sm.players[-1]
                    conn.player.password = password
                    if not self.colors:
                        conn.player.color = [random.randint(0, 255) for i in range(3)]
                    else:
                        conn.player.color = self.colors.pop(random.randint(0, len(self.colors) - 1))
                    print "%s has been granted the name \"%s\" and password: %s." % (conn.peerAddress().toString(), name, password)
                    print "%s has been assigned the color %s" % (name, conn.player.color)
                    self.sendTo(conn.id, Message.NameAccepted, [name, conn.player.password])
                    self.sendExcept(conn.id, Message.PlayerJoined, [name] + conn.player.color)


            elif msg == Message.Rejoin:
                password = args[0]
                for i in range(len(self.sm.players)):
                    if self.sm.players[i].password == password:
                        conn.player = self.sm.players[i]
                        break
                if conn.player:
                    print "%s has rejoined." % (conn.player.name)
                    self.sendTo(conn.id, Message.RejoinSuccess, [conn.player.name])
                    self.sendExcept(conn.id, Message.PlayerRejoined, [conn.player.name])
                else:
                    self.sendTo(conn.id, Message.IncorrectPassword)

        else:
            if msg == Message.SendChat:
                text = args[0]
                print "%s: %s" % (conn.player.name, text)
                timestamp = QDateTime.currentMSecsSinceEpoch()
                self.chatHistory.append([conn.player, text, timestamp])
                self.send(Message.ReceiveChat, [conn.player.name, text, timestamp])

            elif msg == Message.SendWhisper:
                (target, text) = args
                targetPlayer = self.sm.getPlayer(target)
                if not targetPlayer:
                    self.sendTo(conn.id, Message.WhisperError)
                else:
                    timestamp = QDateTime.currentMSecsSinceEpoch()
                    for c in self.connections:
                        if c.player == targetPlayer:
                            self.sendTo(c.id, Message.ReceiveWhisper, [conn.player.name, c.player.name, text, timestamp])
                            self.sendTo(conn.id, Message.ReceiveWhisper, [conn.player.name, c.player.name, text, timestamp])
                            print "%s >> %s: %s" % (conn.player.name, target, text)
                            break

            elif msg == Message.RequestBoardName:
                print "Sending board information to %s." % (conn.player.name)
                self.sendTo(conn.id, Message.LoadBoard, [self.boardName])

            elif msg == Message.RequestPlayerList:
                self.sendTo(conn.id, Message.BeginPlayerList)
                for p in self.sm.players:
                    self.sendTo(conn.id, Message.PlayerInfo, [p.name] + list(p.color))
                self.sendTo(conn.id, Message.EndPlayerList)

            elif msg == Message.RequestChatHistory:
                for line in self.chatHistory:
                    self.sendTo(conn.id, Message.ReceiveChat, [line[0].name, line[1]])

            elif msg == Message.ChangeName:
                before = conn.player.name
                after = args[0]
                if before == after:
                    return
                for player in self.sm.players:
                    if player == conn.player:
                        continue
                    if player.name == after:
                        self.sendTo(conn.id, Message.NameChangeTaken)
                        return
                conn.player.name = after
                print "%s changed their name to %s." % (before, after)
                self.sendTo(conn.id, Message.NameChangeSuccess, [after])
                self.send(Message.NameChanged, [before, after])            

            elif msg == Message.ChangeColor:
                color = args
                player = conn.player
                player.color = color
                print "%s changed their color to (%d, %d, %d)" % (player.name, color[0], color[1], color[2])
                self.send(Message.ColorChanged, [player.name] + color)

            elif msg == Message.ReadyToPlay:
                conn.player.ready = True
                if not False in [p.ready for p in self.sm.players] and self.sm.playerCount() > 1:
                    print "Game automatically started."
                    self.sm.next(Action.StartGame)

            elif msg == Message.ClaimTerritory:
                if conn.player == self.sm.currentPlayer:
                    name = args[0]
                    self.sm.next(Action.PlaceTroops, [name])

            elif msg == Message.Draft:
                if conn.player == self.sm.currentPlayer:
                    (name, count) = args
                    self.sm.next(Action.PlaceTroops, [name, count])

            elif msg == Message.Attack:
                if conn.player == self.sm.currentPlayer:
                    (source, target, count) = args
                    self.sm.next(Action.Attack, [source, target, count])

    def readStdin(self):
        line = sys.stdin.readline().strip()
        if line.lower() == "quit":
            QCoreApplication.quit()
        elif line.lower() == "reset":
            print "Resetting server."
            self.colors = self.predefinedColors
            self.resetting.emit()
            self.sm.reset()
        elif line.lower() == "start":
            if not self.sm.next(Action.StartGame):
                print "Need more players to start."

    def sendPing(self):
        self.send(Message.Ping)
                
    def sendStateChange(self, old, new):
        self.send(Message.StateChanged, [old, new])

    def sendDiceRoll(self, playerName, rolls):
        print "%s rolled %s." % (playerName, rolls)
        rolls += [0] * (3 - len(rolls))
        self.send(Message.DiceRolled, [playerName] + rolls)

    def sendTurnChange(self, name):
        self.send(Message.TurnChanged, [name])

    def sendTerritoryUpdate(self, name, owner, troopCount):
        name = str(name)
        owner = str(owner)
        print "%s owns %s with %d troops" % (owner, name, troopCount)
        self.send(Message.TerritoryUpdated, [name, owner, troopCount])

    def sendRemainingTroopsChange(self, n):
        if self.sm.currentPlayer:
            print "%s has %d troops remaining." % (self.sm.currentPlayer.name, n)
            self.send(Message.RemainingTroopsChanged, [n])

    def sendAttack(self, attacker, source, target):
        self.send(Message.Attacked, [attacker, source, target])

if __name__ == "__main__":
    app = QCoreApplication(sys.argv)
    try:
        boardName = sys.argv[1]
    except IndexError:
        print "Please specify a board to load."
        sys.exit(1)
    board = loadBoard(boardName)
    if not board:
        print "Could not load board: %s" % (boardName)
    print "Loaded \"%s\" board." % (board.name)
    server = Server(boardName, board)
    socket = QSocketNotifier(sys.stdin.fileno(), QSocketNotifier.Read)
    socket.activated.connect(server.readStdin)
    if not server.listen(port=9002):
        print "could not listen"
    sys.exit(app.exec_())
