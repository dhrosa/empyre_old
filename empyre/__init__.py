import sip
sip.setapi("QString", 2)

import os
import os.path
home = os.path.expanduser("~")
configDir = os.path.join(home, ".empyre")
if not os.path.exists(configDir):
    os.mkdir(configDir)
serverConfigDir = os.path.join(configDir, "server")
if not os.path.exists(serverConfigDir):
    os.mkdir(serverConfigDir)
clientConfigDir = os.path.join(configDir, "client")
if not os.path.exists(clientConfigDir):
    os.mkdir(clientConfigDir)
    
import inspect

from PyQt4.QtCore import QDateTime

class Player(object):
    def __init__(self, name):
        self.name = name
        self.color = (0, 0, 0)
        self.isPlaying = True
        self.cards = []
        self.password = ""
        self.ready = False

    def __str__(self):
        return self.name

    def cardCount(self):
        return len(self.cards)

class State(object):
    (
        OutOfSync,
        Lobby,
        InitialPlacement,
        InitialDraft,
        Draft,
        Attack,
        Fortify,
        GameOver,
    ) = range(8)

    @staticmethod
    def toString(state):
        return stateToString[state]

stateToString = dict([(m[1], m[0]) for m in inspect.getmembers(State) if m[0][0].isupper()])

class Action(object):
    (
        AddPlayer,
        RemovePlayer,
        StartGame,
        ExchangeCards,
        PlaceTroops,
        Attack,
        EndAttack,
        Fortify,
        EndTurn,
     ) = range(9)

    validArgs = {
        AddPlayer: (str,),
        RemovePlayer: (str,),
        StartGame: (),
        ExchangeCards: (int, int, int),
        PlaceTroops: (str, int),
        Attack: (str, str, int),
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

    @staticmethod
    def toString(action):
        return actionToString[action]

actionToString = dict([(m[1], m[0]) for m in inspect.getmembers(Action) if m[0][0].isupper()])
