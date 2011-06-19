from PyQt4.QtCore import pyqtSignal, Qt
from PyQt4.QtGui import QWidget, QImage, QProgressDialog, QPainter, QPixmap, QColor

class BoardWidget(QWidget):
    def __init__(self, game, parent = None):
        QWidget.__init__(self, parent)
        self.game = game
        self.currentTerritory = None
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
            if not t.center:
                t.center = self.calculateCenter(t.image)
        self.resize(self.minimumSizeHint())

    def calculateCenter(self, image):
        leftX = None
        for x in range(image.width()):
            for y in range(image.height()):
                if image.pixel(x, y) != 0:
                    leftX = x
                    break
            if leftX:
                break
        rightX = None
        for x in range(image.width() - 1, -1, -1):
            for y in range(image.height()):
                if image.pixel(x, y) != 0:
                    rightX = x
                    break
            if rightX:
                break
        topY = None
        for y in range(image.height()):
            for x in range(image.width()):
                if image.pixel(x, y) != 0:
                    topY = y
                    break
            if topY:
                break
        bottomY = None
        for y in range(image.height() - 1, -1, -1):
            for x in range(image.width()):
                if image.pixel(x, y) != 0:
                    bottomY = y
                    break
            if bottomY:
                break
        return ((rightX + leftX) / 2, (bottomY + topY) / 2)

    def recreateMasks(self):
        self.masks = {}
        self.selectionImages = {}
        size = self.scaledPixmap.size()
        rect = self.scaledPixmap.rect()
        for t in self.game.board.territories.values():
            mask = t.image.scaled(size)
            self.masks[t] = mask
            selection = QImage(size, QImage.Format_ARGB32_Premultiplied)
            selection.fill(0)
            painter = QPainter()
            painter.begin(selection)
            painter.setCompositionMode(QPainter.CompositionMode_Source)
            painter.fillRect(rect, QColor(127, 127, 0, 127))
            painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
            painter.drawImage(0, 0, mask)
            painter.end()
            self.selectionImages[t] = selection

    def territoryAt(self, x, y):
        for t in self.game.board.territories.values():
            if t.image.pixel(x, y):
                return t

    def minimumSizeHint(self):
        return self.game.board.image.size()

    def resizeEvent(self, event):
        self.scaledPixmap = QPixmap.fromImage(self.game.board.image).scaled(event.size(), Qt.KeepAspectRatio)
        self.sx = float(self.game.board.image.width()) / self.scaledPixmap.width()
        self.sy = float(self.game.board.image.height()) / self.scaledPixmap.height()
        self.recreateMasks()

    def mouseMoveEvent(self, event):
        if self.scaledPixmap.rect().contains(event.pos()):
            x = event.pos().x() * self.sx
            y = event.pos().y() * self.sy
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

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.scaledPixmap)
        rect = self.scaledPixmap.rect()
        if self.isEnabled():
            if self.currentTerritory:
                painter.drawImage(0, 0, self.selectionImages[self.currentTerritory])
        else:
            painter.fillRect(rect, QColor(127, 127, 127, 127))
        painter.end()
