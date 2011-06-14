class Game(object):
    def __init__(self, board):
        self.board = board

class State(object):
    (
        OutOfSync,
        Lobby,
        ChoosingOrder,
        InitialPlacement,
        CardExchange,
        Draft,
        Attack,
        AttackerRoll,
        DefenderRoll,
        Fortify,
        GameOver,
    ) = range(1, 12)

    def __init__(self, board):
        self.board = board
        self.players = []
        self.livePlayers = []
        self.currentPlayer = None
        self.firstPlayer = None
        self.tiedPlayers = []
        self.substate = Lobby
        self.diceRolls = []
        self.occupation = {}
        self.remainingTroops = 0

    def playerNames(self):
        return [p.name for p in self.players]

    def playerCount(self):
        return len(self.players)

    def tiedPlayerCount(self):
        return len(self.tiedPlayers)

    def livePlayerCount(self):
        return len(self.livePlayers())

    def territoryNames(self):
        return [t.name for t in self.board.territories]

    def isValidTerritory(self, t):
        return t in self.territoryNames()

class Action(object):
    (
        AddPlayer,
        RemovePlayer,
        StartGame,
        RollDice,
        ExchangeCards,
        PlaceTroops,
        Attack,
        MoveTroops,
        Fortify,
        EndTurn,
     ) = range(10)

    validArgs = {
        AddPlayer: (str, int),
        RemovePlayer: (str),
        StartGame: (),
        RollDice: (),
        ExchangeCards: (int, int, int),
        PlaceTroops: (str, int),
        Attack: (str, str, int),
        MoveTroops: (str, str, int),
        Fortify: (str, str, int),
        EndTurn: (),
    }

    @staticmethod
    def argMatch(action, args):
        try:
            valid = self.validArgs[action]
            for i, a in enumerate(args):
                if not type(a) == valid[i]:
                    return False
        except:
            return False
        return True
