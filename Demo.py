#CODE BY KEVIN
__author__ = "Kevin Chan"
__copyright__ = "Copyright (C) 2022 Kevin"
__license__ = "GPL-3.0"
__version__ = "0.1.1"


import os
import sys

from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, uic
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import UIrc_rc

import sqlite3


from configparser import ConfigParser

from multiprocessing import shared_memory

ui_dir = os.path.dirname(os.path.abspath(__file__))
ui_path = os.path.join(ui_dir,"UI")

config = ConfigParser()
config.read("Config.ini")

ui_1 = config.get('section_ui','Guide_val')
ui_2 = config.get('section_ui','Main_val')

form_1, base_1 = uic.loadUiType(os.path.join(ui_path,ui_1))
form_2, base_2 = uic.loadUiType(os.path.join(ui_path,ui_2))

global connectdb
global conpath
connectdb = None

global txtF
txtF = None

class Gui(base_1, form_1):
    def __init__(self):
        super(base_1, self).__init__()
        self.setupUi(self)

        self.setWindowIcon(QtGui.QIcon(':/icon/UI/UI_Element/icon/guide.png'))
        
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
        connt.execute("CREATE TABLE TODO(Task INTEGER, Title TEXT, Alarm TEXT, State TEXT);")
        connt.execute("INSERT INTO TODO VALUES (?, ?, ?, ?);",(0,"NOTITLE","None","BLOCKED"))
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
        self.setWindowIcon(QtGui.QIcon(':/icon/UI/UI_Element/icon/Memorandum_ico.ico'))
        
        self.setWindowFlags(QtCore.Qt.Dialog)

        self.anotherCall()

        #Main
        self.label_name.setText("Hi " + self.Userdb() )
        

        self.insertButton.clicked.connect(self.Insertdb)

        #SystemTimeshow
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.Timeshow)
        timer.start(1000)

        #Timer/Stopwatch
        self.StopwatchStartButton.clicked.connect(self.stopwatch)
        self.LapRow = 0
        self.StopwatchLapButton.clicked.connect(self.addlap)
        
        self.dial_sec.valueChanged.connect(self.timervalue)
        self.dial_min.valueChanged.connect(self.timervalue)
        self.TimerStartButton.clicked.connect(self.timerdisplay)
        self.TimerCancelButton.setEnabled(False)
        self.TimerCancelButton.setStyleSheet('color: DarkGray')
        self.TimerCancelButton.clicked.connect(self.timercancel)

        #ToDo
        self.todoButton.setIcon(self.style().standardIcon(QStyle.SP_DialogOkButton))
        self.todoButton_Check.setIcon(self.style().standardIcon(QStyle.SP_DialogApplyButton))
        self.todoButton_Weighup.setIcon(self.style().standardIcon(QStyle.SP_ArrowUp))
        self.updateTodo()
        self.AlarmTimeMM()
        self.dial_Adays.valueChanged.connect(self.timeCharge)
        self.dial_Ahour.valueChanged.connect(self.timeCharge)
        self.todoButton_Check.clicked.connect(self.todoCheck)
        self.todoButton_Del.clicked.connect(self.listDel)
        self.todoButton_Weighup.clicked.connect(self.todoWeighup)

        self.todoButton.clicked.connect(self.InsertTodo)
        self.lineEdit_Todo.returnPressed.connect(self.todoButton.click)
        
        #Alarm
        self.player = QMediaPlayer()
        self.stop = False 
        self.label_Music.installEventFilter(self)
        self.CancelButton_Alarm.setIcon(self.style().standardIcon(QStyle.SP_TitleBarCloseButton))
        self.MusicAdd_Button.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        self.updateAlarm()
        self.musicUpdate()
        self.watchdogAlarm()

     
        self.listWidget_Music.itemClicked.connect(self.changeMusic)
        self.radioButton_CtmS.toggled.connect(self.changeMusic)
        self.MusicAdd_Button.clicked.connect(self.musicAdd)
        self.CancelButton_Alarm.clicked.connect(self.delAlarm)
        

        #Search_Output
        self.tableWidget.setHorizontalHeaderLabels(["Number","Year","Month","Day","Time","Memo"])
        sizelist_column = range(5)
        for nb in sizelist_column:
            self.tableWidget.horizontalHeader().setSectionResizeMode(nb,QHeaderView.ResizeToContents)
        self.tableWidget.horizontalHeader().setSectionResizeMode(5,QHeaderView.Stretch)
        
        self.Search_Button.clicked.connect(self.Searchdb)
        self.lineEdit.returnPressed.connect(self.Search_Button.click)

        self.TimeFilter()

        #Info_Editor
        self.spinBox.valueChanged.connect(self.SB_range)
        self.Download_Data.clicked.connect(self.Download_db)

        self.txt_select.clicked.connect(self.txtselect)
        self.PasteButton.clicked.connect(self.PasteText)
        self.DataUpdate_Button.clicked.connect(self.dbUpdate)
      
        #Language & Control
        self.actionEnglish.triggered.connect(self.LangChangeE)
        self.actionChinese.triggered.connect(self.LangChangeC)
        self.actionJapanese.triggered.connect(self.LangChangeJ)
        self.actionQuit.triggered.connect(app.quit)

        #QTrayIcon
        QApplication.setQuitOnLastWindowClosed(False)

        icon = QtGui.QIcon(":/icon/UI/UI_Element/icon/Memorandum_ico.ico")
        self.trayIcon = QSystemTrayIcon()
        self.trayIcon.setIcon(icon)
        self.trayIcon.setVisible(True)

        self.trayIcon.activated.connect(self.onTrayIconActivated)

        menu = QMenu()
        
        show = QAction("Show",self)
        show.triggered.connect(self.showhide(1))
        menu.addAction(show)
        hide = QAction("Hide",self)
        hide.triggered.connect(self.showhide(0))
        menu.addAction(hide)
        
        quit = QAction("Quit",self)
        quit.triggered.connect(app.quit)
        menu.addAction(quit)

        self.trayIcon.setContextMenu(menu)

    def onTrayIconActivated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.hide()
        if reason == QSystemTrayIcon.Trigger:
            self.show()

    def showhide(self,arg):
        if arg == 0 :
            return self.hide
        if arg == 1 :
            return self.show
            

    def delAlarm(self):
        if self.listWidget_Alarm.currentRow() == -1:
            self.label_12.setText("<span style=\" color: red;\">Error NO select</span>")
        else:
            if self.checkBox.isChecked() == False:
                self.label_12.setText("<span style=\" color: red;\">Error Check Box is Not correct.</span>")
            else:
                text = "".join([str(x.text()) for x in self.listWidget_Alarm.selectedItems()])
                Atarget = str(text.split()[-3]+" "+text.split()[-2]+" "+text.split()[-1])
  
                global conpath
                db = conpath
                cnn = sqlite3.connect(db)
                c = cnn.cursor()
                c.execute("UPDATE TODO SET Alarm = 'None' WHERE Alarm = '"+Atarget+"' ;")
                cnn.commit()
                cnn.close()
                
                self.updateAlarm()
   

    def watchdogAlarm(self):
        dgTimer = QtCore.QTimer(self)
        dgTimer.start(15000)
        dgTimer.timeout.connect(self.catchAlarmTime)
        
    def catchAlarmTime(self):
        Now = QtCore.QDateTime.currentDateTime().toString("yyyy/M/d HH:mm AP")
        datetimeNow = Now.split()
    
        global conpath
        db = conpath
        cnn = sqlite3.connect(db)
        c = cnn.cursor()

        c.execute("SELECT Alarm,Task FROM TODO WHERE Alarm != 'None' ;")
        alarm = c.fetchall()
        time = 2359
        if len(alarm) == 0:
            self.label_12.setText("Today is NO Alarm")
        else:
            for t in alarm:
                fooAlarm = t
                day = fooAlarm[0].split()
                
                if day[0].split('/')[1] < datetimeNow[0].split('/')[1] or day[0].split('/')[2] < datetimeNow[0].split('/')[2]:
                    c.execute("UPDATE TODO SET Alarm = 'None' WHERE Task = "+str(fooAlarm[1])+";")
                    cnn.commit()
                if day == datetimeNow:
                    self.media_play()
                    c.execute("UPDATE TODO SET Alarm = 'None' WHERE Task = "+str(fooAlarm[1])+";")
                    cnn.commit()
                if day[0] == datetimeNow[0] :
                    atime = min(time,int(day[1].replace(":","")))
                    if atime == int(day[1].replace(":","")):
                        self.label_12.setText("Next Alarm:"+day[1])

        cnn.close()
        self.updateAlarm()


    def musicUpdate(self):
        music_path = os.path.dirname(os.path.abspath(__file__)) + "/Music"
        dir_list = os.listdir(music_path)
        for m in dir_list:
            self.listWidget_Music.addItem(m)

    def musicAdd(self):
        QFDM = QFileDialog()
        MFile = QFDM.getOpenFileName(self,"Add New Music", "","Music Files(*.mp3)")
        Mname = os.path.split(MFile[0])
        QtCore.QFile.copy(MFile[0],"./Music/"+Mname[1])
        self.listWidget_Music.clear()
        self.musicUpdate()

    def changeMusic(self):
        if self.radioButton_CtmS.isChecked():
            if self.listWidget_Music.currentRow() == -1:
                self.listWidget_Music.setCurrentRow(1)
            name = self.listWidget_Music.currentItem().text()
            alarm_path =  os.path.dirname(os.path.abspath(__file__)) + "/Music/" + name
            url = QtCore.QUrl.fromLocalFile(alarm_path)
            conten = QMediaContent(url)
            self.player.setMedia(conten)
            self.label_Music.setText(name)

    def media_play(self):
        if self.radioButton_CtmS.isChecked():
            self.player.play()
        else:
            music_path = "qrc:/music/Music/Alarm.mp3"
            url = QtCore.QUrl(music_path)
            conten = QMediaContent(url)
            self.player.setMedia(conten)
            self.player.play()
            self.label_Music.setText("Default_Alarm.mp3")

    def eventFilter(self, object, event):
        if event.type() == QtCore.QEvent.Enter:
            self.media_play()
            self.stop = True
            return True
        elif event.type() == QtCore.QEvent.Leave:
            self.player.stop()
            self.stop = False
        return False
    def updateAlarm(self):
        self.listWidget_Alarm.clear()
        global conpath
        db = conpath
        cnn = sqlite3.connect(db)
        c = cnn.cursor()
        
        ld = c.execute("SELECT Title,Alarm FROM TODO WHERE Alarm != 'None' ORDER BY Alarm;")
        for info in ld:
            hoge = info
            listText = str(hoge[0]) +'. ' + hoge[1]
            iconV = QListWidgetItem(listText)
            iconV.setData(QtCore.Qt.DecorationRole,QtGui.QIcon(':/image/UI/UI_Element/clock.png'))
            self.listWidget_Alarm.addItem(iconV)
        cnn.close()

    def AlarmTimeMM(self):
        Mtimer = QtCore.QTimer(self)
        Mtimer.start(1000)
        Mtimer.timeout.connect(self.updateTM)

    def updateTM(self):
        self.dateTimeEdit_Alarm.setMinimumDateTime(QtCore.QDateTime.fromString(QtCore.QDateTime.currentDateTime().toString("yyyy/M/d HH:mm AP"),"yyyy/M/d HH:mm AP").addSecs(300))
    
    def timeCharge(self):
        charge = QtCore.QDateTime.fromString(QtCore.QDateTime.currentDateTime().toString("yyyy/M/d HH:mm AP"),"yyyy/M/d HH:mm AP").addSecs(self.dial_Ahour.value()).addDays(self.dial_Adays.value())
        self.dateTimeEdit_Alarm.setDateTime(charge)

    def InsertTodo(self):
        global conpath
        db = conpath
        conn = sqlite3.connect(db)
        c = conn.cursor()
        
        c.execute("SELECT Task FROM TODO WHERE Task >= 0;")
        fooid = c.fetchall()
        taskid = int(''.join(map(str,fooid[-1])))+1

        ToDo = self.lineEdit_Todo.text()
        Alarm = self.dateTimeEdit_Alarm.dateTime().toString("yyyy/M/d HH:mm AP")
        if self.checkBox_Alarm.isChecked() == True:
            c.execute("INSERT INTO TODO VALUES(?, ?, ?, ?)",(taskid,ToDo,Alarm,"Live"))
            self.checkBox_Alarm.setChecked(False)
        else:
            c.execute("INSERT INTO TODO VALUES(?, ?, ?, ?)",(taskid,ToDo,"None","Live"))
        conn.commit()
        conn.close()

        if self.checkBox_Memo.isChecked() == True:
            TodoMemo = self.plainTextEdit_todoMemo.toPlainText()
            self.Insert_Data.setPlainText("###This is ToDo Memo ###\n" + "*** Title ***\n"+ ToDo + "\n----------\n" + TodoMemo)
            self.Insertdb()
            self.checkBox_Memo.setChecked(False)
        
        self.lineEdit_Todo.clear()
        self.plainTextEdit_todoMemo.clear()
        self.updateTodo()
    
    def updateTodo(self):
        self.listWidget_todo.clear()
        self.listWidget_trash.clear()
        global conpath
        db = conpath
        cnn = sqlite3.connect(db)
        c = cnn.cursor()
        
        ld = c.execute("SELECT Task,Title FROM TODO WHERE State = 'Live' ORDER BY Task;")
        for info in ld:
            hoge = info
            listText = str(hoge[0]) +'. ' + hoge[1]
            iconV = QListWidgetItem(listText)
            iconV.setData(QtCore.Qt.DecorationRole,QtGui.QIcon(':/image/UI/UI_Element/live.png'))
            self.listWidget_todo.addItem(iconV)
        td = c.execute("SELECT Task,Title,State FROM TODO WHERE Task < 0 ORDER BY Task DESC;")
        for info in td:
            foo = info
            listText = str(foo[0]) +'. ' + foo[1]
            iconV = QListWidgetItem(listText)
            if foo[2] == "Done":
                iconV.setData(QtCore.Qt.DecorationRole,QtGui.QIcon(':/image/UI/UI_Element/done.png'))
            else:
                iconV.setData(QtCore.Qt.DecorationRole,QtGui.QIcon(':/image/UI/UI_Element/off.png'))
            self.listWidget_trash.addItem(iconV)
        self.label_8.setText("<span style=\" color: green;\">List Update...</span>")
        cnn.close()

    def todoWeighup(self):
        if self.listWidget_todo.currentRow() == -1:
            self.label_8.setText("<span style=\" color: red;\">Error you need select ToDo task</span>")
        else:
            if self.listWidget_todo.currentRow() == 0:
                self.label_8.setText("<span style=\" color: red;\">THE top ONE!</span>")
            else:
                global conpath
                db = conpath
                cnnrs = sqlite3.connect(db)
                rs = cnnrs.cursor()
                ckid = str(self.listWidget_todo.currentRow() +1)
                ckidup = str(self.listWidget_todo.currentRow())
                rs.execute("UPDATE TODO SET Task = ?  WHERE Task = ?;",(str(999),ckid))
                rs.execute("UPDATE TODO SET Task = ?  WHERE Task = ?;",(ckid,ckidup))
                rs.execute("UPDATE TODO SET Task = ?  WHERE Task = ?;",(ckidup,str(999)))
                cnnrs.commit()
                cnnrs.close()
                self.updateTodo()

    def todoCheck(self):
        if self.listWidget_todo.currentRow() == -1:
            self.label_8.setText("<span style=\" color: red;\">Error you need select ToDo task</span>")
        else:
            global conpath
            db = conpath
            cnn = sqlite3.connect(db)
            c = cnn.cursor()
            c.execute("SELECT Task FROM TODO ORDER BY Task;")
            fooid = c.fetchall()
            trashid = str(int(''.join(map(str,fooid[0]))) -1)
            ckid = str(self.listWidget_todo.currentRow() +1)
            
            if self.radioButton_Done.isChecked():
                c.execute("UPDATE TODO SET Task = ? , State = 'Done' WHERE Task = ?;",(trashid,ckid))
                cnn.commit()
            else:
                c.execute("UPDATE TODO SET Task = ? , State = 'Off' WHERE Task = ?;",(trashid,ckid))
                cnn.commit()
            
            sort = cnn.cursor()
            rs = sort.execute("SELECT Task FROM TODO WHERE Task > ?;",(ckid))
            for id in rs:
                foo = id
                fooid = str(''.join(map(str,foo)))
                newid = str(int(''.join(map(str,foo))) - 1)
                roder = "UPDATE TODO SET Task = "+ newid +" WHERE Task = "+ fooid+";"
                c.execute(roder)
           
            cnn.commit()
            cnn.close()

            self.updateTodo()

    def listDel(self):
        if self.listWidget_trash.currentRow() == -1:
            self.label_8.setText("<span style=\" color: red;\">Error you need select Trash Can.</span>")
      
        else:
            trashid = str(-1)
            if self.listWidget_trash.currentRow() != 0:
                trashid = str((int(self.listWidget_trash.currentRow())+1) *-1)
            global conpath
            db = conpath
            cnn = sqlite3.connect(db)
            
            d = cnn.cursor()
            d.execute("DELETE FROM TODO WHERE Task = "+trashid+" ;")
            cnn.commit()

            sort = cnn.cursor()
            tc = sort.execute("SELECT Task FROM TODO WHERE Task < "+trashid+" ORDER BY Task DESC;")
            for id in tc:
                foo = id
                
                fooid = str(''.join(map(str,foo)))
                newid = str(int(''.join(map(str,foo))) +1)
                d.execute("UPDATE TODO SET Task = "+ newid +" WHERE Task = "+ fooid +";")

            cnn.commit()
            cnn.close()

            self.updateTodo()

        
    def timervalue(self):
        self.spinBox_sec.setValue(int(self.dial_sec.value()))
        self.spinBox_min.setValue(int(self.dial_min.value()))

    def timercancel(self):
        self.Ttimer.stop()
        self.lcdNumber.display('0')
        self.lcdNumber_2.display('0')
        self.lcdNumber_3.display('0')
        self.progressBar_timer.setValue(0)
        self.player.stop()

        self.TimerStartButton.setEnabled(True)
        self.TimerStartButton.setStyleSheet('color: black')
        self.TimerCancelButton.setEnabled(False)
        self.TimerCancelButton.setStyleSheet('color: DarkGray')

    def timercounter(self):
        global Tsec, Tmin, Thor, Total, Totalnow
        Totalnow = Totalnow+1
        self.progressBar_timer.setValue(int((Totalnow/Total)*100))
        if Tsec == Tmin == Thor == 0 :
            if self.checkBox_timerAlarm.isChecked():
                self.trayIcon.showMessage("Time Out !","Push Cancel to Stop Alarm")
                self.Ttimer.stop()
                self.media_play()
            else:
                self.trayIcon.showMessage("Time Out !","Push Cancel to restart.")
                self.Ttimer.stop()
            
        else:
            if Tsec == 0:
                if Tmin == 0:
                    Thor = Thor-1
                    Tmin = 60
                Tmin = Tmin-1
                Tsec = 60
            Tsec = Tsec-1
        self.lcdNumber.display(str(Thor))
        self.lcdNumber_2.display(str(Tmin))
        self.lcdNumber_3.display(str(Tsec))

    def timerdisplay(self):
        global Tsec, Tmin, Thor, Total, Totalnow
        Tsec = self.spinBox_sec.value()
        Tmin = self.spinBox_min.value()
        Thor = self.spinBox_hor.value()
        Total = Tsec + (Tmin*60) + (Thor*3600) + 1
        Totalnow = 0

        self.Ttimer = QtCore.QTimer(self)
        self.Ttimer.start(1000)
        self.Ttimer.timeout.connect(self.timercounter)
        self.TimerStartButton.setEnabled(False)
        self.TimerStartButton.setStyleSheet('color: DarkGray')
        self.TimerCancelButton.setEnabled(True)
        self.TimerCancelButton.setStyleSheet('color: black')


    def timepush(self):
        global Wtms, Wsec, Wmin
        Wtms = Wtms + 1
        if Wtms == 100:
            Wtms = 0
            Wsec = Wsec+1
        elif Wsec == 60 :
            Wsec = 0
            Wmin = Wmin+1
        self.label_10.setText(str(Wmin)+":"+str(Wsec)+"."+str(Wtms))

    def stopwatch(self):
        if self.StopwatchStartButton.text() == "Start":
            self.StopwatchStartButton.setText("Stop")
            self.StopwatchStartButton.setStyleSheet('color: red')
            self.swtime = QtCore.QTimer(self)
            self.swtime.start(10)
            global Wtms, Wsec, Wmin
            Wtms = Wsec = Wmin = 0
            self.swtime.timeout.connect(self.timepush)
            
        else:
            self.swtime.stop()
            self.StopwatchStartButton.setText("Start")
            self.StopwatchStartButton.setStyleSheet('color: black')
            self.StopwatchLapButton.setText("Clear")
            self.StopwatchLapButton.setStyleSheet('color: green')
            
            self.StopwatchStartButton.setEnabled(False)
            self.StopwatchStartButton.setStyleSheet('color: DarkGray')

    def addlap(self):
        if self.StopwatchStartButton.text() == "Stop":
            self.LapRow = self.LapRow+1
            self.Lap_Browser.append("<strong><span style=\" color: LightBlue; \">Lap Number.</span></strong>"+str(self.LapRow)+"  ----------->>>   "+self.label_10.text())
        elif self.StopwatchLapButton.text() == "Clear":
            self.StopwatchLapButton.setText("Lap")
            self.StopwatchLapButton.setStyleSheet('color: black')
            self.StopwatchStartButton.setStyleSheet('color: black')
            self.Lap_Browser.clear()
            self.LapRow = 0
            self.label_10.setText("00:00.00")
            self.StopwatchStartButton.setEnabled(True)

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
        self.SystemOP_Browser.append("<strong><span style=\"background-image: url(':/image/UI/UI_Element/bbk.png'); color:#583759; \">Insert Data ID = <span style=\"color:DarkOrange; \"> 'Numb."+ str(dataid) +" '</span> # update to database.</span></strong>" )
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
        bm = [1,3,5,7,8]
        
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
            self.checkBox_4.setChecked(False)

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
            self.checkBox_5.setChecked(False)
            self.trayIcon.showMessage("Just Now...","New Memo Updated")
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
        curent_time = QtCore.QDateTime.currentDateTime()
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
        elif arg == 6 :
            time = curent_time.toString('dd:MM:yyyy')

        elif arg == 0 :
            time = curent_time
        return time

    def Timeshow(self):
        t = self.Timeget(1)
        self.label_time.setText(t)
        self.label_time_2.setText(t)

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


    def LangChangeE(self):
        if config.get('section_language','Language_val') == "English":
            self.trayIcon.showMessage("Language NO Changed !","Engilsh")
        else:
            config.set('section_language','Language_val','English')
            config.set('section_ui','Guide_val','Guide_en.ui')
            config.set('section_ui','main_val','Main_en.ui')
            with open('Config.ini','w') as configfile:
                config.write(configfile)
            QMessageBox.information(None,"Language -> English","Language config is changed.\n"" You need reboot App...")
    def LangChangeC(self):
        if config.get('section_language','Language_val') == "Chinese":
            self.trayIcon.showMessage("语言选项未改变！","中文")
        else:
            config.set('section_language','Language_val','Chinese')
            config.set('section_ui','Guide_val','Guide_cn.ui')
            config.set('section_ui','main_val','Main_cn.ui')
            with open('Config.ini','w') as configfile:
                config.write(configfile)
            QMessageBox.information(None,"语言 -> 中文","已改变换为中文注册文件\n"" 需要重新启动程序...")
    def LangChangeJ(self):
        if config.get('section_language','Language_val') == "Japanese":
            self.trayIcon.showMessage("ランゲージ変わりませんてした。","日本語")
        else:
            config.set('section_language','Language_val','Japanese')
            config.set('section_ui','Guide_val','Guide_jp.ui')
            config.set('section_ui','main_val','Main_jp.ui')
            with open('Config.ini','w') as configfile:
                config.write(configfile)
            QMessageBox.information(None,"言語 -> 日本語","ランゲージ切り替えました。\n"" アプリ再起動が必要です...")  

    def anotherCall(self):
        cTimer = QtCore.QTimer(self)
        cTimer.start(2000)
        cTimer.timeout.connect(self.checkNew)
    def checkNew(self):
         if single.buf[0] == 0:
             self.show()
             single.buf[0] = 1       


if __name__ == '__main__':

    key = "Memorandum"

    try:
        single = shared_memory.SharedMemory(key, create=False)
        single.buf[0] = 0
        sys.exit("App is runing")
        
    except:
        single = shared_memory.SharedMemory(key, create=True,size=1)
        single.buf[0] = 1

        app = QApplication(sys.argv)
        demo = Gui()
        demo.show()

    try:
        sys.exit(app.exec_())

    except SystemExit:
        print("Closing Window ...")
