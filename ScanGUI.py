from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sql import SQLServer
from AdminGUI import InsertRecords
import os


class Register(InsertRecords):
    switch_back = pyqtSignal(QDialog)

    def __init__(self, sql, uid):
        super().__init__(sql)
        self.uid = uid
        self.txt2.setText(self.uid)
        self.txt3.setText('0')
        self.txt2.setDisabled(True)
        self.lbl4.hide()
        self.txt3.hide()

        self.txt2.setStyleSheet("background-color: #212121; font : 20px; font-family : Sanserif; color : gray;")


class Worker(QObject):
    finished = pyqtSignal()  # give worker class a finished signal
    auth = pyqtSignal(int, str, int)
    register = pyqtSignal(str, SQLServer)

    def __init__(self, reader, parent=None):
        QObject.__init__(self, parent=parent)
        self.userAuthenticated = False
        self.continue_run = True
        self.sql = SQLServer()
        self.reader = reader
        self.userID = None
        self.name = None
        self.pts = None

    def do_work(self):
        self.reader.write('Y')
        while self.continue_run:  # give the loop a stoppable condition
            self.reader.resume()
            uid = ''
            while uid is '' and self.continue_run:
                uid = self.reader.read()
            QThread.msleep(1)
            try:
                user = self.sql.findUid(int(uid, 16))
                if len(user) > 0:
                    (userID, name, rfid, pts), = user
                    self.userID = userID
                    self.name = name
                    self.pts = pts
                    self.reader.write('O')
                    self.userAuthenticated = True
                    self.continue_run = False
                    self.auth.emit(self.userID, self.name, self.pts)
                    self.reader.pause()
                else:
                    self.reader.write('X')
                    self.register.emit(uid, self.sql)
            except ValueError:
                print("No Result")
            QThread.sleep(1)
        self.reader.pause()
        self.finished.emit()

    def stop(self):
        self.continue_run = False


class Scan(QDialog):
    stop_signal = pyqtSignal()
    switch_cam = pyqtSignal(int, str, int)
    switch_back = pyqtSignal(QDialog)
    switch_register = pyqtSignal(str)

    def __init__(self, reader):
        super().__init__()
        self.title = "MR BIN"
        self.left = 0
        self.top = 0
        self.width = 480
        self.height = 320
        self.userpath = os.getenv("HOME")
        self.icon = QIcon(self.userpath + '/mrbin/res/favicon.png')
        self.vbox = QVBoxLayout()

        self.reader = reader

        self.thread = None
        self.worker = None

        self.InitWindow()
        self.InitComponents()
        self.InitWorker()
        self.show()

    def InitWorker(self):
        self.thread = QThread(parent=self)
        self.worker = Worker(self.reader)

        self.stop_signal.connect(self.worker.stop)
        self.worker.moveToThread(self.thread)

        self.worker.auth.connect(self.authenticated)
        self.worker.register.connect(self.register)

        self.worker.finished.connect(self.thread.quit)  # connect the workers finished signal to stop thread
        self.worker.finished.connect(self.worker.deleteLater)  # connect the workers finished signal to clean up worker
        self.thread.finished.connect(self.thread.deleteLater)  # connect threads finished signal to clean up thread
        self.thread.finished.connect(self.worker.stop)

        self.thread.started.connect(self.worker.do_work)

        self.thread.start()

    def authenticated(self, userID, name, pts):
        self.stop_signal.emit()
        msg = QMessageBox(self)
        msg.information(self,
                        "Success!", "Welcome, {}\nYour current incentive points is: {}".format(name, pts))
        self.switch_cam.emit(userID, name, pts)

    def register(self, uid):
        ret = QMessageBox.question(self,
                                   "No Record in Database",
                                   "Your UID: {} is not listed in our database\nCreate new account?".format(uid),
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if ret == QMessageBox.Yes:
            self.stop_signal.emit()
            self.switch_register.emit(uid)
            self.worker.userAuthenticated = False
            self.reader.pause()
        else:
            pass

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
        lbl1 = QLabel("Please Scan your ID", self)
        lbl1.setStyleSheet("font : 40px; font-family : Sanserif; color : #e1efe6")
        lbl1.setAlignment(Qt.AlignHCenter)

        lbl2 = QLabel(self)
        lbl2.setAlignment(Qt.AlignHCenter)

        pix1 = QPixmap(self.userpath + '/mrbin/res/rfid.jpg')
        pix1 = pix1.scaled(128, 128, QtCore.Qt.KeepAspectRatio)
        lbl2.setPixmap(pix1)

        btn1 = QPushButton("Back", self)
        btn1.clicked.connect(self.btn1Action)

        btn1.setStyleSheet("color : white; background-color : #d50000; font : 20px; font-family : Sanserif;")

        self.vbox.addWidget(lbl1)
        self.vbox.addWidget(lbl2)
        self.vbox.addWidget(btn1)

    def btn1Action(self):
        self.reader.pause()
        self.stop_signal.emit()
        self.switch_back.emit(self)
