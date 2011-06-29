from PyQt4.QtCore import pyqtSignal, Qt, QObject, QByteArray, QDataStream, QCoreApplication, QBuffer
from PyQt4.QtNetwork import QTcpSocket
import inspect

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
        ClaimTerritory,
        Draft,
        Attack,
        EndAttack,
        Fortify,
        EndTurn,
    ) = range(20)

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
        
        BeginTiedPlayerList,
        TiedPlayer,
        EndTiedPlayerList,
        TurnChanged,
        DiceRolled,
        TerritoryUpdated,
        RemainingTroopsChanged,
        Attacked,
        ReceiveCard,
        CardAwarded,
    ) = range (100, 134)
        
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
        ClaimTerritory: (str,),
        Draft: (str, int),
        Attack: (str, str, int),
        EndAttack: (),
        Fortify: (str, str, int),
        EndTurn: (),

        Ping: (),
        CurrentState: (int,),
        StateChanged: (int, int,),
        ReceiveChat: (str, str, long),
        ReceiveWhisper: (str, str, str, long),
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

        BeginTiedPlayerList: (),
        TiedPlayer: (str,),
        EndTiedPlayerList: (),
        TurnChanged: (str,),
        DiceRolled: (str, int, int, int),
        TerritoryUpdated: (str, str, int,),
        RemainingTroopsChanged: (int,),
        Attacked: (str, str, str),
        ReceiveCard: (str, int),
        CardAwarded: (str,),
    }

    @staticmethod
    def argMatch(msg, args):
        try:
            valid = Message.validArgs[msg]
            for i, a in enumerate(args):
                if type(a) == unicode and valid[i] == str:
                    args[i] = str(args[i])
                    continue
                if not type(a) == valid[i]:
                    return False
        except:
            return False
        return True

    @staticmethod
    def toString(message):
        return messageToString[message]

messageToString = dict([(m[1], m[0]) for m in inspect.getmembers(Message) if m[0][0].isupper()])


class Connection(QTcpSocket):
    messageSent = pyqtSignal(int, list)
    messageReceived = pyqtSignal(int, list)
    messageReceived2 = pyqtSignal()

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

    def abort(self):
        super(Connection, self).abort()

    def readIncomingData(self):
        bytesWritten = self.buffer.write(self.readAll())
        self.buffer.seek(0)
        result = self.parse()
        bytesRead = 0
        while result:
            bytesRead += result[2]
            self.messageReceived.emit(*result[:2])
            self.messageReceived2.emit()
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
                elif aType == long:
                    if self.buffer.bytesAvailable() < 8:
                        return
                    args.append(stream.readInt64())
                    bytesRead += 8
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
            elif type(arg) == long:
                stream.writeInt64(arg)
        self.write(data)
        self.messageSent.emit(msg, args)

