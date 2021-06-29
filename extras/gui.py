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
        self.virtual_buttons = {}
        self.slew_speed = 'CSlew'


        # self.dome_drive_left.setAutoRepeat(True)
        self.dome_drive_left.pressed.connect(self.send_dome_left)
        self.dome_drive_left.released.connect(self.send_dome_stop)

        self.dome_drive_right.pressed.connect(self.send_dome_right)
        self.dome_drive_right.released.connect(self.send_dome_stop)

        self.dome_goto_position.clicked.connect(self.dome_goto_pos)
        self.focus_goto_position.clicked.connect(self.focus_goto_pos)
        self.dome_stop.clicked.connect(self.send_stop_dome_goto)
        self.focus_stop.clicked.connect(self.send_stop_focus_goto)
        
        self.telescope_north.pressed.connect(self.send_telescope_north)
        self.telescope_south.pressed.connect(self.send_telescope_south)
        self.telescope_east.pressed.connect(self.send_telescope_east)
        self.telescope_west.pressed.connect(self.send_telescope_west)

        self.focus_drive_left.pressed.connect(self.send_focus_in)
        self.focus_drive_left.released.connect(self.send_focus_stop)

        self.focus_drive_right.pressed.connect(self.send_focus_out)
        self.focus_drive_right.released.connect(self.send_focus_stop)

        self.goto_target.pressed.connect(self.jump_target)

        self.telescope_guide_speed.toggled.connect(self.set_slew_speed)
        self.telescope_set_speed.toggled.connect(self.set_slew_speed)
        self.telescope_slew_speed.toggled.connect(self.set_slew_speed)

        self.Dome_lights_on.pressed.connect(self.dome_lights_on)
        self.Dome_lights_off.pressed.connect(self.dome_lights_off)

        self.shutter_open_with_windshield.pressed.connect(self.send_shutter_open_with_windshield)
        self.shutter_open_without_windshield.pressed.connect(self.send_shutter_open_without_windshield)
        self.shutter_close.pressed.connect(self.send_shutter_close)
        self.shutter_stop.pressed.connect(self.send_shutter_stop)

        self.mirror_cover_open.pressed.connect(self.send_mirror_cover_open)
        self.mirror_cover_close.pressed.connect(self.send_mirror_cover_close)

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
        self.update_dome()
        self.update_focus()
        self.update_mirror_cover()
        self.update_lights()
        self.update_shutter()

        
        

        self.virtual_buttons = self.teljoy_status.proxy.get_virtual_buttons_status()
        if self.virtual_buttons["North"]:
            self.telescope_north.setStyleSheet("background-color: green")
        else:
            self.telescope_north.setStyleSheet("background-color: ")

        if self.virtual_buttons["South"]:
            self.telescope_south.setStyleSheet("background-color: green")
        else:
            self.telescope_south.setStyleSheet("background-color: ")

        if self.virtual_buttons["East"]:
            self.telescope_east.setStyleSheet("background-color: green")
        else:
            self.telescope_east.setStyleSheet("background-color: ")

        if self.virtual_buttons["West"]:
            self.telescope_west.setStyleSheet("background-color: green")
        else:
            self.telescope_west.setStyleSheet("background-color: ")


    def send_telescope_north(self):
        self.teljoy_status.proxy.set_virtual_buttons_speed(self.slew_speed)
        self.teljoy_status.proxy.press_virtual_north()
    
    def send_telescope_south(self):
        self.teljoy_status.proxy.set_virtual_buttons_speed(self.slew_speed)
        self.teljoy_status.proxy.press_virtual_south()


    def send_telescope_east(self):
        self.teljoy_status.proxy.set_virtual_buttons_speed(self.slew_speed)
        self.teljoy_status.proxy.press_virtual_east()

    def send_telescope_west(self):
        self.teljoy_status.proxy.set_virtual_buttons_speed(self.slew_speed)
        self.teljoy_status.proxy.press_virtual_west()



    def send_dome_right(self):
        self.teljoy_status.proxy.send_dome_manual_right()

    def send_dome_left(self):
        self.teljoy_status.proxy.send_dome_manual_left()
    
    def send_dome_stop(self):
        if not (self.focus_drive_right.isDown() or self.focus_drive_left.isDown()):
            self.teljoy_status.proxy.send_stop_dome_manual_move()

    def send_stop_dome_goto(self):
        self.teljoy_status.proxy.send_stop_dome_goto()

    def send_stop_focus_goto(self):
        self.teljoy_status.proxy.send_stop_focus_goto()


    def send_focus_in(self):
        self.teljoy_status.proxy.send_focus_manual_in()
    
    def send_focus_out(self):
        self.teljoy_status.proxy.send_focus_manual_out()
    
    def send_focus_stop(self):
        if not (self.focus_drive_right.isDown() or self.focus_drive_left.isDown()):
            self.teljoy_status.proxy.send_focus_manual_stop()
    
        

    
    def update_RA(self):
        hours = self.teljoy_status.current.RaC / 15 / 3600
        minutes = hours % 1 * 60
        seconds = minutes % 1 * 60
        self.ra_hours.setText("%02d" % hours)
        self.ra_minutes.setText("%02d" % minutes)
        self.ra_seconds.setText("%.2f" % seconds)

    def update_HA(self):
        hours = self.teljoy_status.current.RaC / 15 / 3600 - self.teljoy_status.current.Time.LST #self.teljoy_status.current.Ra / 15 / 3600
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
    
    def update_dome(self):
        self.current_dome_position.setText("%03d" % self.teljoy_status.dome.DomeAzi)
        self.dome_status.setText(self.teljoy_status.dome.dome_drive_status)

    def update_mirror_cover(self):
        self.mirror_cover_status.setText(self.teljoy_status.dome.mirror_cover_status)

    def update_lights(self):
        self.dome_lights_status.setText(self.teljoy_status.dome.dome_lights_status)

    def update_shutter(self):
        self.shutter_status.setText(self.teljoy_status.dome.shutter_status)

    def dome_goto_pos(self):
        pos = int(self.dome_manul_goto_position.text())
        self.teljoy_status.proxy.send_dome_goto_pos(pos)
        self.commanded_dome_position.setText("%3d" % pos)

    def focus_goto_pos(self):
        pos = int(self.focus_manul_goto_position.text())
        self.teljoy_status.proxy.send_focus_goto_pos(pos)
        self.commanded_focus_position.setText("%3d" % pos)

    def jump_target(self):
        target = self.telescope_goto_target_id.text()
        self.tj_text.append(tjclient.jump(target))


    def set_slew_speed(self):
        if self.telescope_guide_speed.isChecked():
            self.slew_speed = 'CGuide'
        
        if self.telescope_set_speed.isChecked():
            self.slew_speed = 'CSet'

        if self.telescope_slew_speed.isChecked():
            self.slew_speed = 'CSlew'

        self.teljoy_status.proxy.set_virtual_buttons_speed(self.slew_speed)
    
    def dome_lights_on(self):
        self.teljoy_status.proxy.send_dome_lights_on()

    def dome_lights_off(self):
        self.teljoy_status.proxy.send_dome_lights_off()

    def send_shutter_open_without_windshield(self):
        self.teljoy_status.proxy.send_shutter_open_without_windshield()

    def send_shutter_open_with_windshield(self):
        self.teljoy_status.proxy.send_shutter_open_with_windshield()

    def send_shutter_close(self):
        self.teljoy_status.proxy.send_shutter_close()

    def send_shutter_stop(self):
        self.teljoy_status.proxy.send_shutter_stop()

    def send_mirror_cover_open(self):
        self.teljoy_status.proxy.send_mirror_cover_open()
    
    def send_mirror_cover_close(self):
        self.teljoy_status.proxy.send_mirror_cover_close()





    def update_focus(self):
        self.current_focus_position.setText("%03d" % int(self.teljoy_status.dome.focus_absolute_position))
        if self.teljoy_status.dome.secondary_mirror == '1':
            self.secondary_mirror_status.setText("f13.5")
        elif self.teljoy_status.dome.secondary_mirror == '2':
            self.secondary_mirror_status.setText("f6.25")
        else:
            self.secondary_mirror_status.setText("Error: Check secondary mirror!")

        if self.teljoy_status.dome.focus_endstop_status == '0':
            self.focus_status.setText("OK")
        elif self.teljoy_status.dome.focus_endstop_status == '1':
            self.focus_status.setText("Lower limit")
        elif self.teljoy_status.dome.focus_endstop_status == '2':
            self.focus_status.setText("Upper limit")
        





        

app = QtWidgets.QApplication(sys.argv)
app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))

window = Ui()
app.exec_()