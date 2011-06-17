from PyQt4.QtCore import pyqtSignal, Qt, QObject, QByteArray, QDataStream
from PyQt4.QtNetwork import QTcpSocket

class Message(object):
    (
        RequestState,
        Join,
        Rejoin,
        RequestName,
        ChangeName,
        ChangeColor,
        SendChat,
        SendWhisper,
    ) = range(8)

    (
        CurrentState,
        JoinSuccess,
        NameTaken,
        NameAccepted,
        PlayerJoined,
        ColorChanged,
        NameChanged,
        NameChangeSuccess,
        ReceiveChat,
        ReceiveWhisper,
    ) = range (100, 110)
        
    validArgs = {
        RequestState: (),
        CurrentState: (),
        Join: (),
        RequestName: (str,),
        Rejoin: (str,),
        ChangeName: (str,),
        ChangeColor: (int, int, int),
        SendChat: (str,),
        SendWhisper: (str, int),
        
        CurrentState: (),
        NameTaken: (),
        JoinSuccess: (),
        NameAccepted: (str,),
        PlayerJoined: (str,),
        ColorChanged: (str, int, int, int),
        NameChanged: (str, str),
        NameChangeSuccess: (),
        ReceiveChat: (str, str),
        ReceiveWhisper: (str, str),
    }

    @staticmethod
    def argMatch(msg, args):
        try:
            valid = Message.validArgs[msg]
            for i, a in enumerate(args):
                if not type(a) == valid[i]:
                    return False
        except:
            return False
        return True

class Connection(QTcpSocket):
    socketError = pyqtSignal(int)
    closed = pyqtSignal(QObject)
    messageSent = pyqtSignal(int, list)
    messageReceived = pyqtSignal(int, list)

    def __emitError(self, err):
        if err == self.RemoteHostClosedError:
            self.done()
            return
        self.socketError.emit(int(err))

    def done(self):
        self.closed.emit(self)

    def __init__(self, id = None, parent = None):
        QTcpSocket.__init__(self, parent)
        if id:
            if not self.setSocketDescriptor(id):
                self.done()
                return
            self.id = id
        self.player = None
        self.setSocketOption(self.LowDelayOption, True)
        self.error.connect(self.__emitError, Qt.DirectConnection)
        self.readyRead.connect(self.receiveMessage, Qt.DirectConnection)

    def waitForBytes(self, n):
        while self.bytesAvailable() < n:
            if not self.waitForReadyRead(10000):
                self.done()

    def sendMessage(self, msg, args, id = None):
        if id:
            if self.socketDescriptor() != id:
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
        self.messageSent.emit(msg, args)

    def receiveMessage(self):
        stream = QDataStream(self)
        self.waitForBytes(4)
        msg = stream.readInt32()
        argTypes = Message.validArgs[msg]
        args = []
        for aType in argTypes:
            if aType == str:
                self.waitForBytes(4)
                length = stream.readInt32()
                self.waitForBytes(length)
                args.append(stream.readRawData(length))
            elif aType == int:
                self.waitForBytes(4)
                args.append(stream.readInt32())        
        self.messageReceived.emit(msg, args)
        if self.bytesAvailable() > 4:
            self.readyRead.emit()
