class Player(object):
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.isPlaying = True
        self.cards = []

    def __str__(self):
        return self.name

    def cardCount(self):
        return len(self.cards)
