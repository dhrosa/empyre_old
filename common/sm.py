from game import *

class SM(object):
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
        AddPlayer: (str),
        RemovePlayer: (str),
        StartGame: (),
        RollDice: (),
        ExchangeCards: (int, int, int),
        PlaceTroops: 2,
        Attack: 2,
        MoveTroops: 3,
        Fortify: 3,
        EndTurn: 0,
    }

    def __init__(self):
        self.state = State()

    def argMatch(self, action, args):
        return len(args) == argCounts[action]

    def next(self, action, args):
        s = self.state.substate:
        if not argMatch(action, args):
            return
        if s == State.Lobby:
            if action == AddPlayer:
                if 
