from PyQt4.QtCore import pyqtSignal, Qt, QRect, QPoint
from PyQt4.QtGui import QWidget, QImage, QProgressDialog, QPainter, QPixmap, QColor, QInputDialog

from animations import LineAnimation, BlinkingAnimation, ExplodingAnimation
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
    attacked = pyqtSignal(str, str, int)
    fortified = pyqtSignal(str, str, int)

    def __init__(self, game, parent = None):
        QWidget.__init__(self, parent)
        self.game = game
        self.currentTerritory = None
        self.coloredMaskCache = ColoredMaskCache()
        self.animations = []
        self.cachedMap = None
        self.source = None
        self.sourceAnimation = None
        self.scaleFactor = 1.0
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setEnabled(False)
        self.loadImages()
        self.updateTerritories()

    def imageRect(self):
        return QRect(QPoint(0, 0), self.imageSize())

    def imageSize(self):
        return self.game.board.image.size() / self.scaleFactor

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
        for t in self.game.board.iterTerritories():
            self.masks[t] = t.image.scaled(self.imageSize())
        self.coloredMaskCache.clear()
        self.updateTerritories()

    def updateTerritories(self):
        size = self.imageSize()
        image = QImage(size, QImage.Format_ARGB32_Premultiplied)
        image.fill(0)
        painter = QPainter()
        painter.begin(image)
        painter.drawImage(0, 0, self.game.board.image.scaled(size))
        for t in self.game.board.iterTerritories():
            if t.owner:
                painter.drawPixmap(0, 0, self.coloredMask(t, QColor(*t.owner.color)))
        painter.end()
        self.cachedMap = QPixmap.fromImage(image)

    def territoryAt(self, x, y):
        for t in self.game.board.iterTerritories():
            if t.image.pixel(x, y):
                return t

    def removeAnimation(self):
        anim = self.sender()
        self.animations.remove(anim)
        anim.deleteLater()

    def attack(self, attacker, source, target):
        source = self.game.board.getTerritory(source)
        target = self.game.board.getTerritory(target)
        attacker = self.game.getPlayer(attacker)
        anim = ExplodingAnimation(QPoint(*target.center), 1000)
        anim.finished.connect(self.removeAnimation)
        anim.updated.connect(self.repaint)
        self.animations.append(anim)
        anim.start()

    def stateChange(self, old, new):
        if self.source:
            self.source = None
            self.sourceAnimation.finished.emit()
            self.sourceAnimation = None

    def minimumSizeHint(self):
        return self.game.board.image.size()

    def resizeEvent(self, event):
        size = self.minimumSizeHint()
        size.scale(event.size(), Qt.KeepAspectRatio)
        self.scaleFactor = float(self.minimumSizeHint().width()) / size.width()
        self.recreateMasks()
        self.coloredMaskCache.clear()

    def mouseMoveEvent(self, event):
        oldTerritory = self.currentTerritory
        if self.imageRect().contains(event.pos()):
            x = event.pos().x() * self.scaleFactor
            y = event.pos().y() * self.scaleFactor
            self.currentTerritory = self.territoryAt(x, y)
        else:
            self.currentTerritory = None
        if self.currentTerritory:
            self.setToolTip(self.currentTerritory.name)
        else:
            self.setToolTip("")
        if oldTerritory != self.currentTerritory:
            self.update()

    def mouseReleaseEvent(self, e):
        if self.currentTerritory:
            if self.game.state == State.InitialPlacement:
                self.territoryClaimed.emit(self.currentTerritory.name)
                return
            m = e.modifiers()
            if m & Qt.ShiftModifier:
                n = 3
            elif m & Qt.AltModifier:
                n = 10
            else:
                n = 1
            if self.game.state in (State.InitialDraft, State.Draft):
                if e.button() == Qt.RightButton:
                    n = self.game.remainingTroops
                self.drafted.emit(self.currentTerritory.name, n)
            elif self.game.state in (State.Attack, State.Fortify) and self.game.yourTurn():
                if not self.source and self.currentTerritory.owner == self.game.clientPlayer:
                    self.source = self.currentTerritory
                    if self.sourceAnimation:
                        self.sourceAnimation.finished.emit()
                    mask = self.coloredMask(self.currentTerritory, QColor(170, 170, 0, 200))
                    self.sourceAnimation = BlinkingAnimation(mask, 1000)
                    self.sourceAnimation.updated.connect(self.update)
                    self.sourceAnimation.finished.connect(self.removeAnimation)
                    self.animations.append(self.sourceAnimation)
                    self.sourceAnimation.start()
                elif self.source:
                    target = self.currentTerritory
                    if self.game.state == State.Attack and target.owner != self.source.owner:
                        if e.button() == Qt.RightButton:
                            n = self.source.troopCount - 1
                        self.attacked.emit(self.source.name, target.name, n)
                    elif self.game.state == State.Fortify and target.owner == self.source.owner:
                        if e.button() == Qt.RightButton:
                            n = self.source.troopCount - 1
                        else:
                            (n, ok) = QInputDialog.getInt(self, "Fortify", "Number of troops to move", 1, 1, self.source.troopCount - 1)
                            if not ok:
                                return
                        self.fortified.emit(self.source.name, target.name, n)

    def keyReleaseEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.source = None
            if self.sourceAnimation:
                self.sourceAnimation.finished.emit()
                self.sourceAnimation = None

    def coloredMask(self, territory, color):
        pixmap = self.coloredMaskCache.get(territory, color)
        if not pixmap:
            mask = self.masks[territory]
            size = self.imageSize()
            rect = self.imageRect()
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
        painter.drawPixmap(0, 0, self.cachedMap)
        rect = self.imageRect()
        painter.setPen(Qt.white)
        painter.setBrush(Qt.black)
        if self.isEnabled():
            if self.currentTerritory:
                painter.drawPixmap(0, 0, self.coloredMask(self.currentTerritory, QColor(*self.game.clientPlayer.color)))
            for a in self.animations:
                painter.save()
                a.paint(painter)
                painter.restore()
            #draw territory troop counts
            for t in self.game.board.iterTerritories():
                if t.owner:
                    x = (t.center[0] - 12) / self.scaleFactor
                    y = (t.center[1] - 12) / self.scaleFactor
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
