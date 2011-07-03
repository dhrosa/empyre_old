from PyQt4.QtCore import pyqtSignal, Qt, QSize, QDateTime
from PyQt4.QtGui import QWidget, QVBoxLayout, QTextEdit, QLineEdit

class Line(object):
    (
        Chat,
        Whisper,
        Info,
        PlayerJoined,
        PlayerRejoined,
        PlayerLeft,
    ) = range(6)

    def __init__(self, type, timestamp = 0, sender = "", target = "", text = "", playerColor = (0, 0, 0)):
        self.type = type
        self.timestamp = timestamp
        self.sender = sender
        self.target = target
        self.text = text
        self.playerColor = playerColor

class Chat(QWidget):
    lineEntered = pyqtSignal(str)

    def __emitLineEntered(self):
        self.lineEntered.emit(self.input.text())
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
            if self.lines[i].type == Line.Chat or self.lines[i].type == Line.Whisper:
                if self.lines[i].sender == name:
                    self.lines[i].playerColor = color
        self.updateHistory()

    def updateHistory(self):
        lines = []
        for line in self.lines:
            text = Qt.escape(line.text)
            target = Qt.escape(line.target)
            if line.type == Line.Chat or line.type == Line.Whisper:
                (r, g, b) = line.playerColor
                sender = Qt.escape(line.sender)
                dateTime = QDateTime.fromTime_t(int(line.timestamp))
                time = dateTime.toString("hh:mm:ss AP")
                if line.type == Line.Whisper:
                    lines.append("<p><strong style=\"color: rgb(%d, %d, %d)\">[%s] %s >> %s</strong>: %s</p>" % (r, g, b, time, sender, target, text))
                else:
                    lines.append("<p><strong style=\"color: rgb(%d, %d, %d)\">[%s] %s</strong>: %s</p>" % (r, g, b, time, sender, text))
            else:
                if line.type == Line.Info:
                    (r, g, b) = (0, 0, 170)
                    text = line.text
                elif line.type == Line.PlayerJoined:
                    (r, g, b) = (0, 170, 0)
                    text = "%s has joined." % (target)
                elif line.type == Line.PlayerRejoined:
                    (r, g, b) = (0, 170, 0)
                    text = "%s has rejoined." % (target)
                elif line.type == Line.PlayerLeft:
                    (r, g, b) = (170, 0, 0)
                    text = "%s has left." % (target)
                lines.append("<p style=\"color: rgb(%d, %d, %d)\">** %s **</p>" % (r, g, b, text))
        self.history.setHtml(
            "<html><body>%s</body></html>" % ("".join(lines))
        )
        self.history.verticalScrollBar().setValue(self.history.verticalScrollBar().maximum())

    def addLine(self, line):
        if type(line) == str or type(line) == unicode:
            self.lines.append(Line(Line.Info, text=line))
        else:
            self.lines.append(line)
        self.updateHistory()

