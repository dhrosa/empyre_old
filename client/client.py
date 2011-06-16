import sys
sys.path.append(sys.path[0] + "/../")

from PyQt4.QtCore import QObject, QDataStream, QCoreApplication

from common.network import Message, Connection

class Client(QObject):
    def __init__(self, host, port, parent = None):
        QObject.__init__(self, parent)
        self.connection = Connection()
        self.connection.connectToHost(host, port)
        self.connection.messageReceived.connect(self.printMessage)

    def printMessage(self, msg, args):
        print msg, args

if __name__ == "__main__":
    app = QCoreApplication(sys.argv)
    client = Client("127.0.0.1", 9002)
    while True:
        s = raw_input("")
        if s == "quit":
            sys.exit()
