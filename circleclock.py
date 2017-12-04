#!/usr/bin/python
# -*- coding: utf-8 -*-

# ***************************License:***********************************
"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
# Author: Sajed Rakhshani
# E-mail: SajedRakhshani@msn.com
# gitlab: https://gitlab.com/sajed68/circle-clock-widget
# Start: 13 Mehr 1396
# First Release 13 Mehr 1396
# Third Release 24 Aban 1396
# version 2.0.1
# Release date: 28 Aban
# #####################################################


# the libraries for ui menu:
from PyQt5.QtWidgets import QApplication, QWidget, QToolTip, QPushButton, QMessageBox, QMainWindow, QMenu, qApp, QTableWidget,QTableWidgetItem,QVBoxLayout, QLabel, QGridLayout, QLineEdit, QSlider, QFontComboBox, QGroupBox, QSpinBox, QColorDialog, QProgressBar
from PyQt5.QtGui import QFont, QPainter, QColor, QPolygonF, QImage, QTransform, QPen
from PyQt5.QtCore import QCoreApplication
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QPointF
import math
from PIL import Image, ImageQt, ImageDraw
from PyQt5.QtCore import QDateTime, QDate, QTimer # because I want get away from time for calculation the time!
import sys
sys.path.append('./utils')
import jdatetime  # use side library to convert date
import json
import requests # to update envents from times.ir
from lxml import html
import time
import codecs


