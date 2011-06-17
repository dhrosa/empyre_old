class GameState(object):
    def __init__(self):
        self.players = []
        self.clientPlayer = None

    def player(self, name):
        for p in self.players:
            if p.name == name:
                return p
