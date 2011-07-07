from PyQt4.QtCore import pyqtSignal, Qt
from PyQt4.QtGui import QApplication, QMainWindow, QDockWidget, QToolBar, QPushButton, QMenuBar, QAction, QKeySequence, QInputDialog, QLineEdit, QColorDialog, QColor

from chat import Chat
from boardwidget import BoardWidget
from playerinfo import PlayerInfo
from carddialog import CardDialog

class MainWindow(QMainWindow):
    colorChanged = pyqtSignal(list)
    nameChanged = pyqtSignal(str)
    endAttackReleased = pyqtSignal()
    endTurnReleased = pyqtSignal()
    cardsSelected = pyqtSignal(list)

    def __init__(self, game, parent = None):
        super(MainWindow, self).__init__(parent)
        self.game = game
        self.boardWidget = BoardWidget(self.game)
        self.chat = Chat()
        self.playerInfo = PlayerInfo(self.game)

        playerDock = QDockWidget("Players")
        playerDock.setWidget(self.playerInfo)
        playerDock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.addDockWidget(Qt.RightDockWidgetArea, playerDock)

        chatDock = QDockWidget("Chat")
        chatDock.setWidget(self.chat)
        chatDock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.addDockWidget(Qt.RightDockWidgetArea, chatDock)

        self.setCentralWidget(self.boardWidget)
        self.statusBar()
        self.initMenuBar()

    def initMenuBar(self):
        menuBar = QMenuBar()
        file = menuBar.addMenu("&File")
        quit = file.addAction("&Quit", QApplication.instance().quit)
        quit.setShortcutContext(Qt.ApplicationShortcut)
        quit.setShortcut(QKeySequence.Quit)
        self.changeName = QAction("Change Name", self, triggered=self.__changeName)
        self.changeColor = QAction("Change Color", self, triggered=self.__changeColor)
        self.cashCards = QAction("Cash in Cards", self, enabled=False, triggered=self.__cashCards)
        self.endAttack = QAction("End Attack", self, enabled=False, triggered=self.endAttackReleased)
        self.endTurn = QAction("End Turn", self, enabled=False, triggered=self.endTurnReleased)
        menuBar.addAction(self.changeName)
        menuBar.addAction(self.changeColor)
        menuBar.addAction(self.cashCards)
        menuBar.addAction(self.endAttack)
        menuBar.addAction(self.endTurn)
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

    def __cashCards(self):
        dialog = CardDialog(self.game.clientPlayer.cards)
        if dialog.exec_() == CardDialog.Accepted and dialog.combination:
            self.cardsSelected.emit(list(dialog.combination))

    def setStatus(self, text):
        self.statusBar().showMessage(text)
