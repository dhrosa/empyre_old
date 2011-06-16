import sys
sys.path.append(sys.path[0] + "/../")

from sm import SM
from connection import Connection
from common.game import Message

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
        self.updated.connect(c.sendMessage)
        thread.start()
        
    def socketErrorHandler(self, socketError):
        print socketError

    def removeConnection(self, conn):
        self.connections.remove(conn)

if __name__ == "__main__":
    app = QCoreApplication(sys.argv)
    server = Server()
    if not server.listen(port=9002):
        print "could not listen"
    while True:
        s = raw_input("")
        if s.lower() == 'quit':
            sys.exit(0)
