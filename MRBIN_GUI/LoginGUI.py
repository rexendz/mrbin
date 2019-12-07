from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys


class customLineEdit(QLineEdit):
    def focusInEvent(self, QFocusEvent):
        if self.text() == 'Username':
            self.setText('')
            self.setStyleSheet("color : white;")
        if self.text() == 'Password':
            self.setText('')
            self.setEchoMode(QLineEdit.Password)
            self.setStyleSheet("color : white;")

    def focusOutEvent(self, QFocusEvent):
        if self.text() == '' and self.objectName() == 'User':
            self.setText('Username')
            self.setStyleSheet("color : gray;")
        if self.text() == '' and self.objectName() == 'Pass':
            self.setText('Password')
            self.setEchoMode(QLineEdit.Normal)
            self.setStyleSheet("color : gray;")


class Login(QDialog):
    def __init__(self):
        super().__init__()
        self.title = "MR BIN"
        self.left = 0
        self.top = 0
        self.width = 320
        self.height = 240
        self.icon = QIcon('/home/rexendz/mrbin/res/favicon.png')
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
        self.vbox.setSpacing(1)
        self.setStyleSheet("background-color: #212121;")
        self.setWindowIcon(self.icon)
        self.setLayout(self.vbox)
        self.setWindowFlags(Qt.FramelessWindowHint)

    def InitComponents(self):
        self.usr = customLineEdit("Username", self)
        self.pwd = customLineEdit("Password", self)
        self.usr.setStyleSheet("color : gray;")
        self.pwd.setStyleSheet("color : gray;")
        btn1 = QPushButton("Login", self)
        btn2 = QPushButton("Back", self)

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
            msg.warning(self, "Login Error", "Empty Fields!\nFill out the fields.")
        else:
            if str(self.usr.text()) == "admin" and str(self.pwd.text()) == "12345":
                msg.information(self, "Login Success", "Login Successful!\nAdministator mode activated.")
            else:
                msg.warning(self, "Login Error", "Wrong credentials")

        print(self.usr.text(), self.pwd.text())

    def btn2Action(self):
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Scan()
    app.exec()
