from PyQt4.QtCore import pyqtSignal, Qt
from PyQt4.QtGui import QWidget, QImage, QProgressDialog, QPainter, QPixmap, QColor

class ColoredMaskCache(object):
    def __init__(self):
        self.cache = {}
    
    def clear(self):
        self.cache = {}

    def get(self, territory, color):
        colorCode = color[0] + color[1] * 256 + color[2] * 256 * 256
        hash = territory.name + str(colorCode)
        if hash in self.cache:
            return self.cache[hash]

    def set(self, territory, color, mask):
        colorCode = color[0] + color[1] * 256 + color[2] * 256 * 256
        hash = territory.name + str(colorCode)
        self.cache[hash] = mask

class BoardWidget(QWidget):
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
        names = self.game.board.territories.keys()
        progress = QProgressDialog("Loading Board", "", 0, len(names))
        progress.setCancelButton(None)
        progress.setMinimumDuration(0)
        for (i, name) in enumerate(names):
            progress.setValue(i)
            t = self.game.board.territories[name]
            t.image = QImage(t.image)
        self.resize(self.minimumSizeHint())

    def recreateMasks(self):
        self.masks = {}
        self.selectionImages = {}
        size = self.scaledPixmap.size()
        rect = self.scaledPixmap.rect()
        for t in self.game.board.territories.values():
            self.masks[t] = t.image.scaled(size)
        self.coloredMaskCache.clear()

    def territoryAt(self, x, y):
        for t in self.game.board.territories.values():
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

    def mouseReleaseEvent(self, event):
        if self.currentTerritory:
            print "Clicked on %s." % (self.currentTerritory.name)

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
            painter.fillRect(rect, QColor(color[0], color[1], color[2], 127))
            painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
            painter.drawImage(0, 0, mask)
            painter.end()
            pixmap = QPixmap.fromImage(image)
            self.coloredMaskCache.set(territory, color, pixmap)
        return pixmap

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.scaledPixmap)
        rect = self.scaledPixmap.rect()
        if self.isEnabled():
            if self.currentTerritory:
                painter.drawPixmap(0, 0, self.coloredMask(self.currentTerritory, (127, 127, 0)))
        else:
            painter.fillRect(rect, QColor(0, 0, 0, 200))
            painter.drawText(rect, Qt.AlignCenter, "Waiting for the game to start.")
        for t in self.game.board.territories.values():
            if t.owner:
                painer.drawPixmap(0, 0, self.coloredMask(t, t.owner.color))
        painter.end()
