from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys


class Cam(QDialog):
    switch_back = pyqtSignal(QDialog)

    def __init__(self, device, url, name, pts):
        super().__init__()
        self.title = "MR BIN"
        self.left = 0
        self.top = 0
        self.width = 320
        self.height = 240
        self.icon = QIcon('/home/rexendz/mrbin/res/favicon.png')
        self.vbox = QVBoxLayout()
        self.name = name
        self.pts = pts
        self.InitWindow()
        self.InitComponents()

        self.show()

    def InitWindow(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setMaximumHeight(self.height)
        self.setMaximumWidth(self.width)
        self.setMinimumHeight(self.height)
        self.setMinimumWidth(self.width)
        self.vbox.setGeometry(QRect(self.left, self.top, self.width, self.height))
        self.vbox.setSpacing(1)
        self.setStyleSheet("background-color: #212121;")
        self.setWindowIcon(self.icon)
        self.setLayout(self.vbox)
        self.setWindowFlags(Qt.FramelessWindowHint)

    def InitComponents(self):
        lbl1 = QLabel(self.name, self)
        lbl2 = QLabel(str(self.pts), self)

        btn1 = QPushButton("Exit", self)

        btn1.clicked.connect(self.btn1Action)

        self.vbox.addWidget(lbl1)
        self.vbox.addWidget(lbl2)
        self.vbox.addWidget(btn1)

    def btn1Action(self):
        self.switch_back.emit(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Cam("amaze", "959")
    app.exec()
