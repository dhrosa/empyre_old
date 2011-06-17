from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import *

from chat import Chat

class MainWindow(QWidget):
    colorChanged = pyqtSignal(list)
    nameChanged = pyqtSignal(str)

    def __emitNameChanged(self):
        self.nameChanged.emit(self.nameEdit.text())

    def __init__(self, game, parent = None):
        QWidget.__init__(self, parent)
        self.game = game
        self.chat = Chat()
        self.nameEdit = QLineEdit()
        self.nameEdit.setText(self.game.clientPlayer.name)
        self.nameEdit.returnPressed.connect(self.__emitNameChanged)
        changeColor = QPushButton("Change color")
        changeColor.released.connect(self.chooseColor)
        layout = QGridLayout()
        layout.addWidget(self.nameEdit, 0, 0)
        layout.addWidget(changeColor, 0, 1)
        layout.addWidget(self.chat, 1, 0, 4, 2)
        self.setLayout(layout)

    def chooseColor(self):
        color = QColorDialog.getColor(
            QColor.fromRgb(*self.game.clientPlayer.color),
            self,
            "Choose your color",
        )
        if color.isValid():
            color = color.getRgb()
            self.colorChanged.emit(list(color[:-1]))

    def changeName(self, newName):
        self.nameEdit.setText(newName)

    def changeColor(self, color):
        color = QColor.fromRgb(*color)
        pal = QPalette()
        pal.setColor(pal.Text, color)
        self.nameEdit.setPalette(pal)
