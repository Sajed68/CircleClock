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
# Email : SajedRakhshani@msn.com
# Start: 13 Mehr 1396
# First Release 13 Mehr 1396
# 3th Release 24 Aban
# #####################################################


# the libraries for ui menu:
from PyQt5.QtWidgets import QApplication, QWidget, QToolTip, QPushButton, QMessageBox, QMainWindow, QMenu, qApp, QTableWidget,QTableWidgetItem,QVBoxLayout, QLabel, QGridLayout
from PyQt5.QtGui import QFont, QPainter, QColor, QPolygonF, QImage, QTransform, QPen
from PyQt5.QtCore import QCoreApplication
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QPointF
import math
from PIL import Image, ImageQt
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
        self.setWindowTitle('Calendar')
        # following line is a setting to remove icon at taskbar, BUT IT MUST BE QMainWindow:
        self.setWindowFlags(QtCore.Qt.Tool| QtCore.Qt.FramelessWindowHint) # To remove Title bar
        self.__read_config__()
        QToolTip.setFont(QFont(self.eventfont, self.eventfontsize))
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setGeometry(self.x, self.y, 400, 400)
        self.setMinimumWidth(350)
        self.setMinimumHeight(400)
        self.setMaximumWidth(400)
        self.setMaximumHeight(400)
        self.faceb = Image.open('./arts/clockface_2.png')
        self.face = Image.open('./arts/clockface.png')
        self.angle = 0
        self.clockface = ImageQt.ImageQt(self.face).scaled(350,350)
        self.clockface2 = ImageQt.ImageQt(self.faceb).scaled(350,350)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(500)
        self.clockwork = ':'
        self.cal = cal(self.events, self.holidays)
        self.cal.hide()
        self.__update__()

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
        self.qp.setPen(QColor(255, 255, 255))
        self.qp.setBrush(QColor(255, 255, 255))
        self.qp.setFont(QFont(self.datefont, self.datefontsize)) # XP Vosta #
        self.qp.drawText(175 - 75, 180, 150, 75, Qt.AlignCenter, self.persian_date)
        
        self.qp.setPen(QColor(255, 255, 255))
        self.qp.setBrush(QColor(255, 255, 255))
        self.qp.setFont(QFont(self.clockfont, self.clockfontsize)) #
        self.qp.drawText(175 - 85, 130, 171, 35, Qt.AlignCenter, self.persian_time)
        
        self.qp.drawRect(100, 175, 150, 1)
        pen = QPen()
        pen.setWidth(10)
        #pen.setColor( QColor(255,255,255))
        #self.qp.setPen(pen)
        #self.qp.setPen(pen)
        #self.qp.setBrush(Qt.white)
        #self.qp.drawArc(5, 0.0, 350.0, 350.0, -0*16, -180*16)

                
        
        
    
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
                self.qp.setBrush(Qt.white)
                self.qp.setPen(Qt.white)
                c, v = self.__rotate_the_points__(a, 1, -110)
                self.qp.drawEllipse(x1 - c - 3, y1 - v - 3, 6, 6)
            if i == ps:
                col = QColor(178,34,34)
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
        self.event_text = self.events.get(event, None) 
        self.event_text = self.event_text if self.event_text is not None else 'امروز اتفاق خاصی نیفتاده!\nافتاده؟ پس اضافه کن!(متاسفانه فعلا امکانش نیست)'
        self.setToolTip(self.event_text)
        
    def animate(self):
        self.clockwork = u':' if self.clockwork == u'.' else u'.'
        self.angle += 6
        self.angle = self.angle % 360
        self.clockface2 = ImageQt.ImageQt(self.faceb.rotate(self.angle)).scaled(350,350)
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
                print('config file loaded')
        except:
            self.config = {"y": 560, "x": 1520, "open": "last", "clockfont": "Koodak", "datefont":"XP Vosta", "clockfontsize":34, "datefontsize":20, "eventfont":"Koodak", "eventfontsize":15}
            self.x = self.config['x']
            self.y = self.config['y']
            self.clockfont = self.config['clockfont']
            self.clockfontsize = self.config['clockfontsize']
            self.datefont = self.config['datefont']
            self.datefontsize = self.config['datefontsize']
            self.eventfont = self.config['eventfont']
            self.eventfontsize = self.config['eventfontsize']
            print("config can't loaded")
        try:
            with open('config.json', 'w') as outfile:
                json.dump(self.config, outfile)
        except:
                pass
    
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
           updateevent = cmenu.addAction("رویدادها رو بروز کنم؟ (اینترنت میخواهم!)")
           action = cmenu.exec_(self.mapToGlobal(event.pos()))

           
           if action == quitAct:
               self.close()
           if action == event_cal:
               self.__cal_show__()
           if action == updateevent:
               print ("I'm updataing myself by times.ir...")
               year = self.persian_date.split(' ')[-1]
               dic = {u'۰':'0', u'۱':'1', u'۲':'2', u'۳':'3', u'۴':'4', u'۵':'5', u'۶':'6', u'۷':'7', u'۸':'8', u'۹':'9'}
               day = u'۰۱۲۳۴۵۶۷۸۹'
               year = u''.join([dic.get(i) for i in year])
               print ("year = ", year)
               m = [31] * 6 + [30] * 5 + [29]
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
                               
                           if sys.version[0] == '2':
                               line = line.encode('utf-8')
                           EV.writelines(line)
                           print (text)
                       time.sleep(0.5)
                
               EV.writelines('"پایان":"پایان"')
               EV.writelines("}")
               EV.close()
               HD.writelines('"پایان":"پایان"')
               HD.writelines("}")
               HD.close()

 
