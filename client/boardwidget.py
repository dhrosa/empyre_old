from PyQt4.QtCore import pyqtSignal, Qt
from PyQt4.QtGui import QWidget, QImage, QProgressDialog, QPainter, QPixmap

class BoardWidget(QWidget):
    def __init__(self, game, parent = None):
        QWidget.__init__(self, parent)
        self.game = game
        self.setMouseTracking(True)
        self.loadImages()
        self.highlights = []

    def loadImages(self):
        self.game.board.image = QImage(self.game.board.image)
        names = self.game.board.territories.keys()
        progress = QProgressDialog("Loading Board", "", 0, len(names))
        progress.setCancelButton(None)
        for (i, name) in enumerate(names):
            progress.setValue(i)
            t = self.game.board.territories[name]
            t.image = QImage(t.image)
        self.resize(self.minimumSizeHint())

    def minimumSizeHint(self):
        return self.game.board.image.size()

    def resizeEvent(self, event):
        self.scaledPixmap = QPixmap.fromImage(self.game.board.image).scaled(event.size(), Qt.KeepAspectRatio)
        self.sx = float(self.game.board.image.width()) / self.scaledPixmap.width()
        self.sy = float(self.game.board.image.height()) / self.scaledPixmap.height()

    def territoryAt(self, x, y):
        for t in self.game.board.territories.values():
            if t.image.pixel(x, y):
                return t

    def mouseReleaseEvent(self, event):
        pos = [event.pos().x(), event.pos().y()]
        pos[0] *= self.sx
        pos[1] *= self.sy
        t = self.territoryAt(*pos)
        if t:
                print "Clicked on %s." % (t.name)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.scaledPixmap)
        painter.end()
