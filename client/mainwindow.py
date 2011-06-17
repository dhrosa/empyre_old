from PyQt4.QtGui import QWidget, QHBoxLayout

from chat import Chat

class MainWindow(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        self.chat = Chat()
        layout = QHBoxLayout()
        layout.addWidget(self.chat)
        self.setLayout(layout)
