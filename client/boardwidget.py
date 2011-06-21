from PyQt4.QtCore import pyqtSignal, Qt, QRect
from PyQt4.QtGui import QWidget, QImage, QProgressDialog, QPainter, QPixmap, QColor

from common.game import State

class ColoredMaskCache(object):
    def __init__(self):
        self.cache = {}
    
    def clear(self):
        self.cache = {}

    def get(self, territory, color):
        hash = territory.name + str(color.rgba())
        if hash in self.cache:
            return self.cache[hash]

    def set(self, territory, color, mask):
        hash = territory.name + str(color.rgba())
        self.cache[hash] = mask

class BoardWidget(QWidget):
    territoryClaimed = pyqtSignal(str)
    drafted = pyqtSignal(str, int)

    def __init__(self, game, parent = None):
        QWidget.__init__(self, parent)
        self.game = game
        self.currentTerritory = None
        self.coloredMaskCache = ColoredMaskCache()
        self.setMouseTracking(True)
        self.setEnabled(False)
        self.loadImages()

    def loadImages(self):
        self.game.board.image = QImage(self.game.board.image)
        names = self.game.board.territoryNames()
        progress = QProgressDialog("Loading Board", "", 0, len(names))
        progress.setCancelButton(None)
        progress.setMinimumDuration(0)
        for (i, name) in enumerate(names):
            progress.setValue(i)
            t = self.game.board.getTerritory(name)
            t.image = QImage(t.image)
        self.resize(self.minimumSizeHint())

    def recreateMasks(self):
        self.masks = {}
        self.selectionImages = {}
        size = self.scaledPixmap.size()
        rect = self.scaledPixmap.rect()
        for t in self.game.board.iterTerritories():
            self.masks[t] = t.image.scaled(size)
        self.coloredMaskCache.clear()

    def territoryAt(self, x, y):
        for t in self.game.board.iterTerritories():
            if t.image.pixel(x, y):
                return t

    def minimumSizeHint(self):
        return self.game.board.image.size()

    def resizeEvent(self, event):
        self.scaledPixmap = QPixmap.fromImage(self.game.board.image).scaled(event.size(), Qt.KeepAspectRatio)
        self.scaleFactor = float(self.game.board.image.width()) / self.scaledPixmap.width()
        self.recreateMasks()
        self.coloredMaskCache.clear()

    def mouseMoveEvent(self, event):
        if self.scaledPixmap.rect().contains(event.pos()):
            x = event.pos().x() * self.scaleFactor
            y = event.pos().y() * self.scaleFactor
            self.currentTerritory = self.territoryAt(x, y)
        else:
            self.currentTerritory = None
        if self.currentTerritory:
            self.setToolTip(self.currentTerritory.name)
        else:
            self.setToolTip("")
        self.update()

    def mouseReleaseEvent(self, e):
        if self.currentTerritory:
            if self.game.state == State.InitialPlacement:
                self.territoryClaimed.emit(self.currentTerritory.name)
            elif self.game.state in (State.InitialDraft, State.Draft):
                m = e.modifiers()
                if m & Qt.ShiftModifier:
                    count = 5
                elif m & Qt.AltModifier:
                    count = 10
                else:
                    count = 1
                self.drafted.emit(self.currentTerritory.name, count)

    def coloredMask(self, territory, color):
        pixmap = self.coloredMaskCache.get(territory, color)
        if not pixmap:
            mask = self.masks[territory]
            size = mask.size()
            rect = self.scaledPixmap.rect()
            image = QImage(size, QImage.Format_ARGB32_Premultiplied)
            image.fill(0)
            painter = QPainter()
            painter.begin(image)
            painter.setCompositionMode(QPainter.CompositionMode_Source)
            color.setAlpha(200)
            painter.fillRect(rect, color)
            painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
            painter.drawImage(0, 0, mask)
            painter.end()
            pixmap = QPixmap.fromImage(image)
            self.coloredMaskCache.set(territory, color, pixmap)
        return pixmap

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.drawPixmap(0, 0, self.scaledPixmap)
        rect = self.scaledPixmap.rect()
        painter.setPen(Qt.white)
        painter.setBrush(Qt.black)
        if self.isEnabled():
            if self.currentTerritory:
                painter.drawPixmap(0, 0, self.coloredMask(self.currentTerritory, QColor(*self.game.clientPlayer.color)))
            for t in self.game.board.iterTerritories():
                if t.owner:
                    painter.drawPixmap(0, 0, self.coloredMask(t, QColor(*t.owner.color)))
            #loop again so text is not drawn under territories
            for t in self.game.board.iterTerritories():
                if t.owner:
                    x = t.center[0] * self.scaleFactor - 12
                    y = t.center[1] * self.scaleFactor - 12
                    width = 25
                    height = 25
                    painter.drawEllipse(x, y, width, height)
                    painter.drawText(x, y, width, height, Qt.AlignCenter, str(t.troopCount))

        else:
            painter.fillRect(rect, QColor(0, 0, 0, 200))
            painter.drawText(rect, Qt.AlignCenter, "Waiting for the game to start.")

        #draw player info
        painter.setPen(Qt.white)
        painter.setBrush(QColor(0, 0, 0, 200))
        playerCount = len(self.game.players)
        height = painter.fontMetrics().height() + 4
        width = max([painter.fontMetrics().width(name) for name in self.game.playerNames()]) + 8
        playersRect = QRect(0, 0, width, height * playerCount + 8)
        playersRect.moveRight(rect.right())
        playersRect.moveTop(0)
        left = playersRect.left() + 4
        painter.drawRect(playersRect)
        for (i, p) in enumerate(self.game.players):
            if p == self.game.currentPlayer:
                painter.setBrush(Qt.darkGreen)
                painter.drawRect(left - 4, i * height + 4, width, height)
            painter.setPen(Qt.white)
            painter.drawText(left, (i + 1) * height, p.name)
            x = left - height - 8
            y = i * height + 4
            painter.setBrush(QColor(*p.color))
            painter.drawRect(x, y, height, height)

        #remaining troops
        if self.game.yourTurn() and self.game.remainingTroops:
            troopText = "Remaining troops: %d" % self.game.remainingTroops
            troopRect = QRect(0, 0, painter.fontMetrics().width(troopText) + 8, height + 8)
            troopRect.moveBottomLeft(rect.bottomLeft())
            painter.setPen(Qt.white)
            painter.setBrush(QColor(0, 0, 0, 200))
            painter.drawRect(troopRect)
            painter.drawText(troopRect, Qt.AlignCenter, troopText)

        painter.end()
