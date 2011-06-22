from common.game import State, Action, Player
from common.board import Board
from random import randint
from math import floor
from PyQt4.QtCore import pyqtSignal, QObject

def rollDice(n):
    return sorted([randint(1, 6) for i in range(n)], reverse=True)

def debug(func):
    def printer(s, action, args=[]):
        print "Passed in action: %s with args %s" % (Action.toString(action), args)
        if func(s, action, args):
            print "=" * 80
            print "OK ",
            print s
            print "=" * 80
            return True
        else:
            print "=" * 80
            print "FAIL ",
            print s
            print "=" * 80
            return False
    return printer

class SM(QObject):
    stateChanged = pyqtSignal(int, int)
    turnChanged = pyqtSignal(Player)
    territoryUpdated = pyqtSignal(str, str, int)
    diceRolled = pyqtSignal(str, list)
    remainingTroopsChanged = pyqtSignal(int)

    def __init__(self, board, parent = None):
        super(SM, self).__init__(parent)
        self.board = board
        self.reset()

    def __str__(self):
        return "substate: %s, current: %s, first: %s, source: %s, target: %s" % (State.toString(self.substate), self.currentPlayer, self.firstPlayer, self.source, self.target)

    def __setattr__(self, name, value):
        if value != None:
            if name == "currentPlayer":
                self.turnChanged.emit(value)
            elif name == "substate":
                try:
                    self.stateChanged.emit(self.substate, value)
                except AttributeError:
                    pass
            elif name == "remainingTroops":
                self.remainingTroopsChanged.emit(value)
        super(SM, self).__setattr__(name, value)

    def reset(self):
        self.substate = State.Lobby
        self.players = []
        self.currentPlayer = None
        self.firstPlayer = None
        self.tiedPlayers = []
        self.diceRolls = []
        self.remainingTroops = 0
        self.source = None
        self.target = None
        self.awardCard = False
        self.setsExchanged = 0
        self.board.reset()

    def clear(self):
        self.diceRolls = []
        self.remainingTroops = 0
        self.source = None
        self.target = None

    def getPlayer(self, name):
        for i in range(len(self.players)):
            if self.players[i].name == name:
                return self.players[i]

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

    def ownedTerritories(self, player):
        return [t for t in self.board.iterTerritories() if t.owner == player]

    def territoryCount(self, player):
        return len(self.ownedTerritories(player))

    def freeTerritoryCount(self):
        return sum([1 for t in self.board.iterTerritories() if not t.owner])

    def placeTroops(self, territoryName, n):
        n = min(self.remainingTroops, n)
        t = self.board.getTerritory(territoryName)
        if not t:
            return False
        if t.owner != self.currentPlayer:
            return False
        t.troopCount += n
        self.territoryUpdated.emit(t.name, self.currentPlayer.name, t.troopCount)
        return n

    def nextPlayer(self, selection = None):
        if not selection:
            selection = self.livePlayers()
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
        if (self.setsExchanged <= 5):
            return 4 + 2 * self.setsExchanged
        else:
            return -10 + 5 * self.setsExchanged

    def draftCount(self, player):
        myTerritories = self.ownedTerritories(player)
        bonus = max(3, floor(len(myTerritories) / 3))
        for region in self.board.regions:
            if region.hasBonus(myTerritories):
                bonus += region.bonus
        return bonus

    @debug
    def next(self, action, args=[]):
        s = self.substate
        if not Action.argMatch(action, args):
            return False
        if action == Action.RemovePlayer and self.substate != State.Lobby:
            return True
        if s == State.Lobby:
            if action == Action.AddPlayer:
                if args[0] in self.playerNames():
                    return False
                self.players.append(Player(*args))
                return True
            elif action == Action.RemovePlayer:
                for i in range(len(self.players)):
                    if self.players[i].name == args[0]:
                        del self.players[i]
                        return True
                return False
            elif action == Action.StartGame:
                if len(self.players) < 2:
                    return False
                self.substate = State.ChoosingOrder
                self.currentPlayer = self.players[0]
                self.tiedPlayers = self.players
                return True

        elif s == State.ChoosingOrder:
            if action == Action.RollDice:
                rolls = rollDice(2)
                self.diceRolled.emit(self.currentPlayer.name, rolls)
                self.diceRolls.append(sum(rolls))
                if len(self.diceRolls) == self.tiedPlayerCount():
                    highest = max(self.diceRolls)
                    if self.diceRolls.count(highest) > 1:
                        self.tiedPlayers = []
                        for i, p in enumerate(self.players):
                            if self.diceRolls[i] == highest:
                                self.tiedPlayers.append(p)
                        self.diceRolls = []
                        self.currentPlayer = self.nextPlayer(self.tiedPlayers)
                        return True
                    else:
                        index = self.diceRolls.index(highest)
                        self.substate = State.InitialPlacement
                        self.currentPlayer = self.tiedPlayers[self.diceRolls.index(highest)]
                        self.firstPlayer = self.currentPlayer
                        self.tiedPlayers = []
                        self.clear()
                        return True
                else:
                    self.currentPlayer = self.nextPlayer(self.tiedPlayers)
                    return True
                
        elif s == State.InitialPlacement:
            if action == Action.PlaceTroops:
                t = args[0]
                t = self.board.getTerritory(t)
                if not t:
                    return False
                if t.owner:
                    return False
                t.owner = self.currentPlayer
                t.troopCount = 1
                self.territoryUpdated.emit(t.name, self.currentPlayer.name, 1)
                self.currentPlayer = self.nextPlayer()
                if self.freeTerritoryCount() == 0:
                    self.substate = State.InitialDraft
                    self.remainingTroops = self.draftCount(self.currentPlayer)
                return True

        elif s == State.InitialDraft:
            if action == Action.PlaceTroops:
                (t, n) = args
                if n < 1:
                    return False
                n = self.placeTroops(t, n)
                if not n:
                    return False
                self.remainingTroops = self.remainingTroops - n
                if self.remainingTroops == 0:
                    self.currentPlayer = self.nextPlayer()
                    self.remainingTroops = self.draftCount(self.currentPlayer)
                    if self.currentPlayer == self.firstPlayer:
                        self.substate = State.Draft
                    return True

                return True

        elif s == State.Draft:
            if action == Action.ExchangeCards:
                cards = self.exchangecards(args)
                if not cards:
                    return False
                pass

            elif action == Action.PlaceTroops:
                (t, n) = args
                if self.currentPlayer.cardCount() > 4:
                    return False
                if n < 1:
                    return False
                n = self.placeTroops(t, n)
                if not n:
                    return False
                self.remainingTroops = self.remainingTroops - n
                if self.remainingTroops == 0:
                    self.substate = State.Attack
                return True

        elif s == State.Attack:
            if action == Action.Attack:
                if self.currentPlayer.cardCount() > 4:
                    return False
                (source, target, n) = args
                source = self.board.getTerritory(source)
                target = self.board.territories(target)
                if not source or not target:
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
                if self.awardCard and self.board.cards:
                    self.currentPlayer.cards.append(self.board.cards.pop())
                    self.awardCard = False
                self.substate = State.Fortify
                return True

        elif s == State.AttackerRoll:
            if action == Action.RollDice:
                self.diceRolls = rollDice(min(self.remainingTroops, 3))
                self.substate = State.DefenderRoll
                return True
            if action == Action.Retreat:
                self.clear()
                self.substate = State.Attack
                return True
    
        elif s == State.DefenderRoll:
            if action == Action.RollDice:
                defenceRolls = rollDice(min(self.target.troopCount, 2))
                count = min(len(self.diceRolls), len(defenceRolls))
                attackerLoss = 0
                defenderLoss = 0
                for i in range(count):
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
                    self.target.troopCount = self.remainingTroops
                    self.source.troopCount -= self.remainingTroops
                    self.clear()
                    self.substate = State.Attack
                    return True
                elif self.remainingTroops == 0:
                    self.clear()
                    self.substate = State.Attack
                return True
            
        elif s == State.Fortify:
            if action == Action.Fortify:
                (source, target, n) = args
                source = self.board.getTerritory(source)
                target = self.board.getTerritory(target)
                if not source or not target:
                    return False
                if not (source.owner == target.owner and source.owner == self.currentPlayer):
                    return False
                if n < 1 or n >= source.troopCount:
                    return False
                source.troopCount -= n
                target.troopCount += n
                return True
            elif action == Action.EndTurn:
                if self.awardCard and self.board.cards:
                    self.currentPlayer.cards.append(self.board.cards.pop())
                    self.awardCard = False
                self.currentPlayer = self.nextPlayer()
                self.substate = State.Draft
                return True

        return False
