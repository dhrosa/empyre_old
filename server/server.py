import sys
sys.path.append(sys.path[0] + "/../")

from sm import SM
from connection import Connection
from PyQt4.QtNetwork import QTcpServer, QTcpSocket
from PyQt4.QtCore import QCoreApplication

class Server(QTcpServer):
    def __init__(self, parent = None):
       QTcpServer.__init__(self, parent)
       self.connections = {}

    def incomingConnection(self, socketDescriptor):
        c = Connection(socketDescriptor)
        c.socketError.connect(self.socketErrorHandler)
        c.finished.connect(self.removeConnection)
        self.connections[socketDescriptor] = c
        c.start()
        
    def socketErrorHandler(self, socketError):
        print socketError

    def removeConnection(self):
        del self.connections[self.sender().id]

if __name__ == "__main__":
    app = QCoreApplication(sys.argv)
    server = Server()
    if not server.listen(port=9002):
        print "could not listen"
    sys.exit(app.exec_())
