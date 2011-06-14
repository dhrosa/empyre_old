class Player(object):
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.isPlaying = True
    
    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name
