from PyQt4.QtCore import pyqtSignal, Qt
from PyQt4.QtGui import QTableWidget, QTableWidgetItem, QHeaderView, QColor

class PlayerInfo(QTableWidget):
    (Name, Color, Cards, NumberOfTroops, NumberOfTerritories, TroopsPerTurn) = range(6)

    def __init__(self, game, parent = None):
        super(PlayerInfo, self).__init__(parent)
        self.game = game
        columns = ["Name", "Color", "Cards", "# of Troops", "# of Territories", "Troops Per Turn"]
        self.setColumnCount(len(columns))
        self.setHorizontalHeaderLabels(columns)
        self.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)
        self.horizontalHeader().setResizeMode(QHeaderView.Stretch)

    def addPlayer(self, player):
        r = self.rowCount()
        self.setRowCount(r + 1)
        name = player.name
        color = player.color
        name = QTableWidgetItem(name)
        name.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        colorItem = QTableWidgetItem()
        colorItem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        colorItem.setBackground(QColor(*color))

        cards = QTableWidgetItem()
        cards.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        cards.setTextAlignment(Qt.AlignCenter)
        cards.setData(Qt.DisplayRole, 0)

        troops = QTableWidgetItem()
        troops.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        troops.setTextAlignment(Qt.AlignCenter)
        troops.setData(Qt.DisplayRole, 0)

        territories = QTableWidgetItem()
        territories.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        territories.setTextAlignment(Qt.AlignCenter)
        territories.setData(Qt.DisplayRole, 0)

        troopsPerTurn = QTableWidgetItem()
        troopsPerTurn.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        troopsPerTurn.setTextAlignment(Qt.AlignCenter)
        troopsPerTurn.setData(Qt.DisplayRole, 0)

        self.setItem(r, self.Name, name)
        self.setItem(r, self.Color, colorItem)
        self.setItem(r, self.Cards, cards)
        self.setItem(r, self.NumberOfTroops, troops)
        self.setItem(r, self.NumberOfTerritories, territories)
        self.setItem(r, self.TroopsPerTurn, troopsPerTurn)

    def removePlayer(self, name):
        items = self.findItems(name, Qt.MatchFixedString)
        if items:
            row = self.row(items[0])
            self.removeRow(row)

    def changePlayerName(self, before, after):
        items = self.findItems(before, Qt.MatchFixedString)
        if items:
            items[0].setData(Qt.DisplayRole, after)

    def changePlayerColor(self, name, color):
        items = self.findItems(name, Qt.MatchFixedString)
        if items:
            row = self.row(items[0])
            self.item(row, self.Color).setBackground(QColor(*color))

    def changeCurrentPlayer(self, name):
        for r in range(self.rowCount()):
            self.item(r, self.Name).setBackground(Qt.white)
        items = self.findItems(name, Qt.MatchFixedString)
        if items:
            items[0].setBackground(Qt.green)

    def updateStatistics(self):
        for r in range(self.rowCount()):
            player = self.game.getPlayer(self.item(r, self.Name).text())
            troops = self.game.board.troopCount(player)
            territoryCount = self.game.board.ownedTerritoryCount(player)
            troopsPerTurn = self.game.board.draftCount(player)
            self.item(r, self.NumberOfTroops).setData(Qt.DisplayRole, troops)
            self.item(r, self.NumberOfTerritories).setData(Qt.DisplayRole, territoryCount)
            self.item(r, self.TroopsPerTurn).setData(Qt.DisplayRole, troopsPerTurn)
