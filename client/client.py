import sys
sys.path.append(sys.path[0] + "/../")

from PyQt4.QtCore import QObject
from PyQt4.QtGui import QApplication

from common.network import Message, Connection
from chat import Chat

class Client(QObject):
    def __init__(self, host, port, parent = None):
        QObject.__init__(self, parent)
        self.connection = Connection()
        self.connection.connectToHost(host, port)
        self.connection.messageReceived.connect(self.handleMessage)
        self.chat = Chat()
        self.chat.lineEntered.connect(self.sendChat)
        self.chat.show()

    def handleMessage(self, msg, args):
        if msg == Message.Chat:
            (sender, text) = args
            self.chat.addLine(sender, 0, text)

    def sendChat(self, text):
        self.connection.sendMessage(Message.Chat, ["Diony", str(text)])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = Client("127.0.0.1", 9002)
    sys.exit(app.exec_())