class cal(QWidget):
    def __init__(self, ev, hd):
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
        self.setWindowTitle('Calendar_veiw')
        self.setGeometry(500, 500, 400, 400)
        self.setMinimumWidth(725)
        self.setMinimumHeight(400)
        self.setMaximumWidth(725)
        #self.setMaximumHeight(400)
        self.events = ev
        self.holidays = hd
        self.tableWidget = QTableWidget() # Calendar table view
        self.next_monthB = QPushButton(u'ماه بعد')  # Next month button
        self.prev_monthB = QPushButton(u'ماه قبل')  # prev month button
        self.next_monthB.clicked.connect(self.go_next_month)
        self.prev_monthB.clicked.connect(self.go_prev_month)
        self.label = QLabel("text") # event showr!
        
        self.createTable(1,1,1,1)
        self.text = ' '
        self.month_idx = 1
        self.month_name = self.month_dict[self.month_idx]
        self.month_label = QLabel(self.month_name) # month showr!
        self.layout = QGridLayout()
        self.layout.addWidget(self.month_label, 0, 0, 1, 2) 
        self.layout.addWidget(self.tableWidget, 1, 0, 1, 2) 
        self.layout.addWidget(self.next_monthB, 2, 0, 1, 1) 
        self.layout.addWidget(self.prev_monthB, 2, 1, 1, 1) 
        self.layout.addWidget(self.label, 3, 0, 1, 2)         
        self.setLayout(self.layout) 
        
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
        days = [u"شنبه", u"یکشنبه",u"دوشنبه", u"سه شنبه", u"چهارشنبه", u"پنجشنبه", u"جمعه"]
        for i in range(7):
            self.tableWidget.setItem(0,i, QTableWidgetItem(days[i]))
    
        day_num = 31 if month <= 6 else 30
        if month == 12:
            day_num = 30 if year % 4 == 1 else 29
        for i in range(day_num):
            j = i + firstday_idx
            x = j / 7
            y = j % 7
            item, num_text = self.create_per_num(i+1)
            #print(num_text + u' ' + self.month_dict[month])
            if self.holidays.get(num_text + u' ' + self.month_dict[month], None) is not None:
                item.setBackground(QColor(250,100,100))
            self.tableWidget.setItem(x+1,y, item)
            if j-1 == day:
                self.tableWidget.setCurrentCell(x+1,y)
            if y%7 == 6:
                self.tableWidget.item(x+1, y).setBackground(QColor(250,100,100))
        self.tableWidget.move(0,0)
        self.tableWidget.cellClicked.connect(self.on_click)
        
        
    def on_click(self):
        try:
            day = self.tableWidget.currentItem().text()
            day_month = day + ' ' + self.month_dict[self.month_idx]
        except:
            day_month = '___'
        self.text = self.events.get(day_month, ' ')
        self.show_text()
        
        
    def show_text(self):
        self.label.setText(self.text)
        
    def show_month(self):
        self.month_name = self.month_dict[self.month_idx]
        self.month_label.setText(self.month_name)
        
    
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
 


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = ui_widget()
    sys.exit(app.exec_())

