from random import shuffle

class Territory(object):
    def __init__(self, name, image):
        self.name = name
        self.image = image
        self.owner = None
        self.troopCount = 0

    def __eq__(self, other):
        return self.name == other.name

    def __str__(self):
        return "%s: %s, %d" % (self.name, self.owner, self.troopCount)

class Border(object):
    def __init__(self, t1, t2):
        self.t1 = t1
        self.t2 = t2

    def __eq__(self, other):
        return (self.t1 == other.t1 and self.t2 == other.t2) or (self.t1 == other.t2 and self.t2 == other.t1)

class Region(object):
    def __init__(self, name, bonus, territories):
        self.name = name
        self.bonus = bonus
        self.territories = territories

    def hasBonus(self, territories):
        return self.territories in territories

    def __str__(self):
        return "%s: %d" % (self.name, self.bonus)

class Card(object):
    (
        Infantry,
        Cavalry,
        Artillery,
        Wild
     ) = range(4)
    validCombinations = [[Infantry, Cavalry, Artillery],
                         [Infantry, Artillery, Cavalry],
                         [Cavalry, Infantry, Artillery],
                         [Cavalry, Artillery, Infantry],
                         [Artillery, Infantry, Cavalry],
                         [Artillery, Cavalry, Infantry],
                         [Infantry] * 3,
                         [Artillery] * 3,
                         [Cavalry] * 3,
                         [Wild] * 3]
    for v in validCombinations[:]:
        for i in range(3):
            one = v[:]
            one[i] = Wild
            validCombinations.append(one)
            two = [Wild] * 3
            two[i] = v[i]
            validCombinations.append(two)

    def __init__(self, territory, unit):
        self.territory = territory
        self.unit = unit

class Board(object):
    def __init__(self, territories, borders, regions):
        self.territories = dict([(t.name, t) for t in territories])
        self.borders = borders
        self.regions = regions
        self.cards = []
        units = []
        for (i, t) in enumerate(territories):
            units.append(i % 3)
        shuffle(units)
        for (t, u) in zip(territories, units):
            self.cards.append(Card(t, u))
        self.cards += [Card(None, Card.Wild)] * 2
        shuffle(self.cards)
