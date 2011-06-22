from PyQt4.QtCore import pyqtSignal, Qt, pyqtProperty, QObject, QPropertyAnimation, QRectF, QPointF, QLineF

from PyQt4.QtGui import QPen

class Animation(QObject):
    updated = pyqtSignal()
    finished = pyqtSignal()

    def __init__(self, parent = None):
        super(Animation, self).__init__(parent)

    def paint(self, painter):
        raise NotImplementedError()


class LineAnimation(Animation):
    def __init__(self, x1, y1, x2, y2, color, duration, parent = None):
        super(LineAnimation, self).__init__(parent)
        self.start = QPointF(x1, y1)
        self.end = QPointF(x2, y2)
        self.__pos = self.start
        self.color = color
        anim = QPropertyAnimation(self, "pos", self)
        anim.setStartValue(self.start)
        anim.setEndValue(self.end)
        anim.setDuration(duration)
        anim.valueChanged.connect(self.updated)
        anim.finished.connect(self.finished)
        anim.start()

    def getPos(self):
        return self.__pos

    def setPos(self, pos):
        self.__pos = pos

    pos = pyqtProperty("QPointF", getPos, setPos)

    def paint(self, painter):
        pen = QPen(self.color)
        pen.setWidthF(2.5)
        painter.setPen(pen)
        line = QLineF(self.start, self.pos)
        painter.drawLine(line)
        #draw arrowhead
        a = line.angle()
        l1 = QLineF.fromPolar(25, a - 155)
        l1.translate(self.pos)
        l2 = QLineF.fromPolar(25, a + 155)
        l2.translate(self.pos)
        painter.drawLine(l1)
        painter.drawLine(l2)
