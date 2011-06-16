import sys
sys.path.append(sys.path[0] + "/../")

from sm import SM
from connection import Connection
from PyQt4.QtNetwork import QTcpServer, QTcpSocket
from PyQt4.QtCore import QCoreApplication

class Server(QTcpServer):
    def __init__(self, parent = None):
       QTcpServer.__init__(self, parent)

    def incomingConnection(self, socketDescriptor):
        self.c = Connection(socketDescriptor)
        self.c.socketError.connect(self.socketErrorHandler)
        self.c.start()

    def socketErrorHandler(self, socketError):
        print socketError

if __name__ == "__main__":
    app = QCoreApplication(sys.argv)
    server = Server()
    if not server.listen(port=9002):
        print "could not listen"
    sys.exit(app.exec_())
