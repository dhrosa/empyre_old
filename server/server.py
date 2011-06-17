#! /usr/bin/python
import sys
sys.path.append(sys.path[0] + "/../")

from sm import SM
from common.game import State, Action
from common.network import Message, Connection

from PyQt4.QtNetwork import QTcpServer, QTcpSocket
from PyQt4.QtCore import QCoreApplication, pyqtSignal, QThread

class Server(QTcpServer):
    sendReady = pyqtSignal(int, list)
    sendReadySpecific = pyqtSignal(int, list, int)

    def __init__(self, parent = None):
       QTcpServer.__init__(self, parent)
       self.connections = []
       self.sm = SM(None)

    def send(self, msg, args):
        self.sendReady.emit(msg, args)

    def sendTo(self, id, msg, args):
        self.sendReadySpecific.emit(msg, args, id)

    def incomingConnection(self, socketDescriptor):
        c = Connection(socketDescriptor)
        c.socketError.connect(self.socketErrorHandler)
        self.connections.append(c)
        thread = QThread(self)
        thread.finished.connect(thread.deleteLater)
        c.moveToThread(thread)
        QCoreApplication.instance().aboutToQuit.connect(thread.quit)
        c.closed.connect(thread.quit)
        c.closed.connect(self.removeConnection)
        c.messageReceived.connect(self.handleMessage)
        self.sendReady.connect(c.sendMessage)
        self.sendReadySpecific.connect(c.sendMessage)
        thread.start()
        
    def socketErrorHandler(self, socketError):
        print socketError

    def removeConnection(self, conn):
        if conn.player:
            print "%s has disconnected." % (conn.player)
            if self.sm.substate == State.Lobby:
                self.sm.next(Action.RemovePlayer, [conn.player.name])
        else:
            print "Anonymous client disconnected."
        self.connections.remove(conn)

    def handleMessage(self, msg, args):
        conn = self.sender()
        if not conn.player:
            if msg == Message.Join:
                print "%s connected." % (conn.peerAddress().toString())
                self.sendTo(conn.id, Message.JoinSuccess, [])

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
                    self.send(Message.PlayerJoined, [name])
        else:
            if msg == Message.SendChat:
                text = str(args[0])
                print "%s: %s" % (conn.player.name, text)
                self.send(Message.ReceiveChat, [conn.player.name, text])

            elif msg == Message.ChangeName:
                before = str(args[0])
                after = str(args[1])
                if before == after:
                    return
                for player in self.sm.players:
                    if player == conn.player:
                        continue
                    if player.name == after:
                        self.sendTo(conn.id, Message.NameTaken, [])
                        return
                conn.player.name = after
                self.sendTo(conn.id, Message.NameChangeSuccess, [conn.player.name])
                self.send(Message.NameChanged, [before, after])                

            elif msg == Message.ChangeColor:
                color = args
                player = conn.player
                player.color = color
                print "%s changed their color to (%d, %d, %d)" % (player.name, color[0], color[1], color[2])
                self.send(Message.ColorChanged, [player.name] + color)

if __name__ == "__main__":
    app = QCoreApplication(sys.argv)
    server = Server()
    if not server.listen(port=9002):
        print "could not listen"
    while True:
        s = raw_input("")
        if s.lower() == 'quit':
            sys.exit(0)
