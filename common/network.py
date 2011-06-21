from PyQt4.QtCore import pyqtSignal, Qt, QObject, QByteArray, QDataStream, QCoreApplication, QBuffer
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
        RollDice,
        ClaimTerritory,
        Draft,
    ) = range(17)

    (
        Ping,
        CurrentState,
        StateChanged,
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

        TurnChanged,
        DiceRolled,
        TerritoryUpdated,
        RemainingTroopsChanged,
    ) = range (100, 128)
        
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
        RollDice: (),
        ClaimTerritory: (str,),
        Draft: (str, int),

        Ping: (),
        CurrentState: (int,),
        StateChanged: (int, int,),
        ReceiveChat: (str, str, int),
        ReceiveWhisper: (str, str, str, int),
        JoinSuccess: (),
        NameTaken: (),
        NameAccepted: (str,str),
        PlayerJoined: (str, int, int, int),
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

        TurnChanged: (str,),
        DiceRolled: (str, int, int),
        TerritoryUpdated: (str, str, int,),
        RemainingTroopsChanged: (int,)
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
    messageSent = pyqtSignal(int, list)
    messageReceived = pyqtSignal(int, list)

    def done(self):
        self.abort()
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
        self.buffer = QBuffer()
        self.buffer.open(QBuffer.ReadWrite)
        self.readyRead.connect(self.readIncomingData)        

    def readIncomingData(self):
        bytesWritten = self.buffer.write(self.readAll())
        self.buffer.seek(0)
        result = self.parse()
        bytesRead = 0
        while result:
            bytesRead += result[2]
            self.messageReceived.emit(*result[:2])
            result = self.parse()
        #remove the successfully parsed data
        size = self.buffer.size()
        self.buffer.close()
        data = self.buffer.data()
        self.buffer.setData(data.right(size - bytesRead))
        self.buffer.open(QBuffer.ReadWrite)
        self.buffer.seek(self.buffer.size())

    def parse(self):
        if self.buffer.bytesAvailable() >= 4:
            stream = QDataStream(self.buffer)
            msg = stream.readInt32()
            args = []
            bytesRead = 4
            for aType in Message.validArgs[msg]:
                if aType == str:
                    if self.buffer.bytesAvailable() < 4:
                        return
                    length = stream.readInt32()
                    if self.buffer.bytesAvailable() < length:
                        return
                    args.append(stream.readRawData(length))
                    bytesRead += 4 + length
                elif aType == int:
                    if self.buffer.bytesAvailable() < 4:
                        return
                    args.append(stream.readInt32())
                    bytesRead += 4
            return (msg, args, bytesRead)

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

