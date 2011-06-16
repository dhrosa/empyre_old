class Player(object):
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.isPlaying = True
        self.cards = []

    def __str__(self):
        return self.name

    def cardCount(self):
        return len(self.cards)

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
        Fortify,
        GameOver,
    ) = range(11)

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
        Fortify,
        EndTurn,
     ) = range(11)

    validArgs = {
        AddPlayer: (str, int),
        RemovePlayer: (str),
        StartGame: (),
        RollDice: (),
        ExchangeCards: (int, int, int),
        PlaceTroops: (str, int),
        Attack: (str, str, int),
        Retreat: (),
        EndAttack: (),
        Fortify: (str, str, int),
        EndTurn: (),
    }

    @staticmethod
    def argMatch(action, args):
        try:
            valid = Action.validArgs[action]
            for i, a in enumerate(args):
                if not type(a) == valid[i]:
                    return False
        except:
            return False
        return True

class Message(object):
    (
        RequestState,
        CurrentState,
        Chat,
        Whisper,
    ) = range(4)
    
    validArgs = {
        RequestState: (),
        CurrentState: (),
        Chat: (str, str),
        Whisper: (str, str, str),
    }

    @staticmethod
    def argMatch(msg, args):
        try:
            valid = Message.validArgs[msg]
            for i, a in enumerate(args):
                if not type(a) == valid[i]:
                    return False
        except:
            return False
        return True
