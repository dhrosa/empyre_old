from PyQt4.QtCore import pyqtSignal, Qt, QSize
from PyQt4.QtGui import QWidget, QVBoxLayout, QTextEdit, QLineEdit

class Line(object):
    (
        Chat,
        Whisper,
        Info,
        PlayerJoin,
        PlayerLeave,
    ) = range(5)

    def __init__(self, type, timestamp = None, sender = None, target = None, text = None, playerColor = None):
        self.type = type
        self.timestamp = timestamp
        self.sender = sender
        self.target = target
        self.text = text
        self.playerColor = playerColor

class Chat(QWidget):
    lineEntered = pyqtSignal(str)

    def __emitLineEntered(self):
        self.lineEntered.emit(str(self.input.text()))
        self.input.setText("")

    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        self.lines = []
        self.history = QTextEdit()
        self.history.setReadOnly(True)
        self.input = QLineEdit()
        layout = QVBoxLayout()
        layout.addWidget(self.history)
        layout.addWidget(self.input)
        self.setLayout(layout)
        self.input.returnPressed.connect(self.__emitLineEntered)

    def minimumSizeHint(self):
        return QSize(300, 200)
        
    def clear(self):
        self.lines = []
        self.history.html = ""

    def changePlayerName(self, before, after):
        for i in range(len(self.lines)):
            if self.lines[i].type == Line.Chat:
                if self.lines[i].sender == before:
                    self.lines[i].sender = after
        self.updateHistory()

    def changePlayerColor(self, name, color):
        for i in range(len(self.lines)):
            if self.lines[i].type == Line.Chat:
                if self.lines[i].sender == name:
                    self.lines[i].playerColor = color
        self.updateHistory()

    def updateHistory(self):
        lines = []
        for line in self.lines:
            if line.type == Line.Chat:
                (r, g, b) = line.playerColor
                sender = line.sender
                text = line.text
                t = line.timestamp
                (s, m, h) = (t % 60, (t / 60) % 60, t / 3600)
                h %= 12
                if h == 0:
                    h = 12
                lines.append("<p><strong style=\"color: rgb(%d, %d, %d)\">[%d:%d:%d] %s</strong>: %s</p>" % (r, g, b, h, m, s, sender, text))
            else:
                if line.type == Line.Info:
                    (r, g, b) = (0, 0, 170)
                    text = line.text
                elif line.type == Line.PlayerJoin:
                    (r, g, b) = (0, 170, 0)
                    text = "%s has joined." % (line.target)
                elif line.type == Line.PlayerRejoin:
                    (r, g, b) = (0, 170, 0)
                    text = "%s has rejoined." % (line.target)
                elif line.type == Line.PlayerLeave:
                    (r, g, b) = (170, 0, 0)
                    text = "%s has left." % (line.target)
                lines.append("<p style=\"color: rgb(%d, %d, %d)\">** %s **</p>" % (r, g, b, text))
        self.history.setHtml(
            "<html><body>%s</body></html>" % ("".join(lines))
        )
        self.history.verticalScrollBar().setValue(self.history.verticalScrollBar().maximum())

    def addLine(self, line):
        self.lines.append(line)
        self.updateHistory()

