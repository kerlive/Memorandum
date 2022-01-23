import os
import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDateTime, QTimer , Qt
from PyQt5 import QtGui, uic

import sqlite3
from Crypto.Cipher import AES


ui_path = os.path.dirname(os.path.abspath(__file__))

form_1, base_1 = uic.loadUiType(os.path.join(ui_path,'Guide.ui'))
form_2, base_2 = uic.loadUiType(os.path.join(ui_path,'Main.ui'))
form_3, base_3 = uic.loadUiType(os.path.join(ui_path,'Login.ui'))

global connectdb
global conpath
connectdb = None

global txtF
txtF = None
"""
class Crypto():
    def encypto(self,arg):

    def dicypto(self,arg):

"""

class Gui(base_1, form_1):
    def __init__(self):
        super(base_1, self).__init__()
        self.setupUi(self)

        self.setWindowTitle('Guide')
        self.setFixedSize(400,300)

        self.pushButton_3.clicked.connect(self.EmptyCheck)
        self.pushButton_2.clicked.connect(self.select)
        self.pushButton.clicked.connect(self.checkin)


    def loadMain(self):
        self.main = Main()
        self.main.show()
        self.close()

    def NoDBError(self):
        Error = QMessageBox.critical(
            self,
            "Oh dear!",
            "No database access now, SYSTEM can't be run .",
            buttons=QMessageBox.Cancel | QMessageBox.Yes ,
            defaultButton=QMessageBox.Cancel,
        )
        if Error == QMessageBox.Cancel:
            self.textBrowser.append("<span style=\"color:red;\"> YOU NEED Chooese Database in your disk! </span>")
        elif Error == QMessageBox.Yes:
            self.select()

    def checkin(self):
        global connectdb
        ct = connectdb
        if ct == 1:
            self.loadMain()
        else:
            self.NoDBError()

    def select(self):
        QFD = QFileDialog()
        FN = QFD.getOpenFileName(self,"Open you own database", "","Database Files(*.db)")
        
        if os.path.splitext(str(FN[0]))[1] != ".db":
            self.textBrowser.append("<span style=\"color:red;\"> Database is not select! </span>")
        else:
            global conpath
            conpath = str(FN[0])
            global connectdb
            connectdb = 1
            ccdcl = '<strong><span style=\"background-color: papayawhip; color: green;\">%s</span></strong>' % str(FN[0])
            self.textBrowser.append(ccdcl +" is Selected")
    
    def dbCreator(self):
        
        connt = sqlite3.connect(str(self.lineEdit.text())+".db")
        
        connt.execute("CREATE TABLE USER (Name TEXT);")
    
        nm = self.lineEdit_2.text()
        connt.execute("INSERT INTO USER VALUES(?);",[nm])
        connt.commit()
        connt.execute("CREATE TABLE MEMORANDUM (ID INTEGER, Year INTEGER, Month INTEGER, Day INTEGER, Time TEXT, Memo TEXT);")
        connt.execute("INSERT INTO MEMORANDUM VALUES (?, ?, ?, ?, ?, ?);",(0, Main.Timeget(self,5) ,Main.Timeget(self,4), Main.Timeget(self,3), Main.Timeget(self,2), 'None'))
        connt.commit()
        connt.close()
        cncl = '<span style=\" color: cyan;\">%s</span>' % nm
        cdcl = '<span style=\" color: blue;\">%s</span>' % self.lineEdit.text()
        self.textBrowser.append("Hi Mr/Ms "+ cncl +" New database  '"+ cdcl +".db' is Created now. ")
        
        
    def EmptyCheck(self):
        if self.lineEdit.text() == '' or self.lineEdit_2.text() == '':
            Error = QMessageBox.critical(
            self,
            "Oh dear!",
            "Database and User Name can't be Empty!!!",
            buttons=QMessageBox.Yes ,
            defaultButton=QMessageBox.Yes,
        )
        else:
            self.dbCreator()
    

