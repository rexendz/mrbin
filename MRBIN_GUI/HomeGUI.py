from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from AboutGUI import About
from ScanGUI import Scan
from LoginGUI import Login
import sys


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.title = "MR BIN"
        self.left = 0
        self.top = 0
        self.width = 480
        self.height = 320
        self.icon = QIcon('/home/pi/mrbin/res/favicon.png')
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
        self.vbox.setSpacing(5)
        self.setStyleSheet("background-color: #212121;")
        self.setWindowIcon(self.icon)
        self.setLayout(self.vbox)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showFullScreen()
        
    def InitComponents(self):
        lbl1 = QLabel("Welcome to MR BIN", self)
        lbl1.setStyleSheet("font : 30px; font-family : Sanserif;")
        lbl1.setAlignment(Qt.AlignHCenter)

        btn1 = QPushButton("Start MR BIN", self)
        btn2 = QPushButton("Instructions", self)
        btn3 = QPushButton("Administrator Mode", self)
        btn4 = QPushButton("About", self)
        btn5 = QPushButton("Exit", self)

        btn1.clicked.connect(self.btn1Action)
        btn2.clicked.connect(self.btn2Action)
        btn3.clicked.connect(self.btn3Action)
        btn4.clicked.connect(self.btn4Action)
        btn5.clicked.connect(self.btn5Action)

        self.vbox.addWidget(lbl1)
        self.vbox.addWidget(btn1)
        self.vbox.addWidget(btn2)
        self.vbox.addWidget(btn3)
        self.vbox.addWidget(btn4)
        self.vbox.addWidget(btn5)

    def btn1Action(self):
        self.hide()
        scan = Scan()
        if scan.exec():
            pass
        self.show()

    def btn2Action(self):
        msg = QMessageBox()
        msg.information(self, "Instructions", """
        How to use MR BIN:
        1.) Hold your ID near the ID Scanner.
        2.) If used for the first time, input your name.
        3.) Place the plastic bottle into the enclosure.
        4.) Wait for the device to finish processing the object.
        5.) You will be credited with incentives.
        
        Note:
        If you placed an object that is not a plastic bottle, you will be 
        asked to remove it and you will not get any incentive points.
        """)

    def btn3Action(self):
        self.hide()
        login = Login()
        if login.exec():
            pass
        self.show()

    def btn4Action(self):
        self.hide()
        about = About()
        if about.exec():
            pass
        self.show()

    def btn5Action(self):
        sys.exit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    app.exec()
