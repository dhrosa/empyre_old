from PyQt4.QtCore import pyqtSignal, Qt
from PyQt4.QtGui import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QSizePolicy

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

    def addLine(self, name, color, text):
        self.lines.append(
            r"<p><span color=#%s><strong>%s</strong></span>: %s</p>" % (hex(color), Qt.escape(name), Qt.escape(text))
        )
        self.history.setHtml(
            "<html><body>%s</body></html>" % ("".join(self.lines))
        )
