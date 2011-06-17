from PyQt4.QtCore import pyqtSignal, Qt
from PyQt4.QtGui import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QSizePolicy

class Line(object):
    def __init__(self, name, color, text, whisper):
        self.name = name
        self.color = color
        self.text = text
        self.whisper = whisper

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
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.input.returnPressed.connect(self.__emitLineEntered)
        
    def clear(self):
        self.lines = []
        self.history.html = ""

    def changePlayerName(self, before, after):
        for i in range(len(self.lines)):
            if self.lines[i].name == before:
                self.lines[i].name = after
        self.updateHistory()

    def changePlayerColor(self, name, r, g, b):
        for i in range(len(self.lines)):
            if self.lines[i].name == name:
                self.lines[i].color = (r, g, b)
        self.updateHistory()

    def updateHistory(self):
        lines = ["<p><span style=\"color: rgb(%d, %d, %d)\"><strong>%s</strong></span>: %s</p>" % (l.color[0], l.color[1], l.color[2], l.name, l.text) for l in self.lines]
        self.history.setHtml(
            "<html><body>%s</body></html>" % ("".join(lines))
        )


    def addLine(self, name, r, g, b, text, whisper = False):
        self.lines.append(Line(name, (r, g, b), text, whisper))
        self.updateHistory()
