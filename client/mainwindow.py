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

        chatLayout = QVBoxLayout()
        chatLayout.addWidget(self.nameEdit)
        chatLayout.addWidget(changeColor)
        chatLayout.addWidget(self.chat)
        chatWidget = QWidget()
        chatWidget.setLayout(chatLayout)
        chatDock = QDockWidget("Chat")
        chatDock.setWidget(chatWidget)
        chatDock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.addDockWidget(Qt.RightDockWidgetArea, chatDock)

        toolBar = QToolBar()
        self.cashCards = QAction("Cash in Cards", self, enabled=False, triggered=self.cashCardsReleased)
        self.endAttack = QAction("End Attack", self, enabled=False, triggered=self.endAttackReleased)
        self.endTurn = QAction("End Turn", self, enabled=False, triggered=self.endTurnReleased)
        toolBar.addAction(self.cashCards)
        toolBar.addAction(self.endAttack)
        toolBar.addAction(self.endTurn)
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
