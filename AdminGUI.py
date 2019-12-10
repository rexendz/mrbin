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
        self.width = 480
        self.height = 320
        self.icon = QIcon('/home/rexendz/mrbin/res/favicon.png')
        self.vbox = QVBoxLayout()
        self.sql = sql
        self.lbl1 = None
        self.table = None
        self.btn1 = None
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
        self.setStyleSheet("background-color: #297045;")
        self.setWindowIcon(self.icon)
        self.setLayout(self.vbox)
        self.setWindowFlags(Qt.FramelessWindowHint)

    def InitComponents(self):

        result = self.sql.readAll()

        self.table = QTableWidget(self)
        self.table.setRowCount(len(result))
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['ID', 'Name', 'RFID-UID', 'Incentives'])
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)

        for i in range(len(result)):
            for j in range(4):
                if j == 2:
                    self.table.setItem(i, j, QTableWidgetItem("{:08X}".format(result[i][j])))
                else:
                    self.table.setItem(i, j, QTableWidgetItem(str(result[i][j])))

        self.lbl1 = QLabel("MR BIN Users", self)
        self.lbl1.setStyleSheet("font : 40px; font-family : Sanserif;")
        self.lbl1.setAlignment(Qt.AlignHCenter)

        self.btn1 = QPushButton(self)
        self.btn1.setText("Close")
        self.btn1.clicked.connect(self.btn1Action)

        self.btn1.setStyleSheet("color : black; background-color : #aeb7b3; font : 20px; font-family : Sanserif;")

        self.table.setGeometry(0, 0, 320, 240)
        self.table.resizeRowsToContents()
        self.table.resizeColumnsToContents()

        self.vbox.addWidget(self.lbl1)
        self.vbox.addWidget(self.table)
        self.vbox.addWidget(self.btn1)

    def btn1Action(self):
        self.switch_back.emit(self)


class InsertRecords(QDialog):
    switch_back = pyqtSignal(QDialog)

    def __init__(self, sql):
        super().__init__()
        self.title = "MR BIN"
        self.left = 0
        self.top = 0
        self.width = 480
        self.height = 320
        self.icon = QIcon('/home/rexendz/mrbin/res/favicon.png')
        self.vbox = QVBoxLayout()
        self.gbox = QGridLayout()

        self.sql = sql

        self.txt1 = None
        self.txt2 = None
        self.txt3 = None

        self.lbl4 = None

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
        gbox = QGridLayout()

        lbl1 = QLabel("Insert Record", self)
        lbl2 = QLabel("Name", self)
        lbl3 = QLabel("RFID in Hex", self)
        self.lbl4 = QLabel("Incentives", self)

        lbl2.setStyleSheet("color : #FAFAFA; font : 20px; font-family : Sanserif;")
        lbl3.setStyleSheet("color : #FAFAFA; font : 20px; font-family : Sanserif;")
        self.lbl4.setStyleSheet("color : #FAFAFA; font : 20px; font-family : Sanserif;")

        lbl1.setStyleSheet("font : 40px; font-family : Sanserif; color : #e1efe6;")
        lbl1.setAlignment(Qt.AlignHCenter)

        self.txt1 = QLineEdit()
        self.txt2 = QLineEdit()
        self.txt3 = QLineEdit()

        self.txt3.setValidator(QIntValidator())

        self.txt1.setStyleSheet("background-color: #212121; font : 20px; font-family : Sanserif; color : #F5F5F5;")
        self.txt2.setStyleSheet("background-color: #212121; font : 20px; font-family : Sanserif; color : #F5F5F5;")
        self.txt3.setStyleSheet("background-color: #212121; font : 20px; font-family : Sanserif; color : #F5F5F5;")

        btn1 = QPushButton("Cancel", self)
        btn2 = QPushButton("Insert", self)

        btn1.setStyleSheet("background-color : #d50000; color : #FAFAFA; font : 20px; font-family : Sanserif;")
        btn2.setStyleSheet("background-color : #1B5E20; color : #FAFAFA; font : 20px; font-family : Sanserif;")

        btn1.clicked.connect(self.btn1Action)
        btn2.clicked.connect(self.btn2Action)

        self.vbox.addWidget(lbl1)
        self.vbox.addLayout(gbox)

        gbox.addWidget(lbl2, 0, 0)
        gbox.addWidget(self.txt1, 0, 1)
        gbox.addWidget(lbl3, 1, 0)
        gbox.addWidget(self.txt2, 1, 1)
        gbox.addWidget(self.lbl4, 2, 0)
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
                msg.information(self, "Success!",
                                "Data Inserted\nName: {}\nRFID_UID: {}\nIncentives: {}".format(self.txt1.text(),
                                                                                               self.txt2.text(),
                                                                                               self.txt3.text()))
            except OperationalError:
                msg.warning(self, "Failed!", "Data Insertion Failed!\nNo Record Inserted")
        self.switch_back.emit(self)


