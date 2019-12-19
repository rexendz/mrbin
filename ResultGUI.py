from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
from sql import SQLServer
from AdminGUI import InsertRecords


class Result(QDialog):
    switch_back = pyqtSignal(QDialog)

    def __init__(self, name, pts, vol, height, diameter):
        super().__init__()
        self.title = "MR BIN"
        self.left = 0
        self.top = 0
        self.width = 480
        self.height = 320
        self.userpath = os.getenv("HOME")
        self.icon = QIcon(self.userpath + '/mrbin/res/favicon.png')
        self.vbox = QVBoxLayout()
        self.gbox = QGridLayout()
        self.bottleH = height
        self.bottleD = diameter
        self.bottleV = vol
        self.name = name
        self.genInc = 1
        self.curInc = pts
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
        self.vbox.setSpacing(30)
        self.gbox.setSpacing(5)
        self.setStyleSheet("background-color: #297045;")
        self.setWindowIcon(self.icon)
        self.setLayout(self.vbox)
        self.setWindowFlags(Qt.FramelessWindowHint)

    def InitComponents(self):
        lbl1 = QLabel("Deposit Success!", self)
        lbl1.setStyleSheet("font : 40px; font-family : Sanserif; color : #e1efe6")
        lbl1.setAlignment(Qt.AlignHCenter)

        lbl2 = QLabel("Bottle Height: {}".format(self.bottleH))
        lbl3 = QLabel("Bottle Diameter: {}".format(self.bottleD))
        lbl4 = QLabel("Bottle Volume: {}".format(self.bottleV))

        lbl2.setStyleSheet("font: 10px; font-family : Sanserif; background-color: white; color : black")
        lbl3.setStyleSheet("font: 10px; font-family : Sanserif; background-color: black; color : white")
        lbl4.setStyleSheet("font: 10px; font-family : Sanserif; background-color: white; color : black")

        lbl5 = QLabel("Current Incentive Points: {}".format(self.curInc))
        lbl6 = QLabel("Generated Incentive Points: {}".format(self.genInc))
        lbl7 = QLabel("New Incentive Points: {}".format(self.curInc + self.genInc))

        lbl6.setStyleSheet("font: 10px; font-family : Sanserif; background-color: white; color : black")
        lbl7.setStyleSheet("font: 10px; font-family : Sanserif; background-color: black; color : white")
        lbl5.setStyleSheet("font: 10px; font-family : Sanserif; background-color: black; color : white")

        lbl8 = QLabel("Thank you, {}!".format(self.name))
        lbl8.setAlignment(Qt.AlignHCenter)
        lbl8.setStyleSheet("font : 20px; font-family : Sanserif; color : white;")

        btn1 = QPushButton("Close", self)

        btn1.setStyleSheet("background-color : #810000; color : white; font : 20px; font-family : Sanserif;")

        btn1.clicked.connect(self.btn1Action)

        self.vbox.addWidget(lbl1)
        self.vbox.addLayout(self.gbox)
        self.gbox.addWidget(lbl2, 0, 0)
        self.gbox.addWidget(lbl3, 1, 0)
        self.gbox.addWidget(lbl4, 2, 0)
        self.gbox.addWidget(lbl5, 0, 1)
        self.gbox.addWidget(lbl6, 1, 1)
        self.gbox.addWidget(lbl7, 2, 1)
        self.vbox.addWidget(lbl8)
        self.vbox.addWidget(btn1)

    def btn1Action(self):
        self.switch_back.emit(self)


if __name__ == "__main__":
    app = QApplication([])
    window = Result("amaze", 952, 343.12)
    app.exec()

