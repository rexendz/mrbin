from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import cv2
import numpy as np
import sys


class camera(QThread):
    changePixmap = pyqtSignal(QImage)

    def __init__(self, device, url, parent=None):
        super().__init__(parent)
        self.device = device
        self.url = url
        self.stopped = False

    def run(self):
        cap = cv2.VideoCapture(self.url)
        while not self.stopped:
            ret, frame = cap.read()
            if ret:
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(300, 300, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)


class Cam(QDialog):
    switch_back = pyqtSignal(QDialog)

    def __init__(self, device, url, name, pts):
        super().__init__()
        self.title = "MR BIN"
        self.left = 0
        self.top = 0
        self.width = 480
        self.height = 320
        self.icon = QIcon('/home/rexendz/mrbin/res/favicon.png')
        self.gbox = QGridLayout()
        self.vbox = QVBoxLayout()
        self.name = name
        self.pts = pts
        self.pic = None
        self.device = device
        self.ip = url
        self.th = camera(self.device, self.ip,parent=self)
        self.th.changePixmap.connect(self.setImage)
        self.th.start()
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
        self.gbox.setGeometry(QRect(self.left, self.top, self.width, self.height))
        self.gbox.setSpacing(1)
        self.setStyleSheet("background-color: #297045;")
        self.setWindowIcon(self.icon)
        self.setLayout(self.vbox)
        self.setWindowFlags(Qt.FramelessWindowHint)

    def setImage(self, image):
        self.pic.setPixmap(QPixmap.fromImage(image))

    def InitComponents(self):
        lbl1 = QLabel(("User: " + self.name), self)
        lbl2 = QLabel(("Current Incentives: " + str(self.pts)), self)
        self.pic = QLabel(self)
        self.pic.resize(300, 300)

        btn1 = QPushButton("Exit", self)
        lbl1.setAlignment(Qt.AlignLeft)
        lbl2.setAlignment(Qt.AlignRight)
        lbl1.setStyleSheet("font : 20px; font-family : Sanserif; color : #e1efe6")
        lbl2.setStyleSheet("font : 20px; font-family : Sanserif; color : #e1efe6")

        btn1.clicked.connect(self.btn1Action)
        btn1.setStyleSheet("background-color : #aeb7b3; color : #1b2f33; font : 20px; font-family : Sanserif;")
        self.vbox.addLayout(self.gbox)
        self.gbox.addWidget(lbl1, 0, 0)
        self.gbox.addWidget(lbl2, 0, 1)
        self.vbox.addWidget(self.pic)
        self.vbox.addWidget(btn1)

    def btn1Action(self):
        self.close()
        self.switch_back.emit(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Cam("__IP__", "http://192.168.1.2:8080/video", "amaze", "959")
    app.exec()