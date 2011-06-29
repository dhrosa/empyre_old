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

    def __init__(self, game, parent = None):
        super(MainWindow, self).__init__(parent)
        self.game = game
        self.boardWidget = BoardWidget(self.game)
        self.chat = Chat()

        chatDock = QDockWidget("Chat")
        chatDock.setWidget(self.chat)
        chatDock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.addDockWidget(Qt.RightDockWidgetArea, chatDock)

        toolBar = QToolBar()
        self.changeName = QPushButton("Change Name", released=self.__changeName)
        self.changeColor = QPushButton("Change Color", released=self.__changeColor)
        self.cashCards = QPushButton("Cash in Cards", self, enabled=False, released=self.cashCardsReleased)
        self.endAttack = QPushButton("End Attack", self, enabled=False, released=self.endAttackReleased)
        self.endTurn = QPushButton("End Turn", self, enabled=False, released=self.endTurnReleased)
        toolBar.addWidget(self.changeName)
        toolBar.addWidget(self.changeColor)
        toolBar.addWidget(self.cashCards)
        toolBar.addWidget(self.endAttack)
        toolBar.addWidget(self.endTurn)
        self.addToolBar(toolBar)

        self.setCentralWidget(self.boardWidget)
        self.statusBar()
        self.initMenuBar()

    def initMenuBar(self):
        menuBar = QMenuBar()
        file = menuBar.addMenu("&File")
        quit = file.addAction("&Quit", QApplication.instance().quit)
        quit.setShortcutContext(Qt.ApplicationShortcut)
        quit.setShortcut(QKeySequence.Quit)
        self.setMenuBar(menuBar)

    def __changeName(self):
        (name, ok) = QInputDialog.getText(self, "Choose New Name", "Name" , QLineEdit.Normal, self.game.clientPlayer.name)
        if ok and name and name != self.game.clientPlayer.name:
            self.nameChanged.emit(name)

    def __changeColor(self):
        color = QColorDialog.getColor(
            QColor.fromRgb(*self.game.clientPlayer.color),
            self,
            "Choose your color",
        )
        if color.isValid():
            color = color.getRgb()
            self.colorChanged.emit(list(color[:-1]))

    def setStatus(self, text):
        self.statusBar().showMessage(text)
