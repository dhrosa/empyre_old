from PyQt4.QtCore import pyqtSignal, Qt, QObject, QByteArray, QDataStream, QCoreApplication
from PyQt4.QtNetwork import QTcpSocket

class Message(object):
    (
        Pong,
        RequestState,
        SendChat,
        WhisperError,
        SendWhisper,
        Join,
        RequestName,
        Rejoin,
        RequestBoardName,
        RequestPlayerList,
        RequestChatHistory,
        ChangeName,
        ChangeColor,

        ReadyToPlay,
    ) = range(14)

    (
        Ping,
        CurrentState,
        ReceiveChat,
        ReceiveWhisper,
        JoinSuccess,
        NameTaken,
        NameAccepted,
        PlayerJoined,
        GameInProgress,
        IncorrectPassword,
        RejoinSuccess,
        PlayerRejoined,
        BeginPlayerList,
        PlayerInfo,
        EndPlayerList,
        LoadBoard,

        PlayerLeft,
        PlayerLeftDuringGame,
        ColorChanged,
        NameChangeTaken,
        NameChangeSuccess,
        NameChanged,
        GameStarted,

        YourTurn,

    ) = range (100, 124)
        
    validArgs = {
        Pong: (),
        RequestState: (),
        SendChat: (str,),
        SendWhisper: (str, str),
        WhisperError: (),
        Join: (),
        RequestName: (str,),
        Rejoin: (str,),
        RequestBoardName: (),
        RequestPlayerList: (),
        RequestChatHistory: (),
        ChangeName: (str,),
        ChangeColor: (int, int, int),

        ReadyToPlay: (),


        Ping: (),
        CurrentState: (),
        ReceiveChat: (str, str, int),
        ReceiveWhisper: (str, str, str, int),
        JoinSuccess: (),
        NameTaken: (),
        NameAccepted: (str,str),
        PlayerJoined: (str,),
        GameInProgress: (),
        IncorrectPassword: (),
        RejoinSuccess: (str,),
        PlayerRejoined: (str,),
        BeginPlayerList: (),
        PlayerInfo: (str, int, int, int),
        EndPlayerList: (),
        LoadBoard: (str,),

        PlayerLeft: (str,),
        PlayerLeftDuringGame: (str,),
        ColorChanged: (str, int, int, int),
        NameChangeTaken: (),
        NameChangeSuccess: (str,),
        NameChanged: (str, str),
        GameStarted: (),

        YourTurn: (int,),
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
    connectionFailed = pyqtSignal()
    messageSent = pyqtSignal(int, list)
    messageReceived = pyqtSignal(int, list)

    def __emitError(self, err):
        if err == self.RemoteHostClosedError:
            self.done()
            return
        self.socketError.emit(int(err))

    def done(self):
        self.abort()
        self.moveToThread(QCoreApplication.instance().thread())
        self.closed.emit(self)

    def __init__(self, id = None, parent = None):
        QTcpSocket.__init__(self, parent)
        self.valid = True
        if id:
            if not self.setSocketDescriptor(id):
                self.done()
                return
            self.id = id
        self.player = None
        self.setSocketOption(self.LowDelayOption, True)
        self.error.connect(self.__emitError, Qt.DirectConnection)
        self.readyRead.connect(self.receiveMessage, Qt.DirectConnection)
        
    def tryConnectToHost(self):
        self.abort()
        self.connectToHost(self.host, self.port)
        if not self.waitForConnected(10000):
            self.connectionFailed.emit()

    def waitForBytes(self, n):
        while self.bytesAvailable() < n:
            if not self.waitForReadyRead(10000):
                self.done()

    def sendMessage(self, msg, args, id = None):
        if id:
            if self.socketDescriptor() != id:
                return
        if not Message.argMatch(msg, args):
            print "Message: %d, args: %s have invalid types. Message not sent." % (msg, args)
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
        if self.bytesAvailable() > 0:
            self.readyRead.emit()

