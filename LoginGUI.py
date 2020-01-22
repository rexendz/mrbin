from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import sys


class customLineEdit(QLineEdit):
    def focusInEvent(self, QFocusEvent):
        if self.text() == 'Username':
            self.setText('')
            self.setStyleSheet("background-color: #212121; font : 20px; font-family : Sanserif; color : white;")
        if self.text() == 'Password':
            self.setText('')
            self.setEchoMode(QLineEdit.Password)
            self.setStyleSheet("background-color: #212121; font : 20px; font-family : Sanserif; color : white;")

    def focusOutEvent(self, QFocusEvent):
        if self.text() == '' and self.objectName() == 'User':
            self.setText('Username')
            self.setStyleSheet("background-color: #212121; font : 20px; font-family : Sanserif; color : #9E9E9E;")
        if self.text() == '' and self.objectName() == 'Pass':
            self.setText('Password')
            self.setEchoMode(QLineEdit.Normal)
            self.setStyleSheet("background-color: #212121; font : 20px; font-family : Sanserif; color : #9E9E9E;")


class Login(QDialog):
    switch_back = pyqtSignal(QDialog)
    switch_admin = pyqtSignal(QDialog)

    def __init__(self):
        super().__init__()
        self.title = "MR BIN"
        self.left = 0
        self.top = 0
        self.width = 480
        self.height = 320
        self.userpath = os.getenv("HOME")
        self.icon = QIcon(self.userpath + '/mrbin/res/favicon.png')
        self.vbox = QVBoxLayout()
        self.usr = None
        self.pwd = None
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
        self.setStyleSheet("background-color: #297045;")
        self.setWindowIcon(self.icon)
        self.setLayout(self.vbox)
        self.setWindowFlags(Qt.FramelessWindowHint)

    def InitComponents(self):
        self.usr = customLineEdit("Username", self)
        self.pwd = customLineEdit("Password", self)
        self.usr.setStyleSheet("background-color: #212121; font : 20px; font-family : Sanserif; color : #9E9E9E;")
        self.pwd.setStyleSheet("background-color: #212121; font : 20px; font-family : Sanserif; color : #9E9E9E;")
        self.usr.setFixedHeight(50)
        self.pwd.setFixedHeight(50)

        btn1 = QPushButton("Login", self)
        btn2 = QPushButton("Back", self)

        btn1.setFixedHeight(40)

        btn1.setStyleSheet("background-color : #81c14b; color : #1b2f33; font : 20px; font-family : Sanserif;")
        btn2.setStyleSheet("background-color : #aeb7b3; color : #1b2f33; font : 20px; font-family : Sanserif;")

        self.usr.setObjectName("User")
        self.pwd.setObjectName("Pass")

        btn1.clicked.connect(self.btn1Action)
        btn2.clicked.connect(self.btn2Action)

        vbox1 = QVBoxLayout()
        vbox2 = QVBoxLayout()

        self.vbox.addLayout(vbox1)
        self.vbox.addLayout(vbox2)

        vbox1.addWidget(self.usr)
        vbox1.addWidget(self.pwd)
        vbox2.addWidget(btn1)
        vbox2.addWidget(btn2)

    def btn1Action(self):
        msg = QMessageBox()
        if self.usr.text() == '' or self.pwd.text() == '' or (self.usr.text() == 'Username' and self.pwd.text() == 'Password'):
            msg.warning(self, "Login Error", "<FONT COLOR='#FFFFFF'>Empty Fields!\nFill out the fields.</FONT>")
        else:
            if str(self.usr.text()) == "admin" and str(self.pwd.text()) == "12345":
                msg.information(self, "Login Success", "<FONT COLOR='#FFFFFF'>Login Successful!\nAdministator mode activated.</FONT>")
                self.switch_admin.emit(self)

            else:
                msg.warning(self, "Login Error", "<FONT COLOR='#FFFFFF'>Wrong credentials</FONT>")

    def btn2Action(self):
        self.switch_back.emit(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Login()
    app.exec()