class ui_widget(QMainWindow):
    def __init__(self):
        super(ui_widget, self).__init__()
        self.setWindowTitle('CircleClock')
        
        self.__read_config__()
        QToolTip.setFont(QFont(self.eventfont, self.eventfontsize))
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setGeometry(self.x, self.y, 400, 400)
        self.setMinimumWidth(350)
        self.setMinimumHeight(400)
        self.setMaximumWidth(400)
        self.setMaximumHeight(400)
        self.faceb = Image.new(mode='RGBA', color=(0,0,0,0), size=(350,350))#.open('./arts/clockface_2.png')
        self.face = Image.new(mode='RGBA', color=(0,0,0,0), size=(350,350))
        self.angle = 0
        self.clockface = ImageQt.ImageQt(self.face)
        self.clockface2 = ImageQt.ImageQt(self.faceb)#.scaled(350,350)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(500)
        self.clockwork = ':'
        self.cal = cal(self.events, self.holidays, self.myevents)
        self.cal.hide()
        self.settings = settings(self.face, self.faceb, self.config, self.events, self.holidays)
        self.settings.hide()
        self.__update__()
        # following line is a setting to remove icon at taskbar, BUT IT MUST BE QMainWindow:
        self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint) # To remove Title bar
        # now need to call shower method!
        self.show()
        self.raise_()
 


    def paintEvent(self, event):
        ''' in the method elements of Clock were drawing.'''
        self.qp = QPainter()
        self.qp.begin(self)
        self.qp.setRenderHints(QPainter.HighQualityAntialiasing | QPainter.Antialiasing)
        self.__draw_Clock__()
        self.qp.end()
        
    
    
    def __draw_Clock__(self):
        #First Draw outter Circle:
        self.qp.drawImage(0, 0, self.clockface2)
        self.qp.drawImage(0, 0, self.clockface)
        # Draw clock number ponits :
        self.__draw_clock_number_points__()
        # write the date:
        self.qp.setPen(QColor(self.datecolor[0],self.datecolor[1],self.datecolor[2]))
        self.qp.setBrush(QColor(self.datecolor[0],self.datecolor[1],self.datecolor[2]))
        self.qp.setFont(QFont(self.datefont, self.datefontsize)) # XP Vosta #
        self.qp.drawText(175 - 75, 180, 150, 75, Qt.AlignCenter, self.persian_date)
        
        self.qp.setPen(QColor(self.clockcolor[0],self.clockcolor[1],self.clockcolor[2]))
        self.qp.setBrush(QColor(self.clockcolor[0],self.clockcolor[1],self.clockcolor[2]))
        self.qp.setFont(QFont(self.clockfont, self.clockfontsize)) #
        self.qp.drawText(175 - 85, 130, 171, 35, Qt.AlignCenter, self.persian_time)
        
        self.qp.setBrush(QColor(self.seconds_color[0],self.seconds_color[1],self.seconds_color[2]))
        self.qp.setPen(QColor(self.seconds_color[0],self.seconds_color[1],self.seconds_color[2]))
        self.qp.drawRect(100, 175, 150, 1)
        pen = QPen()
        pen.setWidth(10)

                
        
        
    
    def __draw_clock_number_points__(self):
        x1 = 175
        y1 = 175
        _, _, ps = self.time
        ps = int(ps) - 15
        ps += (15+45) if ps < 0 else 0
          
        #ps -= 1 if ps % 2 == 1 else 0
        for i in range(0, 60, 1):
            poly = QPolygonF()
            a = (i+1) * math.pi  / 30
            if True: #i != ps:
                self.qp.setBrush(QColor(self.seconds_color[0],self.seconds_color[1],self.seconds_color[2]))
                self.qp.setPen(QColor(self.seconds_color[0],self.seconds_color[1],self.seconds_color[2]))
                c, v = self.__rotate_the_points__(a, 1, -110)
                self.qp.drawEllipse(x1 - c - 3, y1 - v - 3, 6, 6)
            if i == ps:
                col = QColor(self.second_color[0],self.second_color[1],self.second_color[2])
                self.qp.setBrush(col)
                self.qp.setPen(col)
                #self.qp.setOpacity(0.0)
                c, v = self.__rotate_the_points__(a, 1, -110)
                self.qp.drawEllipse(x1 - c - 4, y1 - v - 4, 8, 8)
                #self.qp.setOpacity(1.0)
                
        
    def __rotate_the_points__(self, a, x, y):
        xr = y * math.cos(a) + x * math.sin(-a)
        yr = -y * math.sin(-a) + x * math.cos(a)
        return xr, yr
        
        
    def __update__(self):
        D, T = QDateTime.currentDateTime().toString(Qt.ISODate).split('T')
        self.date = D.split('-')
        self.time = T.split(':')
        self.num_day = QDate.currentDate().dayOfWeek()
        hour, minute, sec = self.time

        sec = 6 * int(sec) * math.pi / 180
        x_sec = self.__un_round__(math.sin(sec) * 90)
        y_sec = self.__un_round__(math.cos(sec) * 90)
        self.sec = (x_sec, y_sec)

        mint = 6 * int(minute) * math.pi / 180
        x_mint = self.__un_round__(math.sin(mint) * 70)
        y_mint = self.__un_round__(math.cos(mint) * 70)
        self.minute = (x_mint, y_mint)
        
        hour = (30 * (int(hour)%12 + int(minute) / 60.0)) * math.pi / 180
        x_hour = self.__un_round__(math.sin(hour) * 40)
        y_hour = self.__un_round__(math.cos(hour) * 40)
        self.hour = (x_hour, y_hour)
        
        ##config reupdated##
        self.clockfont = self.config['clockfont']
        self.clockfontsize = self.config['clockfontsize']
        self.datefont = self.config['datefont']
        self.datefontsize = self.config['datefontsize']
        self.eventfont = self.config['eventfont']
        self.eventfontsize = self.config['eventfontsize']
        self.clockcolor = self.config['clockcolor']
        self.datecolor = self.config['datecolor']
        self.second_color = self.config['second_color']
        self.seconds_color = self.config['seconds_color']
        QToolTip.setFont(QFont(self.eventfont, self.eventfontsize))
        #
        
        self.__get_persian_date__()
        self.__show_events__()
        

    def __get_persian_date__(self):
        year, month, day = self.date
        year = int(year)
        month = int(month)
        day = int(day)
        jd = jdatetime.GregorianToJalali(year, month, day)
        year = str(jd.jyear)
        month = str(jd.jmonth)
        day = str(jd.jday)
        self.jdate = [jd.jyear, jd.jmonth, jd.jday] 
        month_dict = {1:u'فروردین',
                      2:u'اردیبهشت',
                      3:u'خرداد',
                      4:u'تیر',
                      5:u'مرداد',
                      6:u'شهریور',
                      7:u'مهر',
                      8:u'آبان',
                      9:u'آذر',
                      10:u'دی',
                      11:u'بهمن',
                      12:u'اسفند',
            }
        day_dict = {0:u'یکشنبه',
                    1:u'دوشنبه',
                    2:u'سه شنبه',
                    3:u'چهارشنبه',
                    4:u'پنجشنبه',
                    5:u'جمعه',
                    6:u'شنبه',
                    7:u'یکشنبه'}
        dic = u'۰۱۲۳۴۵۶۷۸۹'
        y = ''.join([dic[int(i)] for i in year])
        d = ''.join([dic[int(i)] for i in day])
        self.persian_date = day_dict[self.num_day] + u'\n' + d + u' ' + month_dict[int(month)] + u' ' + y
        ph, pm, ps = self.time
        self.persian_time = u''.join([dic[int(i)] for i in ph]) + self.clockwork+u''.join([dic[int(i)] for i in pm])+self.clockwork+u''.join([dic[int(i)] for i in ps])

        
        
    def closeEvent(self, event):
        self.update()
        self.__write_config__()
        event.accept()
        self.timer.stop()
        print("Now I'm quiting...")
        sys.exit()
        

    def __show_events__(self):
        event = self.persian_date
        event = event.split('\n')[1]
        event = event.split(' ')
        event = event[0] + ' ' + event[1]
        myevent = self.myevents.get(event, u'')
        myevent = u'' if myevent == u'' else u'\n یادآور: '+myevent
        self.event_text = self.events.get(event, None) 
        self.event_text = self.event_text if self.event_text is not None else u'امروز اتفاق خاصی نیفتاده!'
        self.event_text += myevent
        self.setToolTip(self.event_text)
        
    def animate(self):
        self.clockwork = u':' if self.clockwork == u'.' else u'.'
        self.angle += 6
        self.angle = self.angle % 360
        self.clockface2 = ImageQt.ImageQt(self.faceb.rotate(self.angle))#.scaled(350,350)
        self.clockface = ImageQt.ImageQt(self.face)
        self.__update__()
        self.update()
        QApplication.processEvents()
        
        
    def mousePressEvent(self, event):
        self.offset = event.pos()

    def mouseMoveEvent(self, event):
        x=event.globalX()
        y=event.globalY()
        x_w = self.offset.x()
        y_w = self.offset.y()
        self.move(x-x_w, y-y_w)
        
    
    def __read_config__(self):
        try: 
            with codecs.open('events.json', 'r', 'utf-8-sig') as events : # open('events.json', 'r') as events:
                self.events = json.load(events)
            with codecs.open('holidays.json', 'r', 'utf-8-sig') as holidays : 
                self.holidays = json.load(holidays)
        except:
            print("I can't load events file :(")
            self.events = {u"پایان":0}
            self.holidays = {u"پایان":0}
        try:
            with open('config.json', 'r') as configfile:
                self.config = json.load(configfile)
                if self.config['open'] == 'last':
                    self.x = self.config['x']
                    self.y = self.config['y']
                else:
                    self.x = 1900-400
                    self.y = 1000-400
                self.clockfont = self.config['clockfont']
                self.clockfontsize = self.config['clockfontsize']
                self.datefont = self.config['datefont']
                self.datefontsize = self.config['datefontsize']
                self.eventfont = self.config['eventfont']
                self.eventfontsize = self.config['eventfontsize']
                self.clockcolor = self.config['clockcolor']
                self.datecolor = self.config['datecolor']
                a = self.config["face_color"]
                #a = self.config["out_trans"]
                a = self.config["seconds_color"]
                a = self.config["second_color"]
                a = self.config["faceb_color"]
                print('config file loaded')
        except:
            self.config = {"y": 560, "x": 1520, "open": "last", "clockfont": "Koodak", "datefont":"XP Vosta", "clockfontsize":34, "datefontsize":20, "eventfont":"Koodak", "eventfontsize":15, "face_color":(255,160,0,128), "clockcolor":(255,255,255), "datecolor":(255,255,255),  "seconds_color":(255,255,255), "second_color":(178,34,34), "faceb_color":(255,160,0, 128)}
            self.x = self.config['x']
            self.y = self.config['y']
            self.clockfont = self.config['clockfont']
            self.clockfontsize = self.config['clockfontsize']
            self.datefont = self.config['datefont']
            self.datefontsize = self.config['datefontsize']
            self.eventfont = self.config['eventfont']
            self.eventfontsize = self.config['eventfontsize']
            self.clockcolor = self.config['clockcolor']
            self.datecolor = self.config['datecolor']
            print("config can't loaded")
        try:
            with open('config.json', 'w') as outfile:
                json.dump(self.config, outfile)
        except:
                pass
            
        try:
            with codecs.open('myevents.json', 'r', 'utf-8-sig') as reminder : 
                self.myevents = json.load(reminder)
        except:
            self.myevents = {}
            print('there is no reminder, so I created new one!')
            with open('myevents.json', 'w') as outfile:
                json.dump(self.myevents, outfile)
    
    def __write_config__(self):
        pos = self.pos()
        x = pos.x()
        y = pos.y()
        if self.config['open'] == 'last':
            self.config['x'] = int(x)
            self.config['y'] = int(y)
            with open('config.json', 'w') as outfile:
                json.dump(self.config, outfile)
        
        
        
    def __cal_show__(self):
        self.cal.get_date(self.jdate+[self.persian_date])
        self.cal.show()
        print ('pass')
    
    
    def __settings__(self):
        self.settings.__open__(self.persian_date)
        self.settings.show()
        print ('settings menu opened')
            
            
    def __un_round__(self,n):
        r = round(n)
        c = math.ceil(n)
        f = math.floor(n)
        if int(r) == int(f):
            return c
        else:
            return f
        

    def contextMenuEvent(self, event):
       
           cmenu = QMenu(self)

           quitAct = cmenu.addAction("بسته شم؟")
           event_cal = cmenu.addAction("نمایش تقویم")
           setting = cmenu.addAction("تنظیمات")
           #updateevent = cmenu.addAction("رویدادها رو بروز کنم؟ (اینترنت میخواهم!)")
           action = cmenu.exec_(self.mapToGlobal(event.pos()))

           
           if action == quitAct:
               self.close()
           elif action == event_cal:
               self.__cal_show__()
           elif action == setting:
               self.__settings__()

