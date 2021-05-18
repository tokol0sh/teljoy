import sys
import os
import qdarkstyle
from PyQt5 import QtWidgets, QtCore, QtGui, uic
from PyQt5.QtCore import QTimer
import sys
import tjclient
# import dome_parser
import datetime

version = sys.version_info
try:
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True) #enable highdpi scaling
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True) #use highdpi icons
except:
    print("Scaling not available in with the py2.7 pyqt5 implementation")

DEBUG = True

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('./extras/teljoy_gui.ui', self)


        errmsg = tjclient.Init() 
        self.teljoy_status = tjclient.status
        self.teljoy_status_timer = QTimer()
        self.teljoy_status_timer.timeout.connect(self.update_status)
        self.teljoy_status_timer.start(300)


        # self.dome_drive_left.setAutoRepeat(True)
        self.dome_drive_left.pressed.connect(self.send_dome_left)
        self.dome_drive_left.released.connect(self.send_dome_stop)

        self.dome_drive_right.pressed.connect(self.send_dome_right)
        self.dome_drive_right.released.connect(self.send_dome_stop)

        self.dome_goto_position.clicked.connect(self.dome_goto_pos)
        # self.dome_stop.clicked.connect(self.handpaddle.send_stop_dome_goto)
        
        self.telescope_north.pressed.connect(self.send_telescope_north)
        self.telescope_south.pressed.connect(self.send_telescope_south)
        self.telescope_east.pressed.connect(self.send_telescope_east)
        self.telescope_west.pressed.connect(self.send_telescope_west)

        self.goto_target.pressed.connect(self.jump_target)
        self.show()

    def update_status(self):
        self.teljoy_status.update()
        self.update_RA()
        self.update_DEC()
        self.update_HA()
        self.update_time()
        self.update_AZ()
        self.update_EL()
        self.update_time()
        self.update_dome_azimuth()

    def send_telescope_north(self):
        self.teljoy_status.proxy.press_virtual_north()
    
    def send_telescope_south(self):
        self.teljoy_status.proxy.press_virtual_south()

    def send_telescope_east(self):
        self.teljoy_status.proxy.press_virtual_east()

    def send_telescope_west(self):
        self.teljoy_status.proxy.press_virtual_west()



    def send_dome_right(self):
        self.teljoy_status.proxy.send_dome_manual_right()

    def send_dome_left(self):
        self.teljoy_status.proxy.send_dome_manual_left()
    
    def send_dome_stop(self):
        if not (self.dome_drive_right.isDown() or self.dome_drive_left.isDown()):
            self.teljoy_status.proxy.send_stop_dome_manual_move()


    
    def update_RA(self):
        hours = self.teljoy_status.current.RaC / 15 / 3600
        minutes = hours % 1 * 60
        seconds = minutes % 1 * 60
        self.ra_hours.setText("%02d" % hours)
        self.ra_minutes.setText("%02d" % minutes)
        self.ra_seconds.setText("%.2f" % seconds)

    def update_HA(self):
        hours = self.teljoy_status.current.Ra / 15 / 3600
        minutes = hours % 1 * 60
        seconds = minutes % 1 * 60
        self.ha_hours.setText("%02d" % hours)
        self.ha_minutes.setText("%02d" % minutes)
        self.ha_seconds.setText("%.2f" % seconds)

    def update_DEC(self):
        degrees = self.teljoy_status.current.DecC / 3600
        minutes = degrees % 1 * 60
        seconds = minutes % 1 * 60
        self.dec_degrees.setText("%02d" % degrees)
        self.dec_minutes.setText("%02d" % minutes)
        self.dec_seconds.setText("%.2f" % seconds)

    def update_AZ(self):
        degrees = self.teljoy_status.current.Azi
        # print(degrees)
        minutes = degrees % 1 * 60
        seconds = minutes % 1 * 60
        self.az_degrees.setText("%02d" % degrees)
        self.az_minutes.setText("%02d" % minutes)
        self.az_seconds.setText("%.2f" % seconds)

    def update_EL(self):
        degrees = self.teljoy_status.current.Alt
        minutes = degrees % 1 * 60
        seconds = minutes % 1 * 60
        self.el_degrees.setText("%02d" % degrees)
        self.el_minutes.setText("%02d" % minutes)
        self.el_seconds.setText("%.2f" % seconds)
    

    def update_time(self):
        LST_hours = self.teljoy_status.current.Time.LST
        LST_minutes = LST_hours % 1 * 60
        LST_seconds = LST_minutes % 1 * 60

        UT = datetime.datetime.strptime(self.teljoy_status.current.Time.UT, '%Y-%m-%dT%H:%M:%S.%f')
        self.UTC.setText("%02d:%02d:%02d" % (UT.hour, UT.minute, UT.second))
        self.LST.setText("%02d:%02d:%.2f" % (LST_hours, LST_minutes, LST_seconds))
    
    def update_dome_azimuth(self):
        self.current_dome_position.setText("%03d" % self.teljoy_status.dome.DomeAzi)

    def dome_goto_pos(self):
        pos = int(self.dome_manul_goto_position.text())
        self.teljoy_status.proxy.send_dome_goto_pos(pos)
        self.commanded_dome_position.setText("%3d" % pos)

    def jump_target(self):
        target = self.telescope_goto_target_id.text()
        tjclient.jump(target)


        

app = QtWidgets.QApplication(sys.argv)
app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))

window = Ui()
app.exec_()