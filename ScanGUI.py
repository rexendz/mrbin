from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from AboutGUI import About
import sys


class Scan(QDialog):
    def __init__(self):
        super().__init__()
        self.title = "MR BIN"
        self.left = 0
        self.top = 0
        self.width = 320
        self.height = 240
        self.icon = QIcon('/home/rexendz/mrbin/res/favicon.png')
        self.vbox = QVBoxLayout()

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
        self.vbox.setSpacing(10)
        self.setStyleSheet("background-color: #212121;")
        self.setWindowIcon(self.icon)
        self.setLayout(self.vbox)
        self.setWindowFlags(Qt.FramelessWindowHint)

    def InitComponents(self):
        lbl1 = QLabel("Please Scan your ID", self)
        lbl1.setStyleSheet("font : 30px; font-family : Sanserif;")
        lbl1.setAlignment(Qt.AlignHCenter)

        lbl2 = QLabel(self)
        lbl2.setAlignment(Qt.AlignHCenter)

        pix1 = QPixmap('/home/rexendz/mrbin/res/rfid.jpg')
        pix1 = pix1.scaled(128, 128, QtCore.Qt.KeepAspectRatio)
        lbl2.setPixmap(pix1)

        btn1 = QPushButton("Back", self)
        btn1.clicked.connect(self.btn1Action)

        self.vbox.addWidget(lbl1)
        self.vbox.addWidget(lbl2)
        self.vbox.addWidget(btn1)

    def btn1Action(self):
        self.close()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Scan()
    app.exec()
