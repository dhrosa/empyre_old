from PyQt4.QtCore import pyqtSignal, Qt, QObject, QByteArray, QDataStream, QCoreApplication, QBuffer
from PyQt4.QtNetwork import QTcpSocket

from empyre import Enumerated, makeValidatedEnumeration

import logging

log = logging.getLogger("network")

class Message(Enumerated):
    """Represents a message to be sent between clients and the server.
    
    Client to server messages:
    Pong -- See Ping.
    RequestState -- Request the current state of the state.
    SendChat -- Send a chat message. Args: the message
    SendWhisper -- Send a private message to a player. Args: the target player name, the message
    Join -- Request to log into the server.
    RequestName -- Send your desired player name. Args: your desired name
    Rejoin -- Request to rejoin an ongoing game. Args: your password
    RequestBoardName -- Request the name of the game's board.
    RequestPlayerList -- Request a list of all the players. See BeginPlayerList.
    RequestChatHistory -- Request a history of all the chat messages. See RecieveChat.
    RequestOwnershipList -- Request a list of all of the territories' ownership status. See BeginOwnershipList.
    RequestCardList -- Request the number of cards each player has, and what cards you have. See BeginCardList, Card.
    RequestCurrentPlayer -- Request the name of the current player.
    RequestRemainingTroops -- Request the number of remaining troops.
    ChangeName -- Ask to change your name. Args: your desired new name
    ChangeColor -- Ask to change your color. Args: R, G, and B values
    
    ReadyToPlay -- You are ready to start the game.
    ClaimTerritory -- Claim an open territory. Args: territory name.
    ExchangeCards -- Exchange 3 cards. Args: the indexes of the cards.
    Draft -- Place troops in a territory. Args: territory name, number of troops.
    Attack -- Attack a territory. Args: attacking territory, victim territory, number of troops.
    EndAttack -- End your attack phase.
    Fortify -- Fortify troops from one territory to another. Args: from territory name, to territory name, number of troops
    EndTurn -- End your turn.

   
    Server to client messages:
    Ping -- This message is sent periodically by the server to check if the client is still responding. The client should respond with a Pong.
    CurrentState -- The current game state. Args: the state as an integer.
    StateChanged -- The current game state has changed. Args: the old and new states as integers .
    ReceiveChat -- Sends a chat message to the clients. Args: sender name, message, UTC timestamp.
    ReceiveWhisper -- Sends a whisper to the clients. Args: sender name, target name, message, UTC timestamp.
    JoinSuccess -- Successful response to Join.
    NameTaken -- The client's requested name is taken.
    NameAccepted -- The client's name has been accepted. Args: the client's name, password to rejoin game.
    PlayerJoined -- A new player has joined the game. Args: player name, R, G, and B values of player's color.
    GameInProgress -- A game is already in progress. Client must supply password to rejoin.
    IncorrectPassword -- The password is incorrect.
    RejoinSuccess -- The client has successfully rejoined. Args: the player's name
    BeginPlayerList -- Prepare to recieve a list of players.
    PlayerInfo -- Player information. Args: player name, number of cards, R, G, and B values of player's color.
    EndPlayerList -- The player list is complete.
    LoadBoard -- Load the board with this name. Args: the board name.
    BeginOwnershipList -- Prepare to receive a list of territory ownerships.
    Ownership -- Territory information. Args: territory name, owner name, number of troops.
    EndOwnershipList -- Territory ownership list complete.
    BeginCardList -- Prepare to receive a list of your cards.
    Card -- Your card. Args: bonus territory name, unit type.
    EndCardList -- Card list complete.
    CurrentPlayer -- The current player. Args: the current player name.
    PlayerLeft -- A player left the lobby. Args: the player name.
    PlayerLeftDuringGame -- A player left mid-game. Args: the player name.
    ColorChanged -- A player changed their color. Args: player name, R, G, and B values of new color.
    NameChangeTaken -- The requested new name was taken.
    NameChangeSuccess -- You have been granted your new name. Args: new name.
    NameChanged -- A player changed their name. Args: old name, new name.

    TurnChanged -- It is someone else's turn now. Args: the current player's name.
    TerritoryUpdated -- Territory ownership changed. Args: the territory name, owner name, troop count.
    RemainingTroopsChanged -- The number of troops remaining. Args: remaining troops
    MustExchangeCards -- You must exchange cards before playing.
    CardsExchanged -- A player exchanged cards. Args: player name.
    Attacked -- A territory was attacked. Args: attacker name,  attacking territory name, defending territory name, number of troops.
    ReceiveCard -- You've been awarded a card. Args: bonus territory name, unit type.
    CardAwarded -- A player recieved a card. Args: the player name.
    PlayerEliminated -- A player has lost. Args: the player name.
    """
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

    "TurnChanged": (str,),
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
    """Abstracts server-client connections.
    
    Whenever data is received, a Connection attempts to parse a Message and arguments from the data, and emits messageReceived for each parsed message. See QTcpSocket documentation for other members."""
    messageSent = pyqtSignal(int, list)
    """Emitted whenever a message is sent. Arguments: the message type, list of arguments."""
    messageReceived = pyqtSignal(int, list)
    """Emitted whenever a message is recieved. Arguments: the message type, list of arguments."""
    messageReceived2 = pyqtSignal()

    def __init__(self, id = None, client = False, parent = None):
        """Creates a connection.
        
        id -- Optional socket descriptor.
        client -- Whether this connection is opened from the client side or server side.
        parent -- Parent object."""
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
        self.readyRead.connect(self._readIncomingData)        

    def abort(self):
        """Aborts the connection."""
        super(Connection, self).abort()

    def _readIncomingData(self):
        bytesWritten = self.buffer.write(self.readAll())
        self.buffer.seek(0)
        result = self._parse()
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
            result = self._parse()
        #remove the successfully parsed data
        size = self.buffer.size()
        self.buffer.close()
        data = self.buffer.data()
        self.buffer.setData(data.right(size - bytesRead))
        self.buffer.open(QBuffer.ReadWrite)
        self.buffer.seek(self.buffer.size())

    def _parse(self):
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
        """Sends a message.

        msg -- The message type.
        args -- List of message arguments.
        id -- An optional socket descriptor. If specified, then the message will only be sent if this connection's socket descriptor matches id."""
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

