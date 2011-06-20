from PyQt4.QtCore import pyqtSignal, Qt
from PyQt4.QtGui import *

from chat import Chat
from boardwidget import BoardWidget

class MainWindow(QMainWindow):
    colorChanged = pyqtSignal(list)
    nameChanged = pyqtSignal(str)

    def __emitNameChanged(self):
        self.nameChanged.emit(self.nameEdit.text())

    def __init__(self, game, parent = None):
        super(MainWindow, self).__init__(parent)
        self.game = game
        self.boardWidget = BoardWidget(self.game)
        self.chat = Chat()
        self.nameEdit = QLineEdit()
        self.nameEdit.setText(self.game.clientPlayer.name)
        self.nameEdit.returnPressed.connect(self.__emitNameChanged)
        changeColor = QPushButton("Change color")
        changeColor.released.connect(self.chooseColor)

        infoLayout = QVBoxLayout()
        infoLayout.addWidget(self.nameEdit)
        infoLayout.addWidget(changeColor)
        infoLayout.addWidget(self.chat)
        info = QWidget()
        info.setLayout(infoLayout)

        layout = QHBoxLayout()
        splitter = QSplitter()
        splitter.addWidget(self.boardWidget)
        splitter.addWidget(info)
        layout.addWidget(splitter)

        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)
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
