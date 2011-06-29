from random import randint

from PyQt4.QtCore import pyqtSignal, Qt, QRect, QPoint
from PyQt4.QtGui import QWidget, QImage, QProgressDialog, QPainter, QPixmap, QColor, QInputDialog, QAction, QKeySequence

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
        self.source = None
        self.sourceAnimation = None
        self.scaleFactor = 1.0
        self.showRegionMap = False
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setEnabled(False)
        self.loadImages()

        toggleRegionMap = QAction(self,
                                  shortcutContext=Qt.ApplicationShortcut,
                                  shortcut=Qt.Key_B,
                                  triggered=self.toggleShowRegionMap)
        cancelSelection = QAction(self,
                                  shortcutContext=Qt.ApplicationShortcut,
                                  shortcut=Qt.Key_Escape,
                                  triggered=self.cancelSelection)
        self.addAction(toggleRegionMap)
        self.addAction(cancelSelection)

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
        #generate region map
        regionOverlay = QImage(self.imageSize(), QImage.Format_ARGB32_Premultiplied)
        regionOverlay.fill(0)
        painter = QPainter()
        painter.begin(regionOverlay)
        labels = []
        for r in self.game.board.regions:
            regionMask = QImage(self.imageSize(), QImage.Format_ARGB32_Premultiplied)
            regionMask.fill(0)
            p = QPainter()
            p.begin(regionMask)
            center = QPoint(0, 0)
            for t in r.territories:
                p.drawImage(0, 0, t.image)
                center += QPoint(*t.center)
            center /= len(r.territories)
            p.end()
            regionImage = QImage(self.imageSize(), QImage.Format_ARGB32_Premultiplied)
            regionImage.fill(0)
            p.begin(regionImage)
            p.setCompositionMode(QPainter.CompositionMode_Source)
            color = [randint(0, 255) for i in range(3)] + [200]
            p.fillRect(regionImage.rect(), QColor(*color))
            p.setCompositionMode(QPainter.CompositionMode_DestinationIn)
            p.drawImage(0, 0, regionMask)
            p.end()
            painter.drawImage(0, 0, regionImage)
            text = "%s: %d" % (r.name, r.bonus)
            labels.append((center, text))

        for l in labels:
            (center, text) = l
            height = painter.fontMetrics().height() + 8
            width = painter.fontMetrics().width(text) + 8
            painter.setPen(Qt.white)
            painter.setBrush(QColor(0, 0, 0, 200))
            textRect = QRect(0, 0, width, height)
            textRect.moveCenter(center)
            painter.drawRect(textRect)
            painter.drawText(textRect, Qt.AlignCenter, text)
        painter.end()
        regionMap = self.game.board.image.copy()
        painter.begin(regionMap)
        painter.drawImage(0, 0, regionOverlay)
        painter.end()
        self.regionMap = QPixmap.fromImage(regionMap)
        self.scaledRegionMap = self.regionMap
        self.ownershipMap = QPixmap.fromImage(self.game.board.image)
        self.scaledOwnershipMap = self.ownershipMap
        troopCountMap = QImage(self.game.board.image.size(), QImage.Format_ARGB32_Premultiplied)
        troopCountMap.fill(0)
        self.troopCountMap = QPixmap.fromImage(troopCountMap)
        self.scaledTroopCountMap = self.troopCountMap

    def recreateMasks(self):
        self.masks = {}
        for t in self.game.board.iterTerritories():
            self.masks[t] = t.image.scaled(self.imageSize())
        self.coloredMaskCache.clear()

    def updateTerritoryOwner(self, name, owner):
        t = self.game.board.getTerritory(name)
        p = self.game.getPlayer(owner)
        color = QColor(*p.color)
        color.setAlpha(200)
        territoryImage = QImage(t.image.size(), QImage.Format_ARGB32_Premultiplied)
        p = QPainter()
        p.begin(territoryImage)
        p.drawImage(0, 0, self.game.board.image)
        p.setCompositionMode(QPainter.CompositionMode_DestinationIn)
        p.drawImage(0, 0, t.image)
        p.end()
        coloredTerritoryImage = QImage(territoryImage.size(), QImage.Format_ARGB32_Premultiplied)
        coloredTerritoryImage.fill(0)
        p.begin(coloredTerritoryImage)
        p.fillRect(territoryImage.rect(), color)
        p.setCompositionMode(QPainter.CompositionMode_DestinationIn)
        p.drawImage(0, 0, t.image)
        p.end()
        p.begin(self.ownershipMap)
        p.drawImage(0, 0, territoryImage)
        p.drawImage(0, 0, coloredTerritoryImage)
        p.end()
        self.scaledOwnershipMap = self.ownershipMap.scaled(self.imageSize())
        self.update()

    def updateTerritoryTroopCount(self, name, count):
        t = self.game.board.getTerritory(name)
        x = t.center[0] - 12
        y = t.center[1] - 12
        width = 25
        height = 25
        painter = QPainter()
        painter.begin(self.troopCountMap)
        painter.setPen(Qt.white)
        painter.setBrush(Qt.black)
        painter.drawEllipse(x, y, width, height)
        painter.drawText(x, y, width, height, Qt.AlignCenter, str(t.troopCount))
        painter.end()
        self.scaledTroopCountMap = self.troopCountMap.scaled(self.imageSize())
        self.update()

    def toggleShowRegionMap(self):
        self.showRegionMap = not self.showRegionMap
        self.update()

    def cancelSelection(self):
        self.source = None
        if self.sourceAnimation:
            self.sourceAnimation.finished.emit()
            self.sourceAnimation = None
            self.update()

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
        self.cancelSelection()

    def minimumSizeHint(self):
        return self.game.board.image.size()

    def resizeEvent(self, event):
        size = self.minimumSizeHint()
        size.scale(event.size(), Qt.KeepAspectRatio)
        self.scaleFactor = float(self.minimumSizeHint().width()) / size.width()
        self.recreateMasks()
        self.scaledRegionMap = self.regionMap.scaled(size)
        self.scaledOwnershipMap = self.ownershipMap.scaled(size)
        self.scaledTroopCountMap = self.troopCountMap.scaled(size)
        self.coloredMaskCache.clear()
        self.update()

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
                    self.cancelSelection()
                    self.source = self.currentTerritory
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
                    elif target.owner == self.source.owner:
                        self.cancelSelection()
                        self.source = self.currentTerritory
                        mask = self.coloredMask(self.currentTerritory, QColor(170, 170, 0, 200))
                        self.sourceAnimation = BlinkingAnimation(mask, 1000)
                        self.sourceAnimation.updated.connect(self.update)
                        self.sourceAnimation.finished.connect(self.removeAnimation)
                        self.animations.append(self.sourceAnimation)
                        self.sourceAnimation.start()
        else:
            self.cancelSelection()
                        

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
            color.setAlpha(100)
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
        if not self.showRegionMap:
            painter.drawPixmap(0, 0, self.scaledOwnershipMap)
        rect = self.imageRect()
        if self.isEnabled():
            if self.showRegionMap:
                painter.drawPixmap(0, 0, self.scaledRegionMap)
            else:
                if self.currentTerritory:
                    painter.drawPixmap(0, 0, self.coloredMask(self.currentTerritory, QColor(*self.game.clientPlayer.color)))
                #draw active animations
                for a in self.animations:
                    painter.save()
                    a.paint(painter)
                    painter.restore()
                painter.drawPixmap(0, 0, self.scaledTroopCountMap)
        else:
            painter.fillRect(rect, QColor(0, 0, 0, 200))
            painter.drawText(rect, Qt.AlignCenter, "Waiting for the game to start.")

        #remaining troops
        if self.game.yourTurn() and self.game.remainingTroops:
            troopText = "Remaining troops: %d" % self.game.remainingTroops
            troopRect = QRect(0, 0, painter.fontMetrics().width(troopText) + 8, painter.fontMetrics().height() + 8)
            troopRect.moveBottomLeft(rect.bottomLeft())
            painter.setPen(Qt.white)
            painter.setBrush(QColor(0, 0, 0, 200))
            painter.drawRect(troopRect)
            painter.drawText(troopRect, Qt.AlignCenter, troopText)

        painter.end()

