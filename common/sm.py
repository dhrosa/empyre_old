from game import State, Action

def diceRoll(n):
    return 7

class SM(object):
    def __init__(self):
        self.state = State()

    def nextPlayer(self, selection = None):
        if not selection:
            selection = self.state.livePlayers
            i = (selection.index(self.currentPlayer) + 1) % len(selection)
        return selection[i]

    def draftCount(self, player):
        return 1

    def next(self, action, args):
        s = self.state.substate:
        if not Action.argMatch(action, args):
            return False
        if s == State.Lobby:
            if action == Action.AddPlayer:
                if args[0] in self.state.playerNames():
                    return False
                self.state.players.append(Player(*args))
                return True
            elif action == Action.StartGame:
                if len(self.state.players) < 2:
                    return False
                self.state.currentPlayer = self.state.players[0]
                self.state.livePlayers = self.state.players
                self.state.substate = State.ChoosingOrder
                return True
    
        elif s == State.ChoosingOrder:
            if action == Action.RollDice:
                self.state.diceRolls.append(diceRoll(2))
                if len(self.state.diceRolls) == self.state.tiedPlayerCount():
                    highest = max(self.state.diceRolls)
                    if self.state.diceRolls.count(highest) > 1:
                        self.state.tiedPlayers = []
                        for i, p in enumerate(self.state.tiedPlayers):
                            if self.state.diceRolls[i] == highest:
                                self.state.tiedPlayers.append(p)
                        self.state.diceRolls = []
                        return True
                    else:
                        index = self.state.diceRolls.index(highest)
                        self.state.currentPlayer = self.state.tiedPlayers[i]
                        self.state.firstPlayer = self.state.currentPlayer
                        self.state.diceRolls = []
                        self.state.substate = State.InitialPlacement
                        return True
                else:
                    self.state.currentPlayer = self.nextPlayer(self.state.tiedPlayers)
                    return True
                
        elif s == State.InitialPlacement:
            if action == Action.PlaceTroops:
                t = args[0]
                if not t in self.state.territoryNames():
                    return False
                if t in self.state.occupation.keys():
                    return False
                self.state.occupation[t] = (self.state.currentPlayer, 1)
                self.state.currentPlayer = self.nextPlayer()
                if self.state.currentPlayer == self.state.firstPlayer():
                    self.state.substate = Draft
                return True

        elif s == State.CardExchange:
            pass
        
        elif s == State.Draft:
            pass
