from PyQt4.QtCore import pyqtSignal, Qt
from PyQt4.QtGui import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QSizePolicy

class Line(object):
    (
        Chat,
        Info,
    ) = range(2)

    def __init__(self, type, **kwargs):
        self.type = type
        self.data = kwargs

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
            if self.lines[i].type == Line.Chat:
                if self.lines[i].data["name"] == before:
                    self.lines[i].data["name"] = after
        self.updateHistory()

    def changePlayerColor(self, name, color):
        for i in range(len(self.lines)):
            if self.lines[i].type == Line.Chat:
                if self.lines[i].data["name"] == name:
                    self.lines[i].data["color"] = color
        self.updateHistory()

    def updateHistory(self):
        lines = []
        for line in self.lines:
            if line.type == Line.Chat:
                (r, g, b) = line.data["color"]
                name = line.data["name"]
                text = line.data["text"]
                lines.append("<p><strong style=\"color: rgb(%d, %d, %d)\">%s</strong>: %s</p>" % (r, g, b, name, text))
            elif line.type == Line.Info:
                (r, g, b) = line.data["color"]
                text = line.data["text"]
                lines.append("<p style=\"color: rgb(%d, %d, %d)\"><strong>%s</strong></p>" % (r, g, b, text))
        self.history.setHtml(
            "<html><body>%s</body></html>" % ("".join(lines))
        )
        self.history.verticalScrollBar().setValue(self.history.verticalScrollBar().maximum())

    def addLine(self, name, color, text):
        line = Line(type=Line.Chat, name=name, color=color, text=text)
        self.lines.append(line)
        self.updateHistory()

    def addInfoLine(self, color, text):
        self.lines.append(Line(type=Line.Info, color=color, text=text))
        self.updateHistory()
