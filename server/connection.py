from PyQt4.QtCore import pyqtSignal, QThread, QByteArray, QDataStream, QCoreApplication
from PyQt4.QtNetwork import QTcpSocket

class Connection(QThread):
    socketError = pyqtSignal(int)

    def __init__(self, id, parent = None):
        QThread.__init__(self, parent)
        self.socket = QTcpSocket()
        self.id = id
        self.finished.connect(QCoreApplication.quit)
        if not self.socket.setSocketDescriptor(self.id):
            print "hi"
            self.socketError.emit(self.socket.error())
            return
        self.socket.setSocketOption(QTcpSocket.LowDelayOption, True)

    def run(self):
        self.socket.waitForConnected(30000)
        print self.socket.state()
        payload = "Hello world!"
        data = QByteArray()
        stream = QDataStream(data, QTcpSocket.WriteOnly)
        stream.writeInt32(len(payload))
        stream.writeRawData(payload)
        self.socket.write(data)
        print self.socket.state()
        self.socket.waitForBytesWritten(30000)
        print self.socket.state()
        self.socket.disconnectFromHost()
        self.socket.waitForDisconnected(5000)
        return