class Main(base_2, form_2):
    def __init__(self):
        super(base_2, self).__init__()
        self.setupUi(self)

        self. setFixedSize(750,600)
        self.setWindowTitle('Daily Database')

    
        
            
        self.label_name.setText("Hi " + self.Userdb() )
        
        self.insertButton.clicked.connect(self.Insertdb)


        self.tableWidget.horizontalHeader().setSectionResizeMode(1)
        self.tableWidget.setHorizontalHeaderLabels(["Number","Year","Month","Day","Time","Memo"])
        self.Search_Button.clicked.connect(self.Searchdb)

        self.TimeFilter()
        
        #timeshow
        timer = QTimer(self)
        timer.timeout.connect(self.Timeshow)
        timer.start(1000)
        
        self.spinBox.valueChanged.connect(self.SB_range)
        self.Download_Data.clicked.connect(self.Download_db)

        self.txt_select.clicked.connect(self.txtselect)
        self.PasteButton.clicked.connect(self.PasteText)
        self.DataUpdate_Button.clicked.connect(self.dbUpdate)

              
        

    def SB_range(self):
        maxid = self.Getdbrange()
        self.spinBox.setMaximum(int(maxid))

    def Userdb(self):
        global conpath
        db = conpath
        cnn = sqlite3.connect(db)
        c = cnn.cursor()
        
        d = c.execute("SELECT * FROM USER;")
        for info in d:
            hoge = info
        cnn.close()
        # covert data tuple to string
        data= ''.join(hoge)
        return data    
    
    def Insertdb(self):
        global conpath
        db = conpath
        conn = sqlite3.connect(db)
        c = conn.cursor()
        memo = self.Insert_Data.toPlainText()
        yy = self.Timeget(5)
        mm = self.Timeget(4)
        dd = self.Timeget(3)
        tt = self.Timeget(2)
        
        # Select ID number form last tuple element for new memo ID
        c.execute("SELECT ID FROM MEMORANDUM;")
        fooid = c.fetchall()
        dataid = int(''.join(map(str,fooid[-1]))) + 1

        c.execute("INSERT INTO MEMORANDUM VALUES (?, ?, ?, ?, ?, ?);",(dataid,yy,mm,dd,tt,memo))
        conn.commit()
        conn.close()
        self.SystemOP_Browser.append("<strong><span style=\"background-image: url('UI_Element/bbk.png'); color:#583759; \">Insert Data ID = <span style=\"color:DarkOrange; \"> 'Numb."+ str(dataid) +" '</span> # update to database.</span></strong>" )
        self.Insert_Data.clear()

    def Searchdb(self):
        global conpath
        db = conpath
        conn = sqlite3.connect(db)
        c = conn.cursor()

        keyword = self.lineEdit.text()
        sqlite3_select_like =  "SELECT * FROM MEMORANDUM WHERE Memo LIKE '%"+keyword+"%';"
        c.execute(sqlite3_select_like)
        thread = 0
        rowct = c.fetchall()
        if len(rowct) == 0:
            print("debug")
            self.tableWidget.setRowCount(0)
            self.label_6.setText("<strong>Search Done System No Results!</strong>")
            self.progressBar_search.setValue(100)
        else:
            self.tableWidget.setRowCount(0)
            for row_number, row_data in enumerate(rowct):
                self.tableWidget.insertRow(row_number)
                thread += 100/len(rowct)
                self.progressBar_search.setValue(round(thread))
                for column_number, data in enumerate(row_data):
                    self.tableWidget.setItem(row_number, column_number, QTableWidgetItem(str(data)))
            self.label_6.setText("<span style=\" color: Green;\">Search Done!</span>")

        conn.close()

    
    def TimeFilter(self):

        global conpath
        db = conpath
        conn = sqlite3.connect(db)
        c = conn.cursor()
        c.execute("SELECT Year FROM MEMORANDUM;")
        Yr = c.fetchall()
        lasty = int(''.join(map(str,Yr[-1])))
        fsty = int(''.join(map(str,Yr[0]))) 

        for y in range(fsty,lasty+1):
            yr = str(y)
            self.comboBox.addItem(yr)
        for m in range(1,13):
            mon = str(m)
            self.comboBox_2.addItem(mon)
        for d in range(1,32):
            da = str(d)
            self.comboBox_3.addItem(da)


    def Getdbrange(self):
        global conpath
        db = conpath
        conn = sqlite3.connect(db)
        c = conn.cursor()
        c.execute("SELECT ID FROM MEMORANDUM;")
        mub = c.fetchall()
        last = int(''.join(map(str,mub[-1])))
        conn.close
        return last
        

    def txtselect(self):
        QFDT = QFileDialog()
        FNT = QFDT.getOpenFileName(self,"Open Text", "","Txt Files(*.txt)")
        self.label_4.setText("2.Path Selected:"+str(FNT[0]))
        global txtF
        txtF = str(FNT[0])
    
    def PasteText(self):
        global txtF

        if txtF == None:
            Error = QMessageBox.warning(
            self,
            "Oh dear!",
            "Please, you need select txt file first.",
            buttons=QMessageBox.Yes ,
            defaultButton=QMessageBox.Yes,
        )
        
        elif self.checkBox_4.isChecked() == True :
            file1 = open(txtF,"r")
            data = file1.read()
            self.plainTextEdit.clear()
            self.plainTextEdit.appendPlainText(data)
            self.label_7.setText(".txt file copy and Pasted to the Editor.")

        else:
            Error = QMessageBox.warning(
            self,
            "Oh dear!",
            "Please, Be sure checkBox is Checked!",
            buttons=QMessageBox.Yes ,
            defaultButton=QMessageBox.Yes,
        )

    def dbUpdate(self):
        if self.checkBox_5.isChecked() == True :
            global conpath
            db = conpath
            conn = sqlite3.connect(db)
            c = conn.cursor()
            Tx = self.plainTextEdit.toPlainText()
            Id = self.spinBox.value()
            c.execute("UPDATE MEMORANDUM SET Memo = ? WHERE ID = ?",(Tx,Id,))
            conn.commit()
            conn.close()
            self.label_7.setText("New Memo Updated!")
        else:
            Error = QMessageBox.warning(
            self,
            "Oh dear!",
            "You real wanne Update Your Memo? <br> OK, Be sure checkBox is Checked!",
            buttons=QMessageBox.Yes ,
            defaultButton=QMessageBox.Yes,
        )
            

    def strcover(self, arg):
        d = arg
        for info in d:
            foo = info
        dataR = ''.join(foo)
        return dataR

    def Timeget(self,arg):
        curent_time = QDateTime.currentDateTime()
        if arg == 1 :
            time = curent_time.toString('hh:mm:ss')
        elif arg == 2 :
            time = curent_time.toString('hh:mm')
        elif arg == 3 :
            time = curent_time.toString('dd')
        elif arg == 4 :
            time = curent_time.toString('MM')
        elif arg == 5 :
            time = curent_time.toString('yyyy')
        return time

    def Timeshow(self):
        t = self.Timeget(1)
        self.label_time.setText(t)

    def Download_db(self,arg):
        self.plainTextEdit.clear()
        global conpath
        db = conpath
        conn = sqlite3.connect(db)
        c = conn.cursor()
        Nb = str(self.spinBox.value())
        md = c.execute("SELECT Memo FROM MEMORANDUM WHERE ID = ?;",(Nb,))
        MemEd = self.strcover(md)
        self.plainTextEdit.appendPlainText(MemEd)
        conn.close
        self.label_7.setText("Memo Download from database #"+ Nb +">>")
        

"""class UserLogin(base_3, form_3):
    def __init__(self):
        super(base_3, self).__init__()
        self.setupUi(self)

        self.setFixedSize(240,130)
        self.setWindowTitle('ACCESS CONTROL')
        
        self.Login_Button.clicked.connect(self.Password)
    
    def Password(self):
        global Password
        Password = self.Password_Text.Text()
        dbp = Decryption(db.p)
        if p == dbp :
            loadMain
        else:
            Error

"""

if __name__ == '__main__':

    app = QApplication(sys.argv)

    demo = Gui()
    demo.show()

    try:
        sys.exit(app.exec_())

    except SystemExit:
        print("Closing Window ...")
