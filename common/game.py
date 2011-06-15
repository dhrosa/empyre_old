class Game(object):
    def __init__(self, board):
        self.board = board

class State(object):
    (
        OutOfSync,
        Lobby,
        ChoosingOrder,
        InitialPlacement,
        InitialDraft,
        Draft,
        Attack,
        AttackerRoll,
        DefenderRoll,
        Victory,
        Fortify,
        GameOver,
    ) = range(12)

class Action(object):
    (
        AddPlayer,
        RemovePlayer,
        StartGame,
        RollDice,
        ExchangeCards,
        PlaceTroops,
        Attack,
        Retreat,
        EndAttack,
        MoveTroops,
        Fortify,
        EndTurn,
     ) = range(12)

    validArgs = {
        AddPlayer: (str, int),
        RemovePlayer: (str),
        StartGame: (),
        RollDice: (),
        ExchangeCards: (int, int, int),
        PlaceTroops: (str, int),
        Attack: (str, str, int),
        Retreat: (),
        MoveTroops: (int),
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
