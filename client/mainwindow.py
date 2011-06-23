from PyQt4.QtCore import pyqtSignal, Qt
from PyQt4.QtGui import *

from chat import Chat
from boardwidget import BoardWidget

class MainWindow(QMainWindow):
    colorChanged = pyqtSignal(list)
    nameChanged = pyqtSignal(str)
    cashCardsReleased = pyqtSignal()
    endAttackReleased = pyqtSignal()
    endTurnReleased = pyqtSignal()

    def __emitNameChanged(self):
        self.nameChanged.emit(self.nameEdit.text())

    def __init__(self, game, parent = None):
        super(MainWindow, self).__init__(parent)
        self.game = game
        self.boardWidget = BoardWidget(self.game)
        self.chat = Chat()
        self.nameEdit = QLineEdit(text=self.game.clientPlayer.name, returnPressed=self.__emitNameChanged)
        changeColor = QPushButton("Change color", released=self.chooseColor)

        infoLayout = QVBoxLayout()
        infoLayout.addWidget(self.nameEdit)
        infoLayout.addWidget(changeColor)
        infoLayout.addWidget(self.chat)
        info = QWidget()
        info.setLayout(infoLayout)

        buttonLayout = QHBoxLayout()
        self.cashCards = QPushButton("Cash in Cards", enabled=False, released=self.cashCardsReleased)
        self.endAttack = QPushButton("End Attack", enabled=False, released=self.endAttackReleased)
        self.endTurn = QPushButton("End Turn", enabled=False, released=self.endTurnReleased)
        buttonLayout.addWidget(self.cashCards)
        buttonLayout.addWidget(self.endAttack)
        buttonLayout.addWidget(self.endTurn)

        boardLayout = QVBoxLayout()
        boardLayout.addWidget(self.boardWidget)
        boardLayout.addLayout(buttonLayout)
        tempWidget = QWidget()
        tempWidget.setLayout(boardLayout)

        splitter = QSplitter()
        splitter.addWidget(tempWidget)
        splitter.addWidget(info)

        self.setCentralWidget(splitter)
        self.statusBar()
        self.initMenuBar()

    def initMenuBar(self):
        menuBar = QMenuBar()
        file = menuBar.addMenu("&File")
        quit = file.addAction("&Quit", QApplication.instance().quit)
        quit.setShortcutContext(Qt.ApplicationShortcut)
        quit.setShortcut(QKeySequence.Quit)

        self.setMenuBar(menuBar)

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

    def setStatus(self, text):
        self.statusBar().showMessage(text)