# ##########################################################################################################################################################Section II 
class cal(QWidget):
    def __init__(self, ev, hd, mev):
        super(cal, self).__init__()
        self.month_dict = {1:u'فروردین',
                      2:u'اردیبهشت',
                      3:u'خرداد',
                      4:u'تیر',
                      5:u'مرداد',
                      6:u'شهریور',
                      7:u'مهر',
                      8:u'آبان',
                      9:u'آذر',
                      10:u'دی',
                      11:u'بهمن',
                      12:u'اسفند',
            }
        self.setWindowTitle(u'نمای تقویم')
        self.setGeometry(500, 500, 400, 400)
        self.setMinimumWidth(725)
        self.setMinimumHeight(450)
        self.setMaximumWidth(725)
        self.setMaximumHeight(450)
        self.events = ev
        self.holidays = hd
        self.myevents = mev
        self.tableWidget = QTableWidget() # Calendar table view
        self.next_monthB = QPushButton(u'ماه بعد')  # Next month button
        self.prev_monthB = QPushButton(u'ماه قبل')  # prev month button
        self.next_monthB.clicked.connect(self.go_next_month)
        self.prev_monthB.clicked.connect(self.go_prev_month)
        self.reminderB = QPushButton(u'یادآور')  # Add self events
        self.reminderB.clicked.connect(self.reminder_submit)
        self.reminderL = QLabel("۱۲ شهریور")
        self.reminderE = QLineEdit()
        self.label = QLabel("text") # event showr!
        
        self.createTable(1,1,1,1)
        self.text = ' '
        self.month_idx = 1
        self.month_name = self.month_dict[self.month_idx]
        self.month_label = QLabel(self.month_name) # month showr!
        self.layout = QGridLayout()
        self.setLayout(self.layout) 
        
        self.layout.addWidget(self.month_label, 0, 0, 1, 1) 
        self.layout.addWidget(self.tableWidget, 1, 0, 1, -1) 
        self.layout.addWidget(self.reminderB, 2, 0, 1, 1)
        self.layout.addWidget(self.reminderL, 2, 1, 1, 1)
        self.layout.addWidget(self.reminderE, 2, 2, 1, 4)
        self.layout.addWidget(self.next_monthB, 3, 0, 1, 3) 
        self.layout.addWidget(self.prev_monthB, 3, 3, 1, 3) 
        self.layout.addWidget(self.label, 4, 0, 1, -1)  

        self.show()
        
    def get_date(self, date):
        print (date)
        self.date = date
        day = date[2]
        month = date[1]
        self.month_idx = month
        year = date[0]
        per_day = date[3].split('\n')[0]
        days = [u"شنبه", u"یکشنبه",u"دوشنبه", u"سه شنبه", u"چهارشنبه", u"پنجشنبه", u"جمعه"]
        day_idx = days.index(per_day)
        full_week = day + (6-day_idx)
        firstday_idx = 7 - full_week % 7
        self.tableWidget.clear()
        self.createTable(firstday_idx, month, day, year)
        self.on_click()
        self.show_text()
        self.show_month()

    
    def get_events(self):
        pass
    
    
    def createTable(self, firstday_idx, month, day, year):
        # Create table
        self.tableWidget.setRowCount(7)
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setStyleSheet("QTableView {selection-background-color: red}")
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setVisible(False)
        self.tableWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.tableWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        for x in range(0,7):
            for y in range(0,7):
                self.tableWidget.setItem(x,y, QTableWidgetItem(u''))
                self.tableWidget.item(x,y).setFlags(QtCore.Qt.ItemIsEnabled)
        days = [u"شنبه", u"یکشنبه",u"دوشنبه", u"سه شنبه", u"چهارشنبه", u"پنجشنبه", u"جمعه"]
        for i in range(7):
            self.tableWidget.setItem(0,i, QTableWidgetItem(days[i]))
            self.tableWidget.item(0, i).setBackground(QColor(100,150,250, 255))
            self.tableWidget.item(0, i).setFlags(QtCore.Qt.ItemIsEnabled)
    
        day_num = 31 if month <= 6 else 30
        if month == 12:
            day_num = 30 if year % 4 == 1 else 29
        for i in range(day_num):
            j = i + firstday_idx
            x = j / 7
            y = j % 7
            item, num_text = self.create_per_num(i+1)
            #print(num_text + u' ' + self.month_dict[month])
            if self.myevents.get(num_text + u' ' + self.month_dict[month], None) is not None:
                item.setBackground(QColor(100,250,100))
            elif self.holidays.get(num_text + u' ' + self.month_dict[month], None) is not None or y%7 == 6:
                item.setBackground(QColor(250,100,100))
            else:
                item.setBackground(QColor(100,150,150, 100))
            self.tableWidget.setItem(x+1,y, item)
            if j-1 == day:
                self.tableWidget.setCurrentCell(x+1,y)
     
        self.tableWidget.move(0,0)
        self.tableWidget.cellClicked.connect(self.on_click)
        for i in range(7):
            self.tableWidget.setColumnWidth(i, 100)
        
        
    def on_click(self):
        myevent = ' '
        try:
            day = self.tableWidget.currentItem().text()
            r = self.tableWidget.currentRow()
            day_month = day + ' ' + self.month_dict[self.month_idx]
            myevent = self.myevents.get(day_month, ' ')
            if r == 0:
                self.reminderL.setText(u'یک روز را انتخاب کن')
                self.reminderB.setEnabled(False)
                self.reminderE.setEnabled(False)
            elif day != '':
                self.reminderL.setText(day_month)
                self.reminderB.setEnabled(True)
                self.reminderE.setEnabled(True)
            else:
                self.reminderL.setText(u'یک روز را انتخاب کن')
                self.reminderB.setEnabled(False)
                self.reminderE.setEnabled(False)
        except:
            day_month = '___'
        a = '\n' + u'یادآور: ' + myevent
        myevent = ' ' if myevent == ' ' else a
        self.text = self.events.get(day_month, ' ') + myevent
        print (myevent)
        self.show_text()
        
        
    def show_text(self):
        self.label.setText(self.text)
        self.label.setWordWrap(True)
        
        #self.label.setAlignment(Qt.AlignLeft)
        
    def show_month(self):
        self.month_name = self.month_dict[self.month_idx]
        self.month_label.setText(self.month_name)
        
        
    def reminder_submit(self):
        print(self.myevents)
        text = self.reminderE.text()
        day_month = self.reminderL.text()
        my_prev_envent  = self.myevents.get(day_month, None)
        if text == '':
            if my_prev_envent is not None:
                self.myevents.pop(day_month)
                print('I removed new event to your file!')
                with open('myevents.json', 'w') as outfile:
                    json.dump(self.myevents, outfile)
        else :
            print(day_month)
            self.myevents[day_month] = text
            self.reminderE.setText('')
            print('I added new event to your file!')
            with open('myevents.json', 'w') as outfile:
                json.dump(self.myevents, outfile)
        
        
    
    def go_next_month(self):
        if self.month_idx < 12:
            month = self.month_idx
            self.month_idx = self.month_idx % 12 + 1
            #print(self.date)
            self.date[1] = self.month_idx
            day = self.date[2]
            year = self.date[0]
            per_day, other_parts = self.date[3].split('\n')
            days = [u"شنبه", u"یکشنبه",u"دوشنبه", u"سه شنبه", u"چهارشنبه", u"پنجشنبه", u"جمعه"]
            day_idx = days.index(per_day)
            day_num = 31 if month <= 6 else 30
            if month == 12:
                day_num = 30 if year % 4 == 1 else 29
            day_on_next = day + (day_num-day) +day_idx
            last_day = days[day_on_next % 7]
            d,m,y = other_parts.split(' ')
            m = self.month_dict[self.month_idx]
            other_parts = d + ' ' + m + ' ' + y
            self.date[3] = last_day+'\n'+other_parts
            self.get_date(self.date)
            self.show_month()
        else:
            pass
        
    def go_prev_month(self):
        if self.month_idx > 1:
            month = self.month_idx
            self.month_idx -= 1
            if self.month_idx == 0 : self.month_idx == 12
            print(self.date)
            self.date[1] = self.month_idx
            day = self.date[2]
            year = self.date[0]
            per_day, other_parts = self.date[3].split('\n')
            days = [u"شنبه", u"یکشنبه",u"دوشنبه", u"سه شنبه", u"چهارشنبه", u"پنجشنبه", u"جمعه"]
            day_idx = days.index(per_day)
            day_num = 31 if month-1 <= 6 else 30
            if month == 1:
                day_num = 30 if year % 4 == 1 else 29
            full_week = day + (6-day_idx)
            firstday_idx = 7 - full_week % 7
            last_day_of_prev = firstday_idx - 1 if firstday_idx != 0 else 6
            print(days[last_day_of_prev])
            diff_day = day_num - day
            #last_day = days[(diff_day%7 + last_day_of_prev)%7]
            last_day = days[last_day_of_prev]
            self.date[2] = day_num
            d,m,y = other_parts.split(' ')
            m = self.month_dict[self.month_idx]
            other_parts = d + ' ' + m + ' ' + y
            self.date[3] = last_day+'\n'+other_parts
            self.get_date(self.date)
            self.show_month()
        else:
            pass
            
            
    def create_per_num(self, num):
        d = u'۰۱۲۳۴۵۶۷۸۹'
        x = int(num / 10)
        y = num % 10
        r = d[x]+d[y] if x > 0 else d[y]
        item = QTableWidgetItem()
        item.setText(r)
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        return item, r
        
    def closeEvent(self, event):
        #self.tableWidget.clear()
        self.hide()
        event.ignore()
        
