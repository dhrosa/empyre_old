from PyQt4.QtCore import pyqtSignal, Qt
from PyQt4.QtGui import QTableWidget, QTableWidgetItem, QColor

class PlayerInfo(QTableWidget):
    (Name, Color, Cards, TroopsPerTurn) = range(4)

    def __init__(self, parent = None):
        super(PlayerInfo, self).__init__(parent)
        columns = ["Name", "Color", "Cards", "Troops Per Turn"]
        self.setColumnCount(len(columns))
        self.setHorizontalHeaderLabels(columns)

    def addPlayer(self, name, color):
        r = self.rowCount()
        self.setRowCount(r + 1)
        print name, color, r
        name = QTableWidgetItem(name)
        colorItem = QTableWidgetItem()
        colorItem.setBackground(QColor(*color))
        cards = QTableWidgetItem()
        cards.setData(Qt.DisplayRole, 0)
        troops = QTableWidgetItem()
        troops.setData(Qt.DisplayRole, 0)
        self.setItem(r, self.Name, name)
        self.setItem(r, self.Color, colorItem)
        self.setItem(r, self.Cards, cards)
        self.setItem(r, self.TroopsPerTurn, troops)

    def removePlayer(self, name):
        items = self.findItems(name)
        if items:
            row = self.row(items[0])
            self.removeRow(row)

    def changePlayerName(self, before, after):
        items = self.findItems(before)
        if items:
            items[0].setData(Qt.DisplayRole, after)

    def changePlayerColor(self, name, color):
        items = self.findItems(name)
        if items:
            row = self.row(items[0])
            col = self.Color
            self.item(row, col).setBackground(QColor(*color))

    def changeCurrentPlayer(self, name):
        pass
