from random import shuffle

class Territory(object):
    def __init__(self, name, image, neighbors):
        self.name = name
        self.image = image
        self.neighbors = neighbors
        self.owner = None
        self.troopCount = 0
        
    def isNeighbor(self, territory):
        return territory in self.neighbors

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name

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
    def __init__(self, territories, regions):
        self.territories = dict([(t.name, t) for t in territories])
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
