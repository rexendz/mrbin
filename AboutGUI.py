from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys


class AnimationLabel(QLabel):
    def __init__(self, *args, **kwargs):
        QLabel.__init__(self, *args, **kwargs)
        self.animation = QVariantAnimation()
        self.animation.valueChanged.connect(self.changeColor)

    @pyqtSlot(QVariant)
    def changeColor(self, color):
        palette = self.palette()
        palette.setColor(QPalette.WindowText, color)
        self.setPalette(palette)

    def startFadeIn(self):
        self.animation.stop()
        self.animation.setStartValue(QColor(255, 255, 255, 0))
        self.animation.setEndValue(QColor(255, 255, 255, 255))
        self.animation.setDuration(2000)
        self.animation.setEasingCurve(QEasingCurve.InBack)
        self.animation.start()

    def startFadeOut(self):
        self.animation.stop()
        self.animation.setStartValue(QColor(255, 255, 255, 255))
        self.animation.setEndValue(QColor(255, 255, 255, 0))
        self.animation.setDuration(2000)
        self.animation.setEasingCurve(QEasingCurve.OutBack)
        self.animation.start()

    def startAnimation(self):
        self.startFadeIn()
        loop = QEventLoop()
        self.animation.finished.connect(loop.quit)
        loop.exec_()
        QTimer.singleShot(2000, self.startFadeOut)


class About(QDialog):
    switch_back = pyqtSignal(QDialog)

    def __init__(self):
        super().__init__()
        self.title = "MR BIN"
        self.top = 0
        self.left = 0
        self.width = 480
        self.height = 320
        self.icon = QIcon('/home/rexendz/mrbin/res/favicon.png')
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
        label1 = AnimationLabel("Machine for Recycling Bottles\nwith\nIncentive Noting\n\n(MR BIN)\n")
        label1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        label1.setAlignment(Qt.AlignCenter)
        label1.setStyleSheet("font : 30px; font : bold; font-family : Sanserif; color : #e1efe6")

        label2 = AnimationLabel("Created By\n\nRex Christian R. Endozo\n\nand\n\nJohn Ray F. Navarro")
        label2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        label2.setAlignment(Qt.AlignCenter)
        label2.setStyleSheet("font : 30px; font : bold; font-family : Sanserif; color : #e1efe6")
        label1.hide()
        label2.hide()

        btn1 = QPushButton("Go Back", self)

        btn1.clicked.connect(self.btn1Action)

        self.vbox.addWidget(label1)
        self.vbox.addWidget(label2)
        self.vbox.addWidget(btn1)
        btn1.hide()

        label1.show()
        label1.startFadeIn()

        QTimer.singleShot(5000, label1.startFadeOut)
        QTimer.singleShot(6000, label1.hide)
        QTimer.singleShot(6000, label2.show)
        QTimer.singleShot(6000, label2.startFadeIn)
        QTimer.singleShot(10000, label2.startFadeOut)
        QTimer.singleShot(12000, label2.hide)
        QTimer.singleShot(12000, btn1.show)

    def btn1Action(self):
        self.switch_back.emit(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = About()
    sys.exit(app.exec())
