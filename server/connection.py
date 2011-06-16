from PyQt4.QtCore import pyqtSignal, QThread, QByteArray, QDataStream, QCoreApplication
from PyQt4.QtNetwork import QTcpSocket

class Connection(QThread):
    socketError = pyqtSignal(int)

    def __init__(self, id, parent = None):
        QThread.__init__(self, parent)
        self.id = id


    def run(self):
        self.socket = QTcpSocket()
        if not self.socket.setSocketDescriptor(self.id):
            self.socketError.emit(self.socket.error())
            return
        self.socket.setSocketOption(QTcpSocket.LowDelayOption, True)
        self.socket.waitForConnected(30000)
        payload = "Hello world!"
        data = QByteArray()
        stream = QDataStream(data, QTcpSocket.WriteOnly)
        stream.writeInt32(len(payload))
        stream.writeRawData(payload)
        self.socket.write(data)
        self.socket.waitForBytesWritten(30000)
        self.socket.disconnectFromHost()
        return
