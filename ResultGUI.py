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

    def __init__(self, userID, vol, height, diameter, sql, reader):
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
        self.sql = sql
        user = self.sql.findID(userID)
        if len(user) > 0:
            (self.userID, self.name, self.rfid, self.curInc, self.curBottle), = user
        self.bottleH = height
        self.bottleD = diameter
        self.bottleV = vol
        self.genInc = 0
        self.newInc = 0
        self.newBottle = 0
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
        self.newBottle = self.curBottle + 1

    def UpdateRecord(self):
        self.sql.updateIncentives(self.userID, self.newInc, self.newBottle)

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

        lbl2 = QLabel("Height: {:.2f}cm".format(self.bottleH))
        lbl3 = QLabel("Diameter: {:.2f}cm".format(self.bottleD))
        lbl4 = QLabel("Volume: {:.2f}mL".format(self.bottleV))

        lbl2.setStyleSheet("font: 20px; font-family : Sanserif; background-color: white; color : black")
        lbl3.setStyleSheet("font: 20px; font-family : Sanserif; background-color: black; color : white")
        lbl4.setStyleSheet("font: 20px; font-family : Sanserif; background-color: white; color : black")

        lbl5 = QLabel("Current Points: {}".format(self.curInc))
        lbl6 = QLabel("Incurred Points: {}".format(self.genInc))
        lbl7 = QLabel("New Points: {}".format(self.newInc))

        lbl6.setStyleSheet("font: 20px; font-family : Sanserif; background-color: white; color : black")
        lbl7.setStyleSheet("font: 20px; font-family : Sanserif; background-color: black; color : white")
        lbl5.setStyleSheet("font: 20px; font-family : Sanserif; background-color: black; color : white")

        lbl8 = QLabel("Thank you, {}!".format(self.name))
        lbl8.setAlignment(Qt.AlignHCenter)
        lbl8.setStyleSheet("font : 20px; font-family : Sanserif; color : white;")

        btn1 = QPushButton("Deposit Again")
        btn2 = QPushButton("Close", self)

        btn1.setStyleSheet("background-color : #008100; color : white; font : 20px; font-family : Sanserif;")
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
        self.gbox.addWidget(btn1, 3, 0)
        self.gbox.addWidget(btn2, 3, 1)
        self.vbox.addWidget(lbl8)

    def btn1Action(self):
        self.switch_again.emit(self, self.userID, self.name, self.newInc)

    def btn2Action(self):
        if self.reader is not None:
            self.reader.write('X')
        self.switch_back.emit(self)


if __name__ == "__main__":
    sql = SQLServer()
    app = QApplication([])
    window = Result(1, 1230, 17, 15, sql, None)
    app.exec()

