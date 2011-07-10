from PyQt4.QtCore import pyqtSignal, Qt, QObject, QByteArray, QDataStream, QCoreApplication, QBuffer
from PyQt4.QtNetwork import QTcpSocket

from empyre import Enumerated, makeValidatedEnumeration

import logging

log = logging.getLogger("network")

class Message(Enumerated):
    pass

makeValidatedEnumeration(Message, {
    "Pong": (),
    "RequestState": (),
    "SendChat": (str,),
    "SendWhisper": (str, str),
    "WhisperError": (),
    "Join": (),
    "RequestName": (str,),
    "Rejoin": (str,),
    "RequestBoardName": (),
    "RequestPlayerList": (),
    "RequestChatHistory": (),
    "RequestOwnershipList": (),
    "RequestCardList": (),
    "RequestCurrentPlayer": (),
    "RequestRemainingTroops": (),
    "ChangeName": (str,),
    "ChangeColor": (int, int, int),

    "ReadyToPlay": (),
    "ClaimTerritory": (str,),
    "ExchangeCards": (int, int, int),
    "Draft": (str, int),
    "Attack": (str, str, int),
    "EndAttack": (),
    "Fortify": (str, str, int),
    "EndTurn": (),

    "Ping": (),
    "CurrentState": (int,),
    "StateChanged": (int, int,),
    "ReceiveChat": (str, str, long),
    "ReceiveWhisper": (str, str, str, long),
    "JoinSuccess": (),
    "NameTaken": (),
    "NameAccepted": (str,str),
    "PlayerJoined": (str, int, int, int),
    "GameInProgress": (),
    "IncorrectPassword": (),
    "RejoinSuccess": (str,),
    "PlayerRejoined": (str,),
    "BeginPlayerList": (),
    "PlayerInfo": (str, int, int, int, int),
    "EndPlayerList": (),
    "LoadBoard": (str,),
    "BeginOwnershipList": (),
    "Ownership": (str, str, int),
    "EndOwnershipList": (),
    "BeginCardList": (),
    "Card": (str, int),
    "EndCardList": (),
    "CurrentPlayer": (str,),

    "PlayerLeft": (str,),
    "PlayerLeftDuringGame": (str,),
    "ColorChanged": (str, int, int, int),
    "NameChangeTaken": (),
    "NameChangeSuccess": (str,),
    "NameChanged": (str, str),
    "GameStarted": (),

    "BeginTiedPlayerList": (),
    "TiedPlayer": (str,),
    "EndTiedPlayerList": (),
    "TurnChanged": (str,),
    "DiceRolled": (str, int, int, int),
    "TerritoryUpdated": (str, str, int,),
    "RemainingTroopsChanged": (int,),
    "MustExchangeCards": (),
    "CardsExchanged": (str, int, int, int),
    "Attacked": (str, str, str),
    "ReceiveCard": (str, int),
    "CardAwarded": (str,),
    "PlayerEliminated": (str,),
    })

class Connection(QTcpSocket):
    messageSent = pyqtSignal(int, list)
    messageReceived = pyqtSignal(int, list)
    messageReceived2 = pyqtSignal()

    def __init__(self, id = None, client = False, parent = None):
        QTcpSocket.__init__(self, parent)
        if id:
            if not self.setSocketDescriptor(id):
                self.done()
                return
            self.id = id
        self.player = None
        self.client = client
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
            msg, args = result[:2]
            if self.client:
                log.debug("Received %s %s", msg, args)
            elif self.player and self.player.name:
                log.debug("Received %s %s from %s", msg, args, self.player)
            else:
                log.debug("Received %s %s from %s", msg, args, self.peerAddress().toString())
            self.messageReceived.emit(msg, args)
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
            msg = Message.fromInt(stream.readInt32())
            if msg == None:
                return
            args = []
            bytesRead = 4
            for aType in msg.argTypes:
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
        msg = Message.fromInt(msg)
        if not msg.validateArgs(args):
            log.warning("Message %d and args %s have invalid types. Message not sent.", msg, args)
            return
        if self.client:
            log.debug("Sending %s %s", msg, args)
        elif self.player and self.player.name:
            log.debug("Sending %s %s to %s", msg, args, self.player)
        else:
            log.debug("Sending %s %s to %s", msg, args, self.peerAddress().toString())
        data = QByteArray()
        stream = QDataStream(data, self.WriteOnly)
        stream.writeInt32(int(msg))
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