class DeleteRecords(ViewRecords):
    def __init__(self, sql):
        super().__init__(sql)
        self.btn2 = None
        self.comboBox = None
        self.users = self.sql.readAll()
        self.name = []
        self.InitNew()

    def InitNew(self):

        self.btn2 = QPushButton("Delete Selected", self)
        self.btn2.setStyleSheet("background-color : #d30000; color : #FAFAFA; font : 20px; font-family : Sanserif;")

        for user in self.users:
            self.name.append(user[1])

        self.comboBox = QComboBox(self)
        for i in range(len(self.users)):
            self.comboBox.addItem(self.name[i])

        self.btn2.clicked.connect(self.btn2Action)

        self.vbox.addWidget(self.comboBox)
        self.vbox.addWidget(self.btn2)
        self.vbox.addWidget(self.btn1)

    def btn2Action(self):
        name = self.comboBox.currentText()
        ret = QMessageBox.question(self,
                                   "Delete Record",
                                   "Are you sure you want to delete {}'s record?".format(name),
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if ret == QMessageBox.Yes:
            self.sql.delete("Name", self.comboBox.currentText())
            QMessageBox.information(self,
                                    "Delete Record",
                                    "You have successfully deleted {}'s record.".format(name))
            self.vbox.removeWidget(self.btn1)
            self.vbox.removeWidget(self.btn2)
            self.vbox.removeWidget(self.comboBox)
            self.vbox.removeWidget(self.lbl1)
            self.vbox.removeWidget(self.table)
            self.InitComponents()
            self.InitNew()
            self.show()

        else:
            pass


class Admin(QDialog):
    switch_back = pyqtSignal(QDialog)
    switch_insert = pyqtSignal()
    switch_view = pyqtSignal()
    switch_delete = pyqtSignal()

    def __init__(self, sql):
        super().__init__()
        self.title = "MR BIN"
        self.left = 0
        self.top = 0
        self.width = 480
        self.height = 320
        self.icon = QIcon('/home/rexendz/mrbin/res/favicon.png')
        self.vbox = QVBoxLayout()
        self.usr = None
        self.pwd = None
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
        self.setStyleSheet("background-color: #297045;")
        self.setWindowIcon(self.icon)
        self.setLayout(self.vbox)
        self.setWindowFlags(Qt.FramelessWindowHint)

    def InitComponents(self):
        lbl1 = QLabel("Administrator Mode", self)
        lbl1.setStyleSheet("font : 40px; font-family : Sanserif; color : #e1efe6")
        lbl1.setAlignment(Qt.AlignHCenter)

        btn1 = QPushButton("View Records", self)
        btn2 = QPushButton("Insert Record", self)
        btn3 = QPushButton("Delete Record", self)
        btn4 = QPushButton("Modify Record", self)
        btn5 = QPushButton("Back", self)

        btn1.setStyleSheet("background-color : #aeb7b3; color : #1b2f33; font : 20px; font-family : Sanserif;")
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
        self.switch_view.emit()

    def btn2Action(self):
        self.switch_insert.emit()

    def btn3Action(self):
        self.switch_delete.emit()

    def btn4Action(self):
        pass

    def btn5Action(self):
        self.switch_back.emit(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Admin()
    app.exec()
