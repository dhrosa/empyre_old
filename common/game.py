class Game(object):
    def __init__(self, board):
        self.board = board

class State(object):
    (
        OutOfSync,
        Lobby,
        ChoosingOrder,
        OrderTie,
        InitialPlacement,
        CardExchange,
        Draft,
        Attack,
        AttackerRoll,
        DefenderRoll,
        Fortify,
        GameOver,
    ) = range(1, 12)

    def __init__(self, board, players):
        self.board = board
        self.players = []
        self.substate = Lobby
        self.order = []
        self.currentPlayer = None
