from PyQt4.QtCore import pyqtSignal, Qt, pyqtProperty, QObject, QTimer, QPropertyAnimation, QRectF, QPointF, QLineF, QEasingCurve, QRect

from PyQt4.QtGui import QPen, QPainter, QPixmap, QColor

class Animation(QObject):
    updated = pyqtSignal()
    finished = pyqtSignal()

    def __init__(self, parent = None):
        super(Animation, self).__init__(parent)

    def start(self):
        raise NotImplementedError()

    def stop(Self):
        raise NotImplementedError()
    
    def paint(self, painter):
        raise NotImplementedError()


class LineAnimation(Animation):
    def getPos(self):
        return self.__pos

    def setPos(self, pos):
        self.__pos = pos

    pos = pyqtProperty("QPointF", getPos, setPos)

    def __init__(self, p1, p2, color, duration, parent = None):
        super(LineAnimation, self).__init__(parent)
        self.startPoint = QPointF(p1[0], p1[1])
        self.endPoint = QPointF(p2[0], p2[1])
        self.__pos = self.startPoint
        self.color = color
        self.anim = QPropertyAnimation(self, "pos", self)
        self.anim.setStartValue(self.startPoint)
        self.anim.setEndValue(self.endPoint)
        self.anim.setDuration(duration)
        self.anim.valueChanged.connect(self.updated)
        self.anim.finished.connect(self.finished)

    def start(self):
        self.anim.start()

    def stop(self):
        self.anim.stop()

    def paint(self, painter):
        pen = QPen(Qt.black)
        pen.setWidthF(2.5)
        painter.setPen(pen)
        line = QLineF(self.startPoint, self.pos)
        painter.drawLine(line)
        if self.pos != self.startPoint:
            #draw arrowhead
            a = line.angle()
            l1 = QLineF.fromPolar(25, a - 155)
            l1.translate(self.pos)
            l2 = QLineF.fromPolar(25, a + 155)
            l2.translate(self.pos)
            painter.drawLine(l1)
            painter.drawLine(l2)

class BlinkingAnimation(Animation):
    def __init__(self, pixmap, period, parent = None):
        super(BlinkingAnimation, self).__init__(parent)
        self.pixmap = pixmap
        self.timer = QTimer()
        self.timer.setInterval(period / 2)
        self.timer.timeout.connect(self.toggle)
        self.on = False

    def toggle(self):
        self.on = not self.on
        self.updated.emit()

    def start(self):
        self.timer.start()

    def stop(self):
        self.timer.stop()

    def paint(self, painter):
        if self.on:
            painter.drawPixmap(0, 0, self.pixmap)
        

class ExplodingAnimation(Animation):
    def __init__(self, center, duration, parent = None):
        super(ExplodingAnimation, self).__init__(parent)
        self.center = center
        self.__radius = 1.0
        self.anim = QPropertyAnimation(self, "radius")
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(100.0)
        self.anim.setDuration(duration)
        self.anim.setEasingCurve(QEasingCurve.OutExpo)
        self.anim.valueChanged.connect(self.updated)
        self.anim.finished.connect(self.finished)

    def start(self):
        self.anim.start()

    def stop(self):
        self.anim.stop()

    def getRadius(self):
        return self.__radius

    def setRadius(self, r):
        self.__radius = r

    radius = pyqtProperty("qreal", getRadius, setRadius)

    def paint(self, painter):
        opacity = 1.0 - float(self.anim.currentTime()) / self.anim.duration()
        pen = QPen(QColor(255, 0, 0, opacity * 255))
        pen.setWidth(3)
        painter.setPen(pen)
        painter.setBrush(Qt.transparent)
        rect = QRect(0, 0, self.radius * 2, self.radius * 2)
        rect.moveCenter(self.center)
        painter.drawEllipse(rect)
        
