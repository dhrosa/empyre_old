from PyQt4.QtCore import pyqtSignal, Qt, QObject, QByteArray, QDataStream, QMetaType
from PyQt4.QtNetwork import QTcpSocket

from common.game import Action

class Connection(QTcpSocket):
    socketError = pyqtSignal(int)
    closed = pyqtSignal(QObject)

    def __emitError(self, err):
        if err == self.RemoteHostClosedError:
            self.done()
            return
        self.socketError.emit(int(err))

    def done(self):
        self.closed.emit(self)

    def __init__(self, id, parent = None):
        QTcpSocket.__init__(self, parent)
        if not self.setSocketDescriptor(id):
            self.deleteLater()
            return
        self.setSocketOption(self.LowDelayOption, True)
        self.error.connect(self.__emitError, Qt.DirectConnection)
        
    def sendMessage(self, msg, args):
        if not self.waitForConnected():
            self.deleteLater()
            return
        data = QByteArray()
        stream = QDataStream(data, self.WriteOnly)
        stream.writeInt32(msg)
        for arg in args:
            if type(arg) == str:
                stream.writeInt32(len(arg))
                stream.writeRawData(arg)
            elif type(arg) == int:
                stream.writeInt32(arg)
        self.write(data)
