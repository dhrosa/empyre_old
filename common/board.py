class Territory(object):
    def __init__(self, name, image, neighbors):
        self.name = name
        self.image = image
        self.neighbors = neighbors
        
    def isValidMove(self, territory):
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
    

class Board(object):
    def __init__(self, territories, regions):
        self.territories = territories
        self.regions = regions
