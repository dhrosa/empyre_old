import sys
sys.path.append(sys.path[0] + "/../")

from PyQt4.QtCore import QObject, QDataStream, QCoreApplication
from PyQt4.QtNetwork import QTcpSocket

from common.game import Message

def waitForBytes(socket, size):
    while socket.bytesAvailable() < size:
        pass

QTcpSocket.waitForBytes = waitForBytes

class Client(QObject):
    def __init__(self, socket, parent = None):
        QObject.__init__(self, parent)
        self.socket = socket

    def handle(self):
        pass

if __name__ == "__main__":
    app = QCoreApplication(sys.argv)
    socket = QTcpSocket()
    socket.connectToHost("127.0.0.1", 9002)
    socket.waitForReadyRead()
    socket.waitForBytes(4)
    stream = QDataStream(socket)
    msg = stream.readInt32()
    if msg == Message.Chat:
        socket.waitForBytes(4)
        size = stream.readInt32()
        socket.waitForBytes(size)
        player = stream.readRawData(size)
        size = stream.readInt32()
        socket.waitForBytes(size)
        text = stream.readRawData(size)
        print player + ": " + text
