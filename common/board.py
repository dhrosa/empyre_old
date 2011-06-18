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
        return self.name

class Border(object):
    def __init__(self, t1, t2):
        self.t1 = t1
        self.t2 = t2

    def __eq__(self, other):
        return (self.t1 == other.t1 and self.t2 == other.t2) or (self.t1 == other.t2 and self.t2 == other.t1)

    def __str__(self):
        return "%s <=> %s" % (self.t1, self.t2)

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
    def __init__(self, name, territories, borders, regions, image = None):
        self.name = name
        self.territories = dict([(t.name, t) for t in territories])
        self.borders = borders
        self.regions = regions
        self.image = image
        self.cards = []
        units = []
        for (i, t) in enumerate(territories):
            units.append(i % 3)
        shuffle(units)
        for (t, u) in zip(territories, units):
            self.cards.append(Card(t, u))
        self.cards += [Card(None, Card.Wild)] * 2
        shuffle(self.cards)

    def __str__(self):
        return self.name

def loadBoard(boardName, images = False):
    import sys
    import os.path
    base = sys.path[0] + "/../boards/%s/" % (boardName)
    if not os.path.exists(base):
        return
    fileNames = [base + name for name in ["territories", "borders", "regions", "info", "board.png"]]
    for fileName in fileNames:
        if not os.path.isfile(fileName):
            return
    territories = {}
    with open(fileNames[0]) as f:
        info = f.readline()
        while info:
            info = info.split(" ")
            if len(info) < 2:
                return
            shortname = info[0]
            name = " ".join(info[1:]).strip()
            territories[shortname] = Territory(name, base + shortname + ".png" if images else None)
            info = f.readline()

    borders = []
    with open(fileNames[1]) as f:
        info = f.readline()
        while info:
            info = info.split(" ")
            if len(info) < 2:
                return
            (t1, t2) = info
            t2 = t2.strip()
            try:
                borders.append(Border(territories[t1], territories[t2]))
            except KeyError:
                print (t1, t2)
                return
            info = f.readline()
    
    regions = []
    with open(fileNames[2]) as f:
        info = f.readline()
        while info:
            info = info.split("=")
            if len(info) < 3:
                return
            name = info[0].strip()
            shortnames = info[1].strip().split(" ")
            bonus = int(info[2])
            regionTerritories =  []
            for t in shortnames:
                try:
                    regionTerritories.append(territories[t])
                except KeyError:
                    return
            regions.append(Region(name, bonus, regionTerritories))
            info = f.readline()

    name = ""
    with open(fileNames[3]) as f:
        info = f.readline()
        info = info.split("=")
        if len(info) < 2:
            return
        name = info[1].strip()
    return Board(name, territories.values(), borders, regions, fileNames[4])