# ##################################################################################################################################################Section III
class settings(QWidget):
    def __init__(self, f, fb, c, e, h):
        super(settings, self).__init__()
        self.setWindowTitle('تنظیمات')
        self.setGeometry(500, 500, 400, 400)
        self.setMinimumWidth(725)
        self.setMinimumHeight(500)
        self.setMaximumWidth(725)
        self.setMaximumHeight(500)
        
        self.face = f
        self.faceb = fb
        #self.facemask = Image.open('./arts/clockfacealphamask.png').convert('L')
        self.facebmask = Image.open('./arts/clockface_2alphamask.png').resize((350,350))

        self.events = e
        self.holidays = h
        
        self.config = c
        self.clockcolor = self.config['clockcolor']
        self.datecolor = self.config['datecolor']
        self.seconds_color = self.config['seconds_color']
        self.second_color = self.config['second_color']
        
        ### color setting
        self.alpha_slider = QSlider(Qt.Horizontal)
        self.alpha_slider.valueChanged.connect(self.get_alpha_slider)
        self.alpha_slider_label = QLabel('شدت محو شدن پس زمینه:')
        self.alpha_slider_value_label = QLabel('text')
        
        self.red_slider = QSlider(Qt.Horizontal)
        self.red_slider.valueChanged.connect(self.get_alpha_slider)
        self.red_slider_label = QLabel('رنگ قرمز:')
        self.red_slider_value_label = QLabel('text')
        
        self.blue_slider = QSlider(Qt.Horizontal)
        self.blue_slider.valueChanged.connect(self.get_alpha_slider)
        self.blue_slider_label = QLabel('رنگ آبی:')
        self.blue_slider_value_label = QLabel('text')
        
        self.green_slider = QSlider(Qt.Horizontal)
        self.green_slider.valueChanged.connect(self.get_alpha_slider)
        self.green_slider_label = QLabel('رنگ سبز:')
        self.green_slider_value_label = QLabel('text')
        

        self.alpha_sliderb = QSlider(Qt.Horizontal)
        self.alpha_sliderb.valueChanged.connect(self.get_alpha_sliderb)
        self.alpha_sliderb_label = QLabel('شدت محو شدن:')
        self.alpha_sliderb_value_label = QLabel('text')
        
        self.red_sliderb = QSlider(Qt.Horizontal)
        self.red_sliderb.valueChanged.connect(self.get_alpha_sliderb)
        self.red_sliderb_label = QLabel('رنگ قرمز:')
        self.red_sliderb_value_label = QLabel('text')
        
        self.blue_sliderb = QSlider(Qt.Horizontal)
        self.blue_sliderb.valueChanged.connect(self.get_alpha_sliderb)
        self.blue_sliderb_label = QLabel('رنگ آبی:')
        self.blue_sliderb_value_label = QLabel('text')
        
        self.green_sliderb = QSlider(Qt.Horizontal)
        self.green_sliderb.valueChanged.connect(self.get_alpha_sliderb)
        self.green_sliderb_label = QLabel('رنگ سبز:')
        self.green_sliderb_value_label = QLabel('text')
        ### clock shower setting
        self.clockfont_selector = QFontComboBox()
        self.clockfont_selector.currentFontChanged.connect(self.clock_currentFontChange)
        self.clockfontsize_selector = QSpinBox()
        self.clockfontsize_selector.setValue(self.config["clockfontsize"])
        self.clockfontsize_selector.valueChanged.connect(self.setclockfontsize)
        self.clockcolorpicker = QPushButton()
        self.clockcolorpicker.setText('')
        color = QColor(self.clockcolor[0],self.clockcolor[1],self.clockcolor[2]).name()
        self.clockcolorpicker.setStyleSheet(u"QPushButton {background-color: "+color+u';color:red;}')
        self.clockcolorpicker.clicked.connect(self.pickclockcolor)
        
        ### date shower setting
        self.datefont_selector = QFontComboBox()
        self.datefont_selector.currentFontChanged.connect(self.date_currentFontChange)
        self.datefontsize_selector = QSpinBox()
        self.datefontsize_selector.setValue(self.config["datefontsize"])
        self.datefontsize_selector.valueChanged.connect(self.setdatefontsize)
        self.datecolorpicker = QPushButton()
        self.datecolorpicker.setText('')
        color = QColor(self.datecolor[0],self.datecolor[1],self.datecolor[2]).name()
        self.datecolorpicker.setStyleSheet(u"QPushButton {background-color: "+color+u';color:red;}')
        self.datecolorpicker.clicked.connect(self.pickdatecolor)
        ### event popup setting
        self.eventfont_selector = QFontComboBox()
        self.eventfont_selector.currentFontChanged.connect(self.event_currentFontChange)
        self.eventfontsize_selector = QSpinBox()
        self.eventfontsize_selector.setValue(self.config["eventfontsize"])
        self.eventfontsize_selector.valueChanged.connect(self.seteventfontsize)
        ### event updater objects:
        self.update_events = QPushButton(u"به روز رسانی رویدادها")
        self.update_events.clicked.connect(self.eventUpdater)
        self.update_events_progressbar = QProgressBar()
        ### seconds color objects:
        self.secondslabel = QLabel(u"تنظیم رنگ حلقه:")
        self.secondscolorpicker = QPushButton("")
        color = QColor(self.seconds_color[0],self.seconds_color[1],self.seconds_color[2]).name()
        self.secondscolorpicker.setStyleSheet(u"QPushButton {background-color: "+color+u';color:red;}')
        self.secondscolorpicker.clicked.connect(self.picksecondscolor)
        self.secondlabel = QLabel(u"تنظیم رنگ ثانیه شمار:")
        self.secondcolorpicker = QPushButton("")
        color = QColor(self.second_color[0],self.second_color[1],self.second_color[2]).name()
        self.secondcolorpicker.setStyleSheet(u"QPushButton {background-color: "+color+u';color:red;}')
        self.secondcolorpicker.clicked.connect(self.picksecondcolor)
        
        
        self.__set_init_values__()
        ### Group for background color
        self.group_color = QGroupBox()
        self.group_color.setTitle(u"تنظیم رنگ:")
        colorgrid = QGridLayout()
        colorgrid.addWidget(self.alpha_slider_label, 0, 0)
        colorgrid.addWidget(self.alpha_slider, 0, 1)
        colorgrid.addWidget(self.alpha_slider_value_label, 0, 3)
        
        colorgrid.addWidget(self.red_slider_label, 1, 0)
        colorgrid.addWidget(self.red_slider, 1, 1)
        colorgrid.addWidget(self.red_slider_value_label, 1, 3)
        
        colorgrid.addWidget(self.blue_slider_label, 3, 0)
        colorgrid.addWidget(self.blue_slider, 3, 1)
        colorgrid.addWidget(self.blue_slider_value_label, 3, 3)
        
        colorgrid.addWidget(self.green_slider_label, 2, 0)
        colorgrid.addWidget(self.green_slider, 2, 1)
        colorgrid.addWidget(self.green_slider_value_label, 2, 3)
        
        colorgrid.addWidget(self.alpha_sliderb_label, 4, 0)
        colorgrid.addWidget(self.alpha_sliderb, 4, 1)
        colorgrid.addWidget(self.alpha_sliderb_value_label, 4, 3)
        
        colorgrid.addWidget(self.red_sliderb_label, 5, 0)
        colorgrid.addWidget(self.red_sliderb, 5, 1)
        colorgrid.addWidget(self.red_sliderb_value_label, 5, 3)
        
        colorgrid.addWidget(self.blue_sliderb_label, 7, 0)
        colorgrid.addWidget(self.blue_sliderb, 7, 1)
        colorgrid.addWidget(self.blue_sliderb_value_label, 7, 3)
        
        colorgrid.addWidget(self.green_sliderb_label, 6, 0)
        colorgrid.addWidget(self.green_sliderb, 6, 1)
        colorgrid.addWidget(self.green_sliderb_value_label, 6, 3)
        
        self.group_color.setLayout(colorgrid)
        ### Group for clock font
        self.group_clockfont = QGroupBox()
        self.group_clockfont.setTitle(u"تنظیم قلم ساعت:")
        clockfontgrid = QGridLayout()
        clockfontgrid.addWidget(self.clockfont_selector, 0, 0)
        clockfontgrid.addWidget(self.clockfontsize_selector, 0, 1)
        clockfontgrid.addWidget(self.clockcolorpicker, 0, 2)
        self.group_clockfont.setLayout(clockfontgrid)
        ### Group for date font
        self.group_datefont = QGroupBox()
        self.group_datefont.setTitle(u"تنظیم قلم تاریخ:")
        datefontgrid = QGridLayout()
        datefontgrid.addWidget(self.datefont_selector, 0, 0)
        datefontgrid.addWidget(self.datefontsize_selector, 0, 1)
        datefontgrid.addWidget(self.datecolorpicker, 0, 2)
        self.group_datefont.setLayout(datefontgrid)
        ### Group for event font
        self.group_eventfont = QGroupBox()
        self.group_eventfont.setTitle(u"تنظیم قلم نمایش رویداد:")
        eventfontgrid = QGridLayout()
        eventfontgrid.addWidget(self.eventfont_selector, 0, 0)
        eventfontgrid.addWidget(self.eventfontsize_selector, 0, 1)
        self.group_eventfont.setLayout(eventfontgrid)
        ### Group for  update events
        self.group_eventupdate = QGroupBox()
        self.group_eventupdate.setTitle(u"تنطیمات بروزرسانی:")
        updategrid = QGridLayout()
        updategrid.addWidget(self.update_events, 0,0)
        updategrid.addWidget(self.update_events_progressbar, 0, 1)
        self.group_eventupdate.setLayout(updategrid)
        ### Group for seconds
        self.group_second = QGroupBox()
        self.group_second.setTitle(u"تنظیم رنگ حلقه ثانیه شمار:")
        secondgrid = QGridLayout()
        secondgrid.addWidget(self.secondslabel, 0, 0)
        secondgrid.addWidget(self.secondscolorpicker, 0, 1)
        secondgrid.addWidget(self.secondlabel, 1, 0)
        secondgrid.addWidget(self.secondcolorpicker, 1, 1)
        self.group_second.setLayout(secondgrid)
 
        
                
        self.layout = QGridLayout()
        self.setLayout(self.layout) 
        
        self.layout.addWidget(self.group_color, 0, 0, 1, -1)
        self.layout.addWidget(self.group_clockfont, 1, 0)
        self.layout.addWidget(self.group_datefont, 1, 1)
        self.layout.addWidget(self.group_eventfont, 1, 2, 1, 1)
        self.layout.addWidget(self.group_eventupdate, 2,0, 1, 2)
        self.layout.addWidget(self.group_second, 2,2, 1, 1)
        
        
        self.show()
        
    
    def get_alpha_slider(self):
        value = 255.0 * (self.alpha_slider.value()+1) / 100 
        value = self.__change_nums__(value)
        self.alpha_slider_value_label.setText(value)
        
        value = 255.0 * (self.red_slider.value()+1) / 100 
        value = self.__change_nums__(value)
        self.red_slider_value_label.setText(value)
        
        value = 255.0 * (self.green_slider.value()+1) / 100 
        value = self.__change_nums__(value)
        self.green_slider_value_label.setText(value)
        
        value = 255.0 * (self.blue_slider.value()+1) / 100 
        value = self.__change_nums__(value)
        self.blue_slider_value_label.setText(value)
        
        self.__update_alpha__()
    
    def get_alpha_sliderb(self):
        value = 255.0 * (self.alpha_sliderb.value()+1) / 100 
        value = self.__change_nums__(value)
        self.alpha_sliderb_value_label.setText(value)
        
        value = 255.0 * (self.red_sliderb.value()+1) / 100 
        value = self.__change_nums__(value)
        self.red_sliderb_value_label.setText(value)
        
        value = 255.0 * (self.green_sliderb.value()+1) / 100 
        value = self.__change_nums__(value)
        self.green_sliderb_value_label.setText(value)
        
        value = 255.0 * (self.blue_sliderb.value()+1) / 100 
        value = self.__change_nums__(value)
        self.blue_sliderb_value_label.setText(value)
        
        self.__update_alphab__()
        
    def __change_nums__(self, num):
        num_dicts = {'1':u'۱', '2':u'۲', '3':u'۳', '4':u'۴', '5':u'۵', '6':u'۶', '7':u'۷', '8':u'۸', '9':u'۹', '0':u'۰'}
        num = str(int(num))
        per_num = [num_dicts[i] for i in num]
        out = per_num[0]
        for i in range(1, len(per_num)):
            out += per_num[i]
        return out
        
        
    def __set_init_values__(self):
        #r, g, b, a = self.face.getpixel((500, 500))
        numred, numgreen, numblue, numalpha = self.config["face_color"]
        numredb, numgreenb, numblueb, numalphab = self.config["faceb_color"]
        
        valuered = self.__change_nums__(numred)
        valueblue = self.__change_nums__(numblue)
        valuegreen = self.__change_nums__(numgreen)
        valuealpha = self.__change_nums__(numalpha)

        self.alpha_slider_value_label.setText(valuealpha)
        self.red_slider_value_label.setText(valuered)
        self.blue_slider_value_label.setText(valueblue)
        self.green_slider_value_label.setText(valuegreen)
        
        valueredb = self.__change_nums__(numredb)
        valueblueb = self.__change_nums__(numblueb)
        valuegreenb = self.__change_nums__(numgreenb)
        valuealphab = self.__change_nums__(numalphab)
 
        self.alpha_sliderb_value_label.setText(valuealphab)
        self.red_sliderb_value_label.setText(valueredb)
        self.blue_sliderb_value_label.setText(valueblueb)
        self.green_sliderb_value_label.setText(valuegreenb)
        
        a = int(100.0 * numalpha/255 - 1)
        r = int(100.0 * numred/255 - 1)
        b = int(100.0 * numblue/255 - 1)
        g = int(100.0 * numgreen/255 - 1)
        
        ab = int(100.0 * numalphab/255 - 1)
        rb = int(100.0 * numredb/255 - 1)
        bb = int(100.0 * numblueb/255 - 1)
        gb = int(100.0 * numgreenb/255 - 1)

        self.alpha_slider.setValue(a)
        self.red_slider.setValue(r)
        self.blue_slider.setValue(b)
        self.green_slider.setValue(g)
        
        self.alpha_sliderb.setValue(ab)
        self.red_sliderb.setValue(rb)
        self.blue_sliderb.setValue(bb)
        self.green_sliderb.setValue(gb)

        
        self.__update_alpha__()
        self.__update_alphab__()
        self.clockfont_selector.setCurrentFont(QFont(self.config["clockfont"]))
        self.datefont_selector.setCurrentFont(QFont(self.config["datefont"]))
        self.eventfont_selector.setCurrentFont(QFont(self.config["eventfont"]))
    ### clock functions:
    def clock_currentFontChange(self):
        font = self.clockfont_selector.currentFont().family()
        self.config["clockfont"] = font
        
    def setclockfontsize(self):
        size = self.clockfontsize_selector.value()
        if type(size) == type(1):
            self.config["clockfontsize"] = size

            
    def pickclockcolor(self):
        color = QColorDialog.getColor()
        if color.name() != u'#000000':
            self.clockcolor = [color.red(), color.green(), color.blue()]
            self.config['clockcolor'] = self.clockcolor
            self.clockcolorpicker.setStyleSheet(u"QPushButton {background-color: "+color.name()+u';color:red;}')

    ### date functions:
    def date_currentFontChange(self):
        font = self.datefont_selector.currentFont().family()
        self.config["datefont"] = font
        
    def setdatefontsize(self):
        size = self.datefontsize_selector.value()
        if type(size) == type(1):
            self.config["datefontsize"] = size
            
    def pickdatecolor(self):
        color = QColorDialog.getColor()
        if color.name() != u'#000000':
            self.datecolor = [color.red(), color.green(), color.blue()]
            self.config['datecolor'] = self.datecolor
            self.datecolorpicker.setStyleSheet(u"QPushButton {background-color: "+color.name()+u';color:red;}')
    ### event functions
    def event_currentFontChange(self):
        font = self.eventfont_selector.currentFont().family()
        self.config["eventfont"] = font
        
    def seteventfontsize(self):
        size = self.eventfontsize_selector.value()
        if type(size) == type(1):
            self.config["eventfontsize"] = size
    ### event updater functions:
    def eventUpdater(self):
        progbar = 0
        self.update_events_progressbar.setTextVisible(True)
        self.update_events_progressbar.setValue(progbar)
        print ("I'm updataing myself by times.ir...")
        year = self.persian_date.split(' ')[-1]
        dic = {u'۰':'0', u'۱':'1', u'۲':'2', u'۳':'3', u'۴':'4', u'۵':'5', u'۶':'6', u'۷':'7', u'۸':'8', u'۹':'9'}
        day = u'۰۱۲۳۴۵۶۷۸۹'
        year = u''.join([dic.get(i) for i in year])
        print ("year = ", year)
        y = int(year)
        K = 30 if y % 4 == 1 else 29
        m = [31] * 6 + [30] * 5 + [K]
        month_dict = {1:u'فروردین',
                      2:u'اردیبهشت',
                      3:u'خرداد',
                      4:u'تیر',
                      5:u'مرداد',
                      6:u'شهریور',
                      7:u'مهر',
                      8:u'آبان',
                      9:u'آذر',
                      10:u'دی',
                      11:u'بهمن',
                      12:u'اسفند',
            }
        EV = open('events.json', 'w')
        HD = open('holidays.json', 'w')
        EV.writelines('{\n')
        HD.writelines('{\n')
        for i in range(1, 13):
            for j in range(1, m[i-1]+1):
                url = 'http://www.time.ir/fa/event/list/0/'+year+'/'+str(i)+'/'+ str(j)
                page = requests.get(url)
                holiday = 0 if page.content.find(b'eventHoliday') == -1 else 1
                tree = html.fromstring(page.content)
                tt = tree.xpath('//li/text()')
                if len(tt) == 0:
                    pass
                else:
                    a = [tt[k] for k in range(len(tt)) if k % 3 == 1]
                    b = [c.split('\r\n')[1] for c in a]
                for c in range(len(b)):
                    for k in range(len(b[c])):
                        if  b[c][k] != u' ' or b[c][k] != ' ':
                            break
                            print("I break it")
                    b[c] = b[c][k::]
                text = ''
                for t in b:
                    text = text + t + '-'
                    d = u''.join([day[int(l)] for l in str(j)])
                holitext = u' (تعطیل)' if holiday == 1 else u''
                line = u'"' + d + u' ' + month_dict[i]+u'": '+ u'"'+text+holitext+'",\n'
                if holiday == 1:
                    #L = u'"' + u' ' + month_dict[i]+u'": '+ u'"'+d+'",\n'
                    L = u'"'+ d + u' ' + month_dict[i]+u'": '+ u'"'+d+'",\n'
                    if sys.version[0] == '2':
                        L = L.encode('utf-8')
                    HD.writelines(L)
                    self.holidays[d + u' ' + month_dict[i]] = d
                               
                if sys.version[0] == '2':
                    line = line.encode('utf-8')
                EV.writelines(line)
                self.events[d + u' ' + month_dict[i]] = text+holitext
                print (text)
                progbar += 1
                self.update_events_progressbar.setValue(int(progbar*95/366))
                time.sleep(0.5)
        if j == K and i == 12: # means to get all year events
            EV.writelines('"پایان":"پایان"')
            self.events[u"پایان"] = u"پایان"
            EV.writelines("}")
            EV.close()
            HD.writelines('"پایان":"پایان"')
            self.holidays[u"پایان"] = u"پایان"
            HD.writelines("}")
            HD.close()
            self.update_events_progressbar.setValue(100)
            print("I saved events file")
            self.update_events_progressbar.setValue(0)
            self.update_events_progressbar.setTextVisible(False)
    ### second color functions:
    def picksecondscolor(self):
        color = QColorDialog.getColor()
        if color.name() != u'#000000':
            self.seconds_color = [color.red(), color.green(), color.blue()]
            self.config['seconds_color'] = self.seconds_color
            self.secondscolorpicker.setStyleSheet(u"QPushButton {background-color: "+color.name()+u';color:red;}')
    
    def picksecondcolor(self):
        color = QColorDialog.getColor()
        if color.name() != u'#000000':
            self.second_color = [color.red(), color.green(), color.blue()]
            self.config['second_color'] = self.second_color
            self.secondcolorpicker.setStyleSheet(u"QPushButton {background-color: "+color.name()+u';color:red;}')
    
    def __update_alpha__(self):
        va = self.alpha_slider.value()
        va = int(255.0 * (va+1) / 100)
        vr = self.red_slider.value()
        vr = int(255.0 * (vr+1) / 100)
        vb = self.blue_slider.value()
        vb = int(255.0 * (vb+1) / 100)
        vg = self.green_slider.value()
        vg = int(255.0 * (vg+1) / 100)
        I = Image.new(mode='RGBA', color=(0,0,0,0), size=(350, 350))
        draw = ImageDraw.Draw(I)
        draw.ellipse(xy=[(52, 52), (297, 297)], fill=(vr,vg,vb,va))
        self.face.putdata(I.getdata())
        self.config["face_color"] = (vr,vg,vb,va)
        
    def __update_alphab__(self):
        va = self.alpha_sliderb.value()
        va = int(255.0 * (va+1) / 100)
        vr = self.red_sliderb.value()
        vr = int(255.0 * (vr+1) / 100)
        vb = self.blue_sliderb.value()
        vb = int(255.0 * (vb+1) / 100)
        vg = self.green_sliderb.value()
        vg = int(255.0 * (vg+1) / 100)
        mp = self.facebmask.load()
        pixels = self.faceb.load()
        for x in range(self.faceb.width):
            for y in range(self.faceb.height):
                p = mp[x, y]
                if p != 0:
                    pixels[x,y] = (vr, vg, vb, int(va * p/255))
        self.config["faceb_color"] = (vr,vg,vb,va)
    
    def __open__(self, pd):
        self.persian_date = pd
    
    def closeEvent(self, event):
        self.hide()
        event.ignore()
        
# ##################################################################################################################################################Section IV

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = ui_widget()
    sys.exit(app.exec_())

