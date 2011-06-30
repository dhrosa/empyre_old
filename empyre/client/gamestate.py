from empyre.game import Player
from PyQt4.QtCore import pyqtSignal, QObject

class GameState(QObject):
    changed = pyqtSignal()

    def __init__(self):
        super(GameState, self).__init__(None)
        self.board = None
        self.players = []
        self.clientPlayer = None
        self.currentPlayer = None
        self.state = None
        self.remainingTroops = 0

    def __setattr__(self, name, value):
        super(GameState, self).__setattr__(name, value)
        self.changed.emit()

    def yourTurn(self):
        return self.clientPlayer == self.currentPlayer

    def playerNames(self):
        return [p.name for p in self.players]

    def setCurrentPlayer(self, name):
        self.currentPlayer = self.getPlayer(name)

    def addPlayer(self, name):
        self.players.append(Player(name))
        return self.players[-1]

    def getPlayer(self, name):
        for i in range(len(self.players)):
            if self.players[i].name == name:
                return self.players[i]

    def removePlayer(self, name):
        for i in range(len(self.players)):
            if self.players[i].name == name:
                del self.players[i]
                return

    def setPlayerName(self, old, new):
        p = self.getPlayer(old)
        if p:
            p.name = new

    def setPlayerColor(self, name, color):
        p = self.getPlayer(name)
        if p:
            p.color = color
