from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import cv2
import os
from camproc import Processing
from camrecog import ObjectClassifier
import sys
try:
    from picam import camera
except ImportError or ImportError:
    print("Failed importing picam.py **THIS IS NORMAL IF RUNNING ON NON-RASPBIAN**")


class CameraImage(QObject):
    finished = pyqtSignal()  # give worker class a finished signal
    changePixmap = pyqtSignal(QImage)
    noChange = pyqtSignal()
    notBottle = pyqtSignal()
    gotVolume = pyqtSignal(float, float, float)
    
    def __init__(self, device, url, image, reader, parent=None):
        super().__init__(parent)
        self.device = device
        self.url = url
        self.reader = reader
        self.image = image
        self.stopped = False
        self.objectDetected = False
        if device == "__PI__":
            self.cam = camera().start()
        else:
            self.cam = cv2.VideoCapture(url)
        self.phase = 1
        self.change = False
        self.bottleDetected = 0
        self.recog = None
        self.proc = None
        QThread.sleep(1)

    def do_work(self):
        if self.reader is not None:
            self.reader.resume()
        if self.phase == 1:
            self.recog = ObjectClassifier(self.device, cam=self.cam)
            self.recog.start()

        while not self.stopped:
            if self.reader is not None:
                distance = self.reader.read()
                if distance == 'O':
                    if not self.objectDetected:
                        self.objectDetected = True
                else:
                    self.objectDetected = False

            else:
                self.objectDetected = True

            if not self.objectDetected:
                if self.phase == 1:
                    self.recog.rest()
                elif self.phase == 2:
                    self.proc.rest()
                    self.bottleDetected = 0
                if self.change:
                    self.noChange.emit()
                    self.change = False

            elif self.objectDetected:
                if not self.change:
                    QThread.sleep(1)

                if self.phase == 1:
                    frame = self.recog.getProcessedImage()
                elif self.phase == 2:
                    frame = self.proc.getProcessedImage(self.image)

                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(320, 240, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)
                self.change = True
                if self.phase == 1:
                    if self.recog.numDetections > 150:
                        detected = self.recog.getDetection()
                        print(detected)
                        if detected == 'bottle':
                            self.phase = 2
                            self.proc = Processing(self.device, cam=self.cam)
                        else:
                            self.notBottle.emit()
                            self.stop()

                elif self.phase == 2:
                    if self.proc.counter > 500:
                        if self.reader is not None:
                            self.reader.write('S')
                        self.gotVolume.emit(self.proc.getAveVol(), self.proc.getAveHei(), self.proc.getAveDia())
                        self.stop()

        if self.reader is not None:
            self.reader.write('X')
            self.reader.pause()
        self.cam.release()
        self.finished.emit()

    def stop(self):
        self.stopped = True


class Cam(QDialog):
    switch_back = pyqtSignal(QDialog)
    switch_result = pyqtSignal(int, str, int, float, float, float)

    def __init__(self, device, url, image, userID, name, pts, reader):
        super().__init__()
        self.title = "MR BIN"
        self.left = 0
        self.top = 0
        self.width = 480
        self.height = 320
        self.userpath = os.getenv("HOME")
        self.icon = QIcon(self.userpath + '/mrbin/res/favicon.png')
        self.gbox = QGridLayout()
        self.vbox = QVBoxLayout()
        self.userID = userID
        self.name = name
        self.pts = pts
        self.image = image
        self.pic = None
        self.device = device
        self.ip = url
        self.reader = reader;
        self.thread = None
        self.worker = None
        self.InitWorker()
        self.InitWindow()
        self.InitComponents()
        self.setImage(None)

        self.show()

    def InitWorker(self):
        self.thread = QThread(parent=self)
        self.worker = CameraImage(self.device, self.ip, self.image, self.reader)

        self.worker.moveToThread(self.thread)

        self.worker.changePixmap.connect(self.setImage)        
        self.worker.noChange.connect(self.setImage)
        self.worker.gotVolume.connect(self.printVolume)
        self.worker.notBottle.connect(self.NotABottle)
        
        self.worker.finished.connect(self.thread.quit)  # connect the workers finished signal to stop thread
        self.worker.finished.connect(self.worker.deleteLater)  # connect the workers finished signal to clean up worker
        self.thread.finished.connect(self.thread.deleteLater)  # connect threads finished signal to clean up thread
        self.thread.finished.connect(self.worker.stop)

        self.thread.started.connect(self.worker.do_work)

        self.thread.start()

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

    def printVolume(self, vol, height, diameter):
        msg = QMessageBox()
        msg.setStyleSheet('color : white; font-family : Sanserif; background-color: black; font: 30px;')
        msg.information(self, "Measurement Success", "Average Measured Volume: {:.2f}mL".format(vol))
        self.switch_result.emit(self.userID, self.name, self.pts, vol, height, diameter)

    def setImage(self, image=None):
        if image is not None:
            self.pic.setPixmap(QPixmap.fromImage(image))
        else:
            self.pic.setPixmap(QPixmap(self.userpath + '/mrbin/res/instruction.png'))

    def NotABottle(self):
        QMessageBox.information(self, "Result", "Object is NOT a bottle, please try again")
        self.worker.stop()
        self.switch_back(self)

    def InitComponents(self):
        lbl1 = QLabel(("User: " + self.name), self)
        lbl2 = QLabel(("Current Incentives: " + str(self.pts)), self)
        self.pic = QLabel(self)
        self.pic.resize(320, 240)
        self.pic.setAlignment(Qt.AlignHCenter)
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
        self.worker.stop()
        self.switch_back.emit(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Cam("__IP__", "http://192.168.1.64:8080/video", 1, 1, "amaze", "959", None)
    app.exec()
