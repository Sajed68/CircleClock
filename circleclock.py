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
# Start: 13 Mehr 1396
# First Release 13 Mehr 1396
# Url : https://gitlab.com/sajed68/circle-clock-widget
# #####################################################


# the libraries for ui menu:
from PyQt5.QtWidgets import QApplication, QWidget, QToolTip, QPushButton, QMessageBox, QMainWindow, QMenu, qApp
from PyQt5.QtGui import QFont, QPainter, QColor, QPolygonF, QImage, QTransform
from PyQt5.QtCore import QCoreApplication
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QPointF
import math
from PIL import Image, ImageQt
import sys
from PyQt5.QtCore import QDateTime, QDate, QTimer # because I want get away from time for calculation the time!
sys.path.append('./utils')
import jdatetime  # use side library to convert date
import json


class ui_widget(QMainWindow):
    def __init__(self):
        super(ui_widget, self).__init__()
        self.setWindowTitle('Calendar')
        # following line is a setting to remove icon at taskbar, BUT IT MUST BE QMainWindow:
        self.setWindowFlags(QtCore.Qt.Tool| QtCore.Qt.FramelessWindowHint) # To remove Title bar
        QToolTip.setFont(QFont('Koodak', 10))
        self.__read_config__()
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
        self.qp.setFont(QFont('XP Vosta', 20)) # XP Vosta #
        self.qp.drawText(175 - 75, 180, 150, 75, Qt.AlignCenter, self.persian_date)
        
        self.qp.setPen(QColor(255, 255, 255))
        self.qp.setBrush(QColor(255, 255, 255))
        self.qp.setFont(QFont('Koodak', 34)) #
        self.qp.drawText(175 - 85, 130, 171, 35, Qt.AlignCenter, self.persian_time)

                
        
        
    
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
            if i != ps:
                self.qp.setBrush(Qt.white)
                c, v = self.__rotate_the_points(a, 1, -110)
                self.qp.drawEllipse(x1 - c - 3, y1 - v - 3, 6, 6)
            #if i == ps:
                #self.qp.setBrush(Qt.red)
                #self.qp.drawEllipse(x1 - c - 3, y1 - v - 3, 6, 6)
        
    def __rotate_the_points(self, a, x, y):
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
                    3:u'چهار شنبه',
                    4:u'پنج شنبه',
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
            with open('./utils/events.json', 'r') as events:
                self.events = json.load(events)
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
        except:
            self.config = {{"x":1900-400}, {"y":1000-400}, {"open":"default"}}
            self.x = self.config['x']
            self.y = self.config['y']
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
           action = cmenu.exec_(self.mapToGlobal(event.pos()))
           
           if action == quitAct:
               self.close()
        
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = ui_widget()
    sys.exit(app.exec_())

