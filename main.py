from camproc import processing
from serial import serialutil
import argparse
from AboutGUI import About
from ScanGUI import Scan, Register
from LoginGUI import Login
from CameraGUI import Cam
from AdminGUI import *
import sys
try:
    from arduino import SerialListener
except ImportError or serialutil.SerialException:
    print("Warning: No Arduino connected")


class Window(QWidget):
    switch_scan = pyqtSignal(QWidget)
    switch_login = pyqtSignal()
    switch_about = pyqtSignal()
    close_all = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.title = "MR BIN"
        self.left = 0
        self.top = 0
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
        self.setMaximumHeight(self.height)
        self.setMaximumWidth(self.width)
        self.setMinimumHeight(self.height)
        self.setMinimumWidth(self.width)
        self.vbox.setGeometry(QRect(self.left, self.top, self.width, self.height))
        self.vbox.setSpacing(5)
        self.setStyleSheet("background-color: #297045;")
        self.setWindowIcon(self.icon)
        self.setLayout(self.vbox)
        self.setWindowFlags(Qt.FramelessWindowHint)

    def InitComponents(self):
        lbl1 = QLabel("Welcome to MR BIN", self)
        lbl1.setStyleSheet("font : 40px; font-family : Sanserif; color : #e1efe6")
        lbl1.setAlignment(Qt.AlignHCenter)

        btn1 = QPushButton("Start MR BIN", self)
        btn2 = QPushButton("Instructions", self)
        btn3 = QPushButton("Administrator Mode", self)
        btn4 = QPushButton("About", self)
        btn5 = QPushButton("Exit", self)

        btn1.setStyleSheet("background-color : #81c14b; color : #1b2f33; font : 20px; font-family : Sanserif;")
        btn2.setStyleSheet("background-color : #aeb7b3; color : #1b2f33; font : 20px; font-family : Sanserif;")
        btn3.setStyleSheet("background-color : #aeb7b3; color : #1b2f33; font : 20px; font-family : Sanserif;")
        btn4.setStyleSheet("background-color : #aeb7b3; color : #1b2f33; font : 20px; font-family : Sanserif;")
        btn5.setStyleSheet("background-color : #aeb7b3; color : #1b2f33; font : 20px; font-family : Sanserif;")

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
        self.switch_scan.emit(self)

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
        self.switch_login.emit()

    def btn4Action(self):
        self.switch_about.emit()

    def btn5Action(self):
        self.close_all.emit()


class Controller:
    def __init__(self, dev, ur):
        self.device = dev
        self.url = ur
        self.window = None
        self.scan = None
        self.about = None
        self.login = None
        self.cam = None
        self.admin = None
        self.view = None
        self.insert = None
        self.register = None
        self.delete = None
        self.modify = None

        try:
            self.sql = SQLServer("localhost", "root", passwd="", database="mrbin")
            print("SQL Connection Success")
        except OperationalError:
            print("Error connecting to database")
        try:
            self.reader = SerialListener().start()
            self.reader.pause()
        except serialutil.SerialException:
            print("No Arduino!")

    def show_window(self, prev_window):
        if prev_window is not None:
            prev_window.hide()
        self.window = Window()
        self.window.switch_scan.connect(self.show_scan)
        self.window.switch_about.connect(self.show_about)
        self.window.switch_login.connect(self.show_login)
        self.window.close_all.connect(self.exit)

    def show_scan(self, prev_window):
        prev_window.hide()
        self.scan = Scan(self.reader)
        self.scan.switch_back.connect(self.show_window)
        self.scan.switch_cam.connect(self.show_cam)
        self.scan.switch_register.connect(self.show_register)

    def show_register(self, uid):
        self.scan.hide()
        self.register = Register(self.sql, uid)
        self.register.switch_back.connect(self.show_scan)

    def show_login(self):
        self.window.hide()
        self.login = Login()
        self.login.switch_back.connect(self.show_window)
        self.login.switch_admin.connect(self.show_admin)

    def show_about(self):
        self.window.hide()
        self.about = About()
        self.about.switch_back.connect(self.show_window)

    def show_cam(self, name, pts):
        self.scan.hide()
        self.cam = Cam(self.device, self.url, name, pts)
        self.cam.switch_back.connect(self.show_window)

    def show_admin(self, prev_window=None):
        if prev_window is not None:
            prev_window.hide()
        self.admin = Admin(self.sql)
        self.admin.switch_back.connect(self.show_window)
        self.admin.switch_view.connect(self.show_view)
        self.admin.switch_insert.connect(self.show_insert)
        self.admin.switch_delete.connect(self.show_delete)
        self.admin.switch_modify.connect(self.show_modify)

    def show_view(self):
        self.admin.hide()
        self.view = ViewRecords(self.sql)
        self.view.switch_back.connect(self.show_admin)

    def show_insert(self):
        self.admin.hide()
        self.insert = InsertRecords(self.sql)
        self.insert.switch_back.connect(self.show_admin)

    def show_delete(self):
        self.admin.hide()
        self.delete = DeleteRecords(self.sql)
        self.delete.switch_back.connect(self.show_admin)

    def show_modify(self):
        self.admin.hide()
        self.modify = ModifyRecords(self.sql)
        self.modify.switch_back.connect(self.show_admin)

    def exit(self):
        try:
            self.reader.stop()
        except:
            print("No Arduino")
        self.sql.close()
        sys.exit()



if __name__ == "__main__":
    object_detected = False
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--ip", help="Select IP Camera with URL Instead Of PI Camera")
    parser.add_argument("-w", "--window", help="Select Window To Display[0-4]", type=int)
    
    args = parser.parse_args()
    
    device = "__PI__"
    url = "0.0.0.0"
    window = 4;
    
    if args.ip is not None:
        device = "__IP__"
        url = args.ip
    if args.window is not None:
        window = args.window

    userAuthenticated = False

    app = QApplication(sys.argv)
    controller = Controller(device, url)
    controller.show_window(None)
    app.exec()

    processor = processing(device=device, url=url)

    while True:
        try:
            distance = reader.readDistance()
            if 18 >= distance > 2:
                if not object_detected:
                    # print("Object Detected!")
                    # print("Distance from sensor: ", reader.readDistance())
                    object_detected = True
            
            elif distance > 10:
                object_detected = False
        except NameError:
            object_detected = True  # IF there is no Arduino, always show image

        if not object_detected:
            # print("Object is not detected!")
            processor.rest()
            
        elif object_detected:
            # window=0 --- Raw Image from Camera
            # window=1 --- Image w/ Detection
            # window=2 --- Edge Mask
            # window=3 --- Image w/ Detection & Edge Mask
            # window=4 --- Image w/ Detection & Edge Mask & trackbars
            k = processor.display_proc(window=window)
            
            if k == 27:
                break
    try:
        reader.stop()
    except NameError:
        print("Warning: No Arduino")
    processor.release()
