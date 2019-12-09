from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from arduino import SerialListener
from sql import SQLServer


class Worker(QObject):
    finished = pyqtSignal()  # give worker class a finished signal
    auth = pyqtSignal(str, int)
    register = pyqtSignal(str, SQLServer)

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        self.userAuthenticated = False
        self.continue_run = True
        self.sql = SQLServer()
        self.name = None
        self.pts = None
        self.reader = SerialListener().start()

    def do_work(self):
        while self.continue_run:  # give the loop a stoppable condition
            uid = ''
            while uid is '' and self.continue_run:
                uid = self.reader.readRFID()
            QThread.msleep(1)
            try:
                user = self.sql.findUid(int(uid, 16))
                if len(user) > 0:
                    (_, name, _, pts), = user
                    self.name = name
                    self.pts = pts
                    self.reader.write('O')
                    self.userAuthenticated = True
                    self.continue_run = False
                    self.sql.close()
                    self.auth.emit(self.name, self.pts)
                else:
                    self.reader.write('X')
                    self.register.emit(uid, self.sql)
            except ValueError:
                print("No Result")
            QThread.sleep(1)
        self.sql.close()
        self.finished.emit()

    def stop(self):
        print("STOPPED")
        self.continue_run = False


class Scan(QDialog):
    stop_signal = pyqtSignal()
    switch_cam = pyqtSignal(str, int)
    switch_back = pyqtSignal(QDialog)
    switch_register = pyqtSignal(SQLServer, str)

    def __init__(self):
        super().__init__()
        self.title = "MR BIN"
        self.left = 0
        self.top = 0
        self.width = 320
        self.height = 240
        self.icon = QIcon('/home/rexendz/mrbin/res/favicon.png')
        self.vbox = QVBoxLayout()

        self.thread = None
        self.worker = None

        self.InitWindow()
        self.InitComponents()
        self.InitWorker()
        self.show()

    def InitWorker(self):
        self.thread = QThread(parent=self)
        self.worker = Worker()

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

    def authenticated(self, name, pts):
        self.stop_signal.emit()
        msg = QMessageBox(self)
        msg.information(self,
                        "Success!", "Welcome, {}\nYour current incentive points is: {}".format(name, pts))
        self.switch_cam.emit(name, pts)

    def register(self, uid, sql):
        ret = QMessageBox.question(self,
                                   "No Record in Database",
                                   "Your UID: {} is not listed in our database\nCreate new account?".format(uid),
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if ret == QMessageBox.Yes:
            self.switch_register.emit(sql, uid)


    def InitWindow(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setMaximumHeight(self.height)
        self.setMaximumWidth(self.width)
        self.setMinimumHeight(self.height)
        self.setMinimumWidth(self.width)
        self.vbox.setGeometry(QRect(self.left, self.top, self.width, self.height))
        self.vbox.setSpacing(10)
        self.setStyleSheet("background-color: #212121;")
        self.setWindowIcon(self.icon)
        self.setLayout(self.vbox)
        self.setWindowFlags(Qt.FramelessWindowHint)

    def InitComponents(self):
        lbl1 = QLabel("Please Scan your ID", self)
        lbl1.setStyleSheet("font : 30px; font-family : Sanserif;")
        lbl1.setAlignment(Qt.AlignHCenter)

        lbl2 = QLabel(self)
        lbl2.setAlignment(Qt.AlignHCenter)

        pix1 = QPixmap('/home/rexendz/mrbin/res/rfid.jpg')
        pix1 = pix1.scaled(128, 128, QtCore.Qt.KeepAspectRatio)
        lbl2.setPixmap(pix1)

        btn1 = QPushButton("Back", self)
        btn1.clicked.connect(self.btn1Action)

        self.vbox.addWidget(lbl1)
        self.vbox.addWidget(lbl2)
        self.vbox.addWidget(btn1)

    def btn1Action(self):
        print(self)
        self.stop_signal.emit()
        self.switch_back.emit(self)
