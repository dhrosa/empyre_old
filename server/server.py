#! /usr/bin/python
import sys
sys.path.append(sys.path[0] + "/../")

from sm import SM
from common.game import State, Action
from common.network import Message, Connection
from common.board import loadBoard

from PyQt4.QtNetwork import QTcpServer, QTcpSocket
from PyQt4.QtCore import QCoreApplication, pyqtSignal, QThread

class Server(QTcpServer):
    sendReady = pyqtSignal(int, list)
    sendReadySpecific = pyqtSignal(int, list, int)

    def __init__(self, boardName, board, parent = None):
       QTcpServer.__init__(self, parent)
       self.boardName = boardName
       self.connections = []
       self.sm = SM(board)
       self.chatHistory = []

    def send(self, msg, args):
        self.sendReady.emit(msg, args)

    def sendTo(self, id, msg, args):
        self.sendReadySpecific.emit(msg, args, id)

    def sendExcept(self, id, msg, args):
        for c in self.connections:
            if c and c.valid and c.id != id:
                self.sendTo(c.id, msg, args)

    def incomingConnection(self, socketDescriptor):
        c = Connection(socketDescriptor)
        c.socketError.connect(self.socketErrorHandler)
        self.connections.append(c)
        thread = QThread(self)
        c.moveToThread(thread)
        QCoreApplication.instance().aboutToQuit.connect(thread.quit)
        c.closed.connect(thread.quit)
        c.closed.connect(self.handleDisconnect)
        c.destroyed.connect(self.pruneConnections)
        thread.finished.connect(thread.deleteLater)
        c.messageReceived.connect(self.handleMessage)
        self.sendReady.connect(c.sendMessage)
        self.sendReadySpecific.connect(c.sendMessage)
        thread.start()
        
    def socketErrorHandler(self, socketError):
        print socketError

    def pruneConnections(self):
        self.connections = [c for c in self.connections if c]

    def handleDisconnect(self, conn):
        if conn.player:
            print "%s has disconnected." % (conn.player)
            if self.sm.substate == State.Lobby:
                self.sm.next(Action.RemovePlayer, [conn.player.name])
                self.send(Message.PlayerLeft, [conn.player.name])
        else:
            print "Anonymous client disconnected."
        conn.deleteLater()        

    def handleMessage(self, msg, args):
        conn = self.sender()
        if not conn.player:
            if msg == Message.Join:
                print "%s connected." % (conn.peerAddress().toString())
                self.sendTo(conn.id, Message.JoinSuccess, [])

            elif msg == Message.RequestBoardName:
                self.sendTo(conn.id, Message.LoadBoard, [self.boardName])

            elif msg == Message.RequestName:
                name = str(args[0])
                print "%s requested the name \"%s\"." % (conn.peerAddress().toString(), name)
                if not self.sm.next(Action.AddPlayer, [name]):
                    print "Name taken."
                    self.sendTo(conn.id, Message.NameTaken, [])
                else:
                    print "%s has been granted the name \"%s\"." % (conn.peerAddress().toString(), name)
                    conn.player = self.sm.players[-1]
                    self.sendTo(conn.id, Message.NameAccepted, [name])
                    self.sendExcept(conn.id, Message.PlayerJoined, [name])
        else:
            if msg == Message.SendChat:
                text = str(args[0])
                print "%s: %s" % (conn.player.name, text)
                self.chatHistory.append([conn.player, text])
                self.send(Message.ReceiveChat, [conn.player.name, text])

            elif msg == Message.ChangeName:
                before = conn.player.name
                after = str(args[0])
                if before == after:
                    return
                for player in self.sm.players:
                    if player == conn.player:
                        continue
                    if player.name == after:
                        self.sendTo(conn.id, Message.NameTaken, [])
                        return
                conn.player.name = after
                print "%s changed their name to %s." % (before, after)
                self.sendTo(conn.id, Message.NameChangeSuccess, [conn.player.name])
                self.send(Message.NameChanged, [before, after])                

            elif msg == Message.ChangeColor:
                color = args
                player = conn.player
                player.color = color
                print "%s changed their color to (%d, %d, %d)" % (player.name, color[0], color[1], color[2])
                self.send(Message.ColorChanged, [player.name] + color)

            elif msg == Message.RequestPlayerList:
                self.sendTo(conn.id, Message.BeginPlayerList, [])
                for p in self.sm.players:
                    self.sendTo(conn.id, Message.PlayerInfo, [p.name] + list(p.color))
                self.sendTo(conn.id, Message.EndPlayerList, [])

            elif msg == Message.RequestChatHistory:
                for line in self.chatHistory:
                    self.sendTo(conn.id, Message.ReceiveChat, [line[0].name, line[1]])

    def startGame(self):
        if not self.sm.next(Action.StartGame):
            print "Need more players to start."
        else:
            self.send(Message.GameStarted, [])
    
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
    if not server.listen(port=9002):
        print "could not listen"
    while True:
        s = raw_input("")
        if s.lower() == 'quit':
            sys.exit(0)
        if s.lower() == "start":
            server.startGame()
