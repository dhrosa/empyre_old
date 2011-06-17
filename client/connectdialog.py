from PyQt4.QtGui import QDialog, QFormLayout, QLineEdit, QSpinBox, QPushButton

class ConnectDialog(QDialog):
    def __init__(self, parent = None):
        QDialog.__init__(self, parent)
        self.setWindowTitle("Connect To Game")
        self.hostEdit = QLineEdit()
        self.hostEdit.setText("127.0.0.1")
        self.portEdit = QSpinBox()
        self.portEdit.setRange(0, 2 ** 16)
        self.portEdit.setValue(9002)
        self.nameEdit = QLineEdit()
        connect = QPushButton("Connect")
        connect.released.connect(self.accept)
        layout = QFormLayout()
        layout.addRow("Host", self.hostEdit)
        layout.addRow("Port", self.portEdit)
        layout.addRow("Username", self.nameEdit)
        layout.addRow(connect)
        self.setLayout(layout)
