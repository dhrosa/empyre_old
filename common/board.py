from random import shuffle

class Territory(object):
    def __init__(self, name, image, center = None):
        self.name = name
        self.image = image
        self.owner = None
        self.troopCount = 0
        self.center = center

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

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
        for t in self.territories:
            if t not in territories:
                return False
        return True

    def __hash__(self):
        return hash(self.name)

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

    def __init__(self, territory = None, unit = None):
        self.territory = territory
        self.unit = unit

class Board(object):
    def __init__(self, name, territories, borders, regions, image = None):
        self.name = name
        self.__territories = dict([(t.name, t) for t in territories])
        self.borders = borders
        self.regions = regions
        self.image = image
        self.cards = []
        self.reset()

    def __str__(self):
        return self.name

    def reset(self):
        units = []
        for (i, t) in enumerate(self.__territories):
            units.append(i % 3)
        shuffle(units)
        for t in self.territoryNames():
            self.__territories[t].owner = None
            self.__territories[t].troopCount = None
            for u in range(4):
                self.cards.append(Card(self.__territories[t], u))
        self.cards += [Card(None, Card.Wild)] * 2
        shuffle(self.cards)

    def getTerritory(self, name):
        try:
            return self.__territories[name]
        except KeyError:
            return

    def iterTerritories(self):
        for t in self.__territories.keys():
            yield self.__territories[t]

    def territoryNames(self):
        return self.__territories.keys()

    def territoriesBorder(self, t1, t2):
        return Border(t1, t2) in self.borders

def loadBoard(boardName, images = False):
    import sys
    import os.path
    import yaml
    current = os.path.dirname(os.path.abspath(__file__))
    parent = os.path.join(current, "..")
    base = os.path.join(parent, "boards/%s/" % boardName)
    if not os.path.exists(base):
        print "Board does not exist."
        print base
        return
    yamlFile = base + "board.yaml"
    if not os.path.exists(yamlFile):
        print "Board configuration file missing."
        return
    f = open(yamlFile)
    try:
        d = yaml.load(f.read())
    except:
        print "Invalid board file."
        return
    f.close()
    name = d["name"] if "name" in d else boardName
    image = (base + d["image"]) if "image" in d else (base + "board.png")
    if not "territories" in d:
        print "Board has no territories."
        return
    territories = {}
    for t in d["territories"]:
        if not "id" in t or not "name" in t:
            print "Invalid territory description."
            return
        id = t["id"]
        territoryImage = (base + t["image"]) if "image" in t else (base + id + ".png")
        if not os.path.exists(territoryImage):
            print "File: %s missing." % territoryImage
            return
        if "center" in t:
            center = t["center"]
            if type(center) != list:
                print "%s: Center must be a coordinate pair." % id
                return
            if len(center) != 2:
                print "%s: Must list two coordinates." % id
                return
            try:
                x = int(center[0])
                y = int(center[1])
                center = (x, y)
            except ValueError:
                print "%s: Coordinates must be integral."
                return
        else:
            center = (0, 0)
            print "Warning: %s has no center." % id
        territories[id] = Territory(t["name"], territoryImage, center)
    borders = []
    if not "borders" in d:
        print "Board has no borders."
        return
    for b in d["borders"]:
        if type(b) != list:
            print "Border must be a list."
            return
        if len(b) != 2:
            print "Border must contain two territories."
            return
        (t1, t2) = b
        if t1 not in territories:
            print "Territory %s does not exist." % t1
            return
        if t2 not in territories:
            print "Territory %s does not exist." % t1
            return
        borders.append(Border(territories[t1], territories[t2]))
    regions = []
    if "regions" in d:
        for r in d["regions"]:
            if not "name" in r:
                print "Region must have name."
                return
            regionName = r["name"]
            if not "bonus" in r:
                print "%s: Missing bonus." % regionName
                return
            bonus = r["bonus"]
            if not "territories" in r:
                print "%s: Missing territories." % regionName
                return
            terrs = r["territories"]
            if type(terrs) != list:
                print "%s: Territories must be a list." % regionName
                return
            regionTerritories = []
            for t in terrs:
                if not t in territories:
                    print "%s: %s does not exist." % (regionName, t)
                    return
                regionTerritories.append(territories[t])
            regions.append(Region(regionName, bonus, regionTerritories))
    terrs = []
    for k in territories.keys():
        terrs.append(territories[k])
    return Board(name, territories.values(), borders, regions, image)
