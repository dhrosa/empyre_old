from PyQt4.QtCore import QObject, QDataStream, QCoreApplication
from PyQt4.QtNetwork import QTcpSocket

class Client(QObject):
    def __init__(self, socket, parent = None):
        QObject.__init__(self, parent)
        self.socket = socket

    def handle(self):
        pass

if __name__ == "__main__":
    import sys
    app = QCoreApplication(sys.argv)
    socket = QTcpSocket()
    socket.connectToHost("127.0.0.1", 9002)
    socket.waitForReadyRead()
    while socket.bytesAvailable() < 4:
        pass
    stream = QDataStream(socket)
    size = stream.readInt32()
    while socket.bytesAvailable() < size:
        pass
    print stream.readRawData(size)
