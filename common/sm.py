from game import State, Action
from board import Board, Territory, Region
from random import randint

def diceRoll(n):
    return sorted([randint(1, 6) for i in range(n)])

class SM(object):
    def __init__(self, board):
        self.substate = State.OutOfSync
        self.board = board
        self.players = []
        self.currentPlayer = None
        self.firstPlayer = None
        self.tiedPlayers = []
        self.substate = Lobby
        self.diceRolls = []
        self.remainingTroops = 0
        self.source = None
        self.target = None
        self.awardCard = False
        self.setsExchanged = 0

    def playerNames(self):
        return [p.name for p in self.players]

    def playerCount(self):
        return len(self.players)

    def tiedPlayerCount(self):
        return len(self.tiedPlayers)

    def livePlayers(self):
        return [p for p in self.players if p.isPlaying]

    def livePlayerCount(self):
        return len(self.livePlayers())

    def territoryNames(self):
        return [t.name for t in self.board.territories]

    def isValidTerritory(self, t):
        return t in self.territoryNames()

    def territory(self, territoryName):
        for t in self.board.territories:
            if t.name == territoryName:
                return (t, i)

    def territoryCount(self, player):
        return sum([1 for t in self.board.territories if t.owner == player])

    def placeTroops(self, territoryName, n):
        t = self.territory(territoryName)
        if not t:
            return False
        if t.owner != self.currentPlayer:
            return False
        t.troopCount += n
        return True

    def nextPlayer(self, selection = None):
        if not selection:
            selection = self.livePlayers
            i = (selection.index(self.currentPlayer) + 1) % len(selection)
        return selection[i]

    def cardsExchangable(self, indexes):
        try:
            cards = [self.currentPlayer.cards[i] for i in indexes]
        except:
            return False
        units = [c.unit for c in cards]
        if units in Card.validCombinations:
            return cards
        return False

    def cardValue(self):
        return 1

    def draftCount(self, player):
        return 1

    def next(self, action, args):
        s = self.substate
        if not Action.argMatch(action, args):
            return False
        if s == State.Lobby:
            if action == Action.AddPlayer:
                if args[0] in self.playerNames():
                    return False
                self.players.append(Player(*args))
                return True
            elif action == Action.StartGame:
                if len(self.players) < 2:
                    return False
                self.currentPlayer = self.players[0]
                self.livePlayers = self.players
                self.substate = State.ChoosingOrder
                return True
    
        elif s == State.ChoosingOrder:
            if action == Action.RollDice:
                self.diceRolls.append(diceRoll(2))
                if len(self.diceRolls) == self.tiedPlayerCount():
                    highest = max(self.diceRolls)
                    if self.diceRolls.count(highest) > 1:
                        self.tiedPlayers = []
                        for i, p in enumerate(self.tiedPlayers):
                            if self.diceRolls[i] == highest:
                                self.tiedPlayers.append(p)
                        self.diceRolls = []
                        return True
                    else:
                        index = self.diceRolls.index(highest)
                        self.currentPlayer = self.tiedPlayers[i]
                        self.firstPlayer = self.currentPlayer
                        self.diceRolls = []
                        self.substate = State.InitialPlacement
                        return True
                else:
                    self.currentPlayer = self.nextPlayer(self.tiedPlayers)
                    return True
                
        elif s == State.InitialPlacement:
            if action == Action.PlaceTroops:
                t = args[0]
                if not self.placeTroops(t, 1):
                    return False
                self.currentPlayer = self.nextPlayer()
                if self.currentPlayer == self.firstPlayer():
                    self.substate = InitialDraft
                    self.remainingTroops = self.draftCount(self.currentPlayer)
                return True

        elif s == State.InitialDraft:
            if action == Action.PlaceTroops:
                (t, n) = args
                if n < 1 or n > self.remainingTroops:
                    return False
                if not self.placeTroops(t, n):
                    return False
                self.remainingTroops -= n
                if self.remainingTroops == 0:
                    self.currentPlayer = self.nextPlayer()
                    self.remainingTroops = self.draftCount(self.currentPlayer)
                    if self.currentPlayer == self.firstPlayer:
                        self.substate = State.Draft
                return True

        elif s == State.Draft:
            if action == Action.ExchangeCards:
                cards = self.exchangecards(args)
                if not cards:
                    return False
                pass

            elif action == Action.PlaceTroops:
                if self.currentPlayer.cardCount() > 4:
                    return False
                if n < 1 or n > self.remainingTroops:
                    return False
                if not self.placeTroops(t, n):
                    return False
                self.remainingTroops -= n
                if self.remainingTroops == 0:
                    self.substate = State.Attack
                return True

        elif s == State.Attack:
            if action == Action.Attack:
                if self.currentPlayer.cardCount() > 4:
                    return False
                (source, target, n) = args
                source = self.territory(source)
                target = self.territory(target)
                if not target or not source:
                    return False
                if source.owner != self.currentPlayer or target.owner == self.currentPlayer:
                    return False
                if n < 1 or n >= source.troopCount:
                    return False
                self.source = source
                self.target = target
                self.substate = State.AttackerRoll
                self.remainingTroops = n
                return True
            elif action == Action.EndAttack:
                if self.awardCard:
                    self.currentPlayer
                self.awardCard = False
                self.substate = State.Fortify
                return True

        elif s == State.AttackerRoll:
            if action == Action.RollDice:
                self.diceRolls = self.rollDice(min(self.remainingTroops, 3))
                self.substate = State.DefenderRoll
                return True
            if action == Action.Retreat:
                self.substate = State.Attack
                return True
    
        elif s == State.DefenderRoll:
            if action == Action.RollDice:
                defenceRolls = self.rollDice(min(self.target.troopCount, 2))
                count = min(len(self.diceRolls), len(defenceRolls))
                attackerLoss = 0
                defenderLoss = 0
                for i in count:
                    if defenceRolls[i] >= self.diceRolls[i]:
                        attackerLoss += 1
                    else:
                        defenderLoss += 1
                self.remainingTroops -= attackerLoss
                self.source.troopCount -= attackerLoss
                self.target.troopCount -= defenderLoss
                if self.target.troopCount == 0:
                    self.awardCard = True
                    if self.territoryCount(self.target.owner) == 1:
                        self.currentPlayer.cards += self.target.owner.cards
                        self.target.owner.cards = []
                        self.target.owner.isPlaying = False
                        if self.livePlayerCount == 1:
                            self.substate = State.GameOver
                            return True
                    self.target.owner = self.currentPlayer
                    self.substate = State.Victory
                elif self.remainingTroops == 0:
                    self.substate = State.Attack
                return True
                    
        elif s == State.Victory:
            if action == Action.MoveTroops:
                n = args[0]
                if n < self.remainingTroops or n >= self.source.troopCount:
                    return False
                self.source.troopCount -= n
                self.target.troopCount += n
                self.substate = State.Attack
                return True
            
        elif s == State.Fortify:
            if action == Action.Fortify:
                (source, target, n) = args
                source = self.territory(source)
                target = self.territory(target)
                if not (source.owner == target.owner == self.currentPlayer):
                    return False
                if n >= source.troopCount:
                    return False
                self.source.troopCount -= n
                self.target.troopCount += n
                return True
            elif action == Action.EndTurn:
                if self.awardCard and self.board.cards:
                    self.currentPlayer.cards.append(self.board.cards.pop())
                    self.awardCard = False
                self.currentPlayer = self.nextPlayer()
                self.substate = State.Draft
                return True
