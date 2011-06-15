from sm import *
from board import *

import inspect
print "States:"
for m in inspect.getmembers(State):
    if m[0][0].isupper():
        print m
print "=" * 80

print "Actions"
for m in inspect.getmembers(Action):
    if m[0][0].isupper():
        print m
print "=" * 80

NY = Territory("NY", None)
VT = Territory("VT", None)
NH = Territory("NH", None)
MA = Territory("MA", None)

territories = [NY, VT, NH, MA]

b1 = Border(NY, VT)
b2 = Border(VT, NH)
b3 = Border(VT, MA)
b4 = Border(MA, NY)
b5 = Border(MA, NH)

borders = [b1, b2, b3, b4, b5]

board = Board(territories, borders, [])

sm = SM(board)

sm.next(Action.AddPlayer, ["Diony", 1])
sm.next(Action.AddPlayer, ["Mary", 2])
sm.next(Action.StartGame)
while sm.tiedPlayers:
    sm.next(Action.RollDice)
if sm.firstPlayer.name == "Diony":
    (p1, p2) = sm.players
else:
    (p2, p1) = sm.players
sm.next(Action.PlaceTroops, ["NY", 1])
sm.next(Action.PlaceTroops, ["MA", 1])
sm.next(Action.PlaceTroops, ["VT", 1])
sm.next(Action.PlaceTroops, ["NH", 1])
#initial draft
sm.next(Action.PlaceTroops, ["NY", 4])
sm.next(Action.PlaceTroops, ["MA", 2])
sm.next(Action.PlaceTroops, ["NH", 2])
#first turn
sm.next(Action.PlaceTroops, ["NY", 4])
sm.next(Action.Attack, ["NY", "MA", 8])
while MA.owner == p2 and sm.substate != State.Attack:
    sm.next(Action.RollDice)
sm.next(Action.EndAttack)
for t in territories:
    print t
sm.next(Action.Fortify, ["MA", "NY", 2])
sm.next(Action.EndTurn)
for t in territories:
    print t
