from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sql import SQLServer
from pymysql.err import OperationalError
import sys


class ViewRecords(QDialog):
    switch_back = pyqtSignal(QDialog)

    def __init__(self, sql):
        super().__init__()
        self.title = "MR BIN"
        self.left = 0
        self.top = 0
        self.width = 320
        self.height = 240
        self.icon = QIcon('/home/rexendz/mrbin/res/favicon.png')
        self.vbox = QVBoxLayout()
        self.sql = sql
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

        result = self.sql.readAll()

        table = QTableWidget(self)
        table.setRowCount(len(result))
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(['ID', 'Name', 'RFID-UID', 'Incentives'])
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setStretchLastSection(True)

        for i in range(len(result)):
            for j in range(4):
                if j == 2:
                    table.setItem(i, j, QTableWidgetItem("{:08X}".format(result[i][j])))
                else:
                    table.setItem(i, j, QTableWidgetItem(str(result[i][j])))

        lbl1 = QLabel("MR BIN Users", self)
        lbl1.setStyleSheet("font : 15px; font-family : Sanserif;")
        lbl1.setAlignment(Qt.AlignHCenter)

        btn1 = QPushButton(self)
        btn1.setText("Close")
        btn1.clicked.connect(self.btn1Action)

        table.setGeometry(0, 0, 320, 240)
        table.resizeRowsToContents()
        table.resizeColumnsToContents()

        self.vbox.addWidget(lbl1)
        self.vbox.addWidget(table)
        self.vbox.addWidget(btn1)

    def btn1Action(self):
        self.switch_back.emit(self)


class InsertRecords(QDialog):
    switch_back = pyqtSignal(QDialog)

    def __init__(self, sql):
        super().__init__()
        self.title = "MR BIN"
        self.left = 0
        self.top = 0
        self.width = 320
        self.height = 240
        self.icon = QIcon('/home/rexendz/mrbin/res/favicon.png')
        self.vbox = QVBoxLayout()
        self.gbox = QGridLayout()

        self.sql = sql

        self.txt1 = None
        self.txt2 = None
        self.txt3 = None

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
        self.vbox.setSpacing(15)
        self.setStyleSheet("background-color: #212121;")
        self.setWindowIcon(self.icon)
        self.setLayout(self.vbox)
        self.setWindowFlags(Qt.FramelessWindowHint)

    def InitComponents(self):
        gbox = QGridLayout()

        lbl1 = QLabel("Insert Record", self)
        lbl2 = QLabel("Name", self)
        lbl3 = QLabel("RFID in Hex", self)
        lbl4 = QLabel("Incentives", self)

        lbl1.setStyleSheet("font : 25px; font-family : Sanserif;")
        lbl1.setAlignment(Qt.AlignHCenter)

        self.txt1 = QLineEdit()
        self.txt2 = QLineEdit()
        self.txt3 = QLineEdit()

        btn1 = QPushButton("Cancel", self)
        btn2 = QPushButton("Insert", self)

        btn1.clicked.connect(self.btn1Action)
        btn2.clicked.connect(self.btn2Action)

        self.vbox.addWidget(lbl1)
        self.vbox.addLayout(gbox)

        gbox.addWidget(lbl2, 0, 0)
        gbox.addWidget(self.txt1, 0, 1)
        gbox.addWidget(lbl3, 1, 0)
        gbox.addWidget(self.txt2, 1, 1)
        gbox.addWidget(lbl4, 2, 0)
        gbox.addWidget(self.txt3, 2, 1)
        gbox.addWidget(btn1, 3, 0)
        gbox.addWidget(btn2, 3, 1)

    def btn1Action(self):
        self.switch_back.emit(self)

    def btn2Action(self):
        msg = QMessageBox()
        if str(self.txt1.text()) == '' or str(self.txt2.text()) == '' or str(self.txt3.text()) == '':
            msg.warning(self, "Failed!", "Empty Fields!\nFill all the fields to insert record.")
        else:
            try:
                self.sql.insert(str(self.txt1.text()), int(self.txt2.text(), 16), int(self.txt3.text()))
                msg.information(self, "Success!", "Data Inserted\nName: {}\nRFID_UID: {}\nIncentives: {}".format(self.txt1.text(), self.txt2.text(), self.txt3.text()))
            except OperationalError:
                msg.warning(self, "Failed!", "Data Insertion Failed!\nNo Record Inserted")
        self.switch_back.emit(self)


class Admin(QDialog):
    switch_back = pyqtSignal(QDialog)
    switch_insert = pyqtSignal(SQLServer)
    switch_view = pyqtSignal(SQLServer, str)

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
        try:
            self.sql = SQLServer("localhost", "root", passwd="", database="mrbin")
            print("SQL Connection Success")
        except OperationalError:
            print("Error connecting to database")
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
        lbl1 = QLabel("Administrator Mode", self)
        lbl1.setStyleSheet("font : 30px; font-family : Sanserif;")
        lbl1.setAlignment(Qt.AlignHCenter)

        btn1 = QPushButton("View Records", self)
        btn2 = QPushButton("Insert Record", self)
        btn3 = QPushButton("Delete Record", self)
        btn4 = QPushButton("Modify Record", self)
        btn5 = QPushButton("Back", self)

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
        self.switch_view.emit(self.sql, None)

    def btn2Action(self):
        self.switch_insert.emit(self.sql)

    def btn3Action(self):
        pass

    def btn4Action(self):
        pass

    def btn5Action(self):
        self.switch_back.emit(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Admin()
    app.exec()
