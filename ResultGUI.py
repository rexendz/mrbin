from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
from sql import SQLServer
from AdminGUI import InsertRecords


class Result(QDialog):
    switch_back = pyqtSignal(QDialog)
    switch_again = pyqtSignal(QDialog, int, str, int)

    def __init__(self, userID, name, pts, vol, height, diameter, sql, reader):
        super().__init__()
        self.title = "MR BIN"
        self.left = 0
        self.top = 0
        self.width = 480
        self.height = 320
        self.reader = reader
        self.userpath = os.getenv("HOME")
        self.icon = QIcon(self.userpath + '/mrbin/res/favicon.png')
        self.vbox = QVBoxLayout()
        self.gbox = QGridLayout()
        self.bottleH = height
        self.bottleD = diameter
        self.bottleV = vol
        self.userID = userID
        self.name = name
        self.sql = sql
        self.genInc = 0
        self.curInc = pts
        self.newInc = 0
        self.CalculateIncentives()
        self.InitWindow()
        self.InitComponents()
        self.UpdateRecord()

        self.show()

    def CalculateIncentives(self):
        if self.bottleV < 600:
            self.genInc = 1
        elif 600 <= self.bottleV < 1000:
            self.genInc = 2
        elif self.bottleV >= 1000:
            self.genInc = 3
        self.newInc = self.curInc + self.genInc

    def UpdateRecord(self):
        self.sql.updateIncentives(self.userID, self.newInc)

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

        lbl2 = QLabel("Bottle Height: {:.2f}".format(self.bottleH))
        lbl3 = QLabel("Bottle Diameter: {:.2f}".format(self.bottleD))
        lbl4 = QLabel("Bottle Volume: {:.2f}".format(self.bottleV))

        lbl2.setStyleSheet("font: 10px; font-family : Sanserif; background-color: white; color : black")
        lbl3.setStyleSheet("font: 10px; font-family : Sanserif; background-color: black; color : white")
        lbl4.setStyleSheet("font: 10px; font-family : Sanserif; background-color: white; color : black")

        lbl5 = QLabel("Current Incentive Points: {}".format(self.curInc))
        lbl6 = QLabel("Incurred Incentive Points: {}".format(self.genInc))
        lbl7 = QLabel("New Incentive Points: {}".format(self.newInc))

        lbl6.setStyleSheet("font: 10px; font-family : Sanserif; background-color: white; color : black")
        lbl7.setStyleSheet("font: 10px; font-family : Sanserif; background-color: black; color : white")
        lbl5.setStyleSheet("font: 10px; font-family : Sanserif; background-color: black; color : white")

        lbl8 = QLabel("Thank you, {}!".format(self.name))
        lbl8.setAlignment(Qt.AlignHCenter)
        lbl8.setStyleSheet("font : 20px; font-family : Sanserif; color : white;")

        btn1 = QPushButton("Deposit Again")
        btn2 = QPushButton("Close", self)

        btn1.setStyleSheet("background-color : #810000; color : white; font : 20px; font-family : Sanserif;")
        btn2.setStyleSheet("background-color : #810000; color : white; font : 20px; font-family : Sanserif;")

        btn1.clicked.connect(self.btn1Action)
        btn2.clicked.connect(self.btn2Action)

        self.vbox.addWidget(lbl1)
        self.vbox.addLayout(self.gbox)
        self.gbox.addWidget(lbl2, 0, 0)
        self.gbox.addWidget(lbl3, 1, 0)
        self.gbox.addWidget(lbl4, 2, 0)
        self.gbox.addWidget(lbl5, 0, 1)
        self.gbox.addWidget(lbl6, 1, 1)
        self.gbox.addWidget(lbl7, 2, 1)
        self.vbox.addWidget(lbl8)
        self.gbox.addWidget(btn1, 3, 0)
        self.gbox.addWidget(btn2, 3, 1)

    def btn1Action(self):
        self.switch_again.emit(self, self.userID, self.name, self.newInc)

    def btn2Action(self):
        self.reader.write('X')
        self.switch_back.emit(self)


if __name__ == "__main__":
    sql = SQLServer()
    app = QApplication([])
    window = Result(1, "John", 1, 343.12, 17, 15, sql)
    app.exec()

