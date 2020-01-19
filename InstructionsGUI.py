import os
import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class Instructions(QDialog):
    switch_back = pyqtSignal(QDialog)

    def __init__(self):
        super().__init__()
        self.title = "MR BIN"
        self.top = 0
        self.left = 0
        self.width = 480
        self.height = 320
        self.userpath = os.getenv("HOME")
        self.icon = QIcon(self.userpath + '/mrbin/res/favicon.png')
        self.vbox = QVBoxLayout()

        self.InitWindow()
        self.InitComponents()

        self.show()

    def InitWindow(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowIcon(self.icon)
        self.setStyleSheet("background-color: #212121;")
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.setLayout(self.vbox)

    def InitComponents(self):
        label1 = QLabel("How to use MR BIN")
        label2 = QLabel("""
        1.) Hold your ID near the ID Scanner.
        2.) If used for the first time, input your name.
        3.) Place the bottle inside the enclosure.
        4.) Wait for the device to finish processing the object.
        5.) You will be credited with incentive points.
        
        Note:
        If you placed an object that is not a bottle, you will
        be asked to remove it and you will not get any points.""", self)
        btn1 = QPushButton("Go Back", self)
        btn1.clicked.connect(self.btn1Action)
        label1.setStyleSheet("font : 40px; font-family : Sanserif; color : #e1efe6")
        label1.setAlignment(Qt.AlignHCenter)
        label2.setStyleSheet("font : 15px; font-family : Sanserif; color : #e1efe6")

        self.vbox.addWidget(label1)
        self.vbox.addWidget(label2)
        self.vbox.addWidget(btn1)

    def btn1Action(self):
        self.switch_back.emit(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Instructions()
    sys.exit(app.exec())
