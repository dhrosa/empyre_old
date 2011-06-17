#! /usr/bin/python
import sys
sys.path.append(sys.path[0] + "/../")

from sm import SM
from common.network import Message, Connection

from PyQt4.QtNetwork import QTcpServer, QTcpSocket
from PyQt4.QtCore import QCoreApplication, pyqtSignal, QThread

class Server(QTcpServer):
    updated = pyqtSignal(int, list)

    def __init__(self, parent = None):
       QTcpServer.__init__(self, parent)
       self.connections = []

    def incomingConnection(self, socketDescriptor):
        c = Connection(socketDescriptor)
        c.socketError.connect(self.socketErrorHandler)
        self.connections.append(c)
        thread = QThread(self)
        thread.finished.connect(thread.deleteLater)
        c.moveToThread(thread)
        c.closed.connect(thread.quit)
        c.closed.connect(self.removeConnection)
        c.messageReceived.connect(self.handleMessage)
        self.updated.connect(c.sendMessage)
        thread.start()
        print "%s connected." % (c.peerAddress().toString())
        
    def socketErrorHandler(self, socketError):
        print socketError

    def removeConnection(self, conn):
        print "client disconnected."
        self.connections.remove(conn)

    def handleMessage(self, msg, args):
        if msg == Message.Chat:
            print "%s: %s" % (args[0], args[1])
            self.updated.emit(Message.Chat, args)

if __name__ == "__main__":
    app = QCoreApplication(sys.argv)
    server = Server()
    if not server.listen(port=9002):
        print "could not listen"
    while True:
        s = raw_input("")
        if s.lower() == 'quit':
            sys.exit(0)
