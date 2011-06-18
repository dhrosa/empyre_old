from common.game import Player

class GameState(object):
    def __init__(self):
        self.players = []
        self.clientPlayer = None

    def addPlayer(self, name):
        self.players.append(Player(name))

    def getPlayer(self, name):
        for i in range(len(self.players)):
            if self.players[i].name == name:
                return self.players[i]

    def removePlayer(self, name):
        for i in range(len(self.players)):
            if self.players[i].name == name:
                del self.players[i]
                return
