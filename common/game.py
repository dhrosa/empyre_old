class GameState(object):
    def __init__(self, board, players):
        self.board = board
        self.players = players
        self.occupation = {}
        self.turnOrder = []
