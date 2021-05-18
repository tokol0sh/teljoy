from __future__ import print_function
import serial
import time
import threading
import numpy


DOME_PORT = 'COM4'
DEBUG = False
PRINT = False

mirror_cover = ["mirror cover closed", "mirror cover opened", "mirror cover opening", "mirror cover closing", "mirror cover partly opened"]
dome_drive = ["Dome stopped", "Dome arrived at GoTo position", "DomeDoingGoTo", "DoingDomeManualDriveRight", "DoingDomeManualDriveLeft", "DomeParked", "DomeEncoderNotInitialised", "DomeGoToWasCancelled"]
shutter = ["Shutter fully closed", "Shutter fully open", "Shutter driving up without windshield", "Shutter driving up with windshield", "Shutter stopped part way up", "Shutter stopped part way down"]
dome_encoder = ["Dome encoder not initialised", " Dome encoder initialised"]
dome_lights = ["Dome lights on", "Dome lights off"]




class HandPaddle:
    def __init__(self):
        # open the com port
        try:
            self.ser = serial.Serial(DOME_PORT, baudrate=9600, stopbits=serial.STOPBITS_ONE, timeout=1.0, rtscts=False, xonxoff=False, dsrdtr=False)
        except:
            self.ser = None
            print("Error opening serial port, no dome communication")
        # setup timers
        self.command_buffer = []
        self.dome_azimuth = 0
        self.mirror_cover_status = 0
        self.dome_drive_status = 0
        self.secondary_mirror = 0
        self.focus_endspot_staus = 0
        self.focus_absolute_position = 0
        self.focus_relative_position = 0
        self.shutter_status = 0
        self.dome_encoder_status = 0
        self.dome_lights_status = 0
        self.now = 0
        self.last = 0
        self.parser = command_parser(self)

    def update(self):
        self.read_command()
        self.send_commands()

    def read_command(self):
        data = self.ser.read_until(expected=b'*').decode()
        commands = data.split('\r')
        commands.pop(-1) # get rid of the '*'
        for command in commands:
            if command != '':
                self.parser.process(command)
        print("\n\n")


    def send_commands(self):
        string = ""
        for command in self.command_buffer:
            string += command
            string += "\r"
        string += "*"

        if DEBUG == True:
            print(string)
        else:
            self.ser.write(string.encode())
            # if PRINT:
            #     print(string)
        self.command_buffer=[]

    def send_RA(self):
        self.command_buffer.append("A123456")

    def send_DEC(self):
        self.command_buffer.append("B+123456")

    def send_HA(self):
        self.command_buffer.append("C+123456")

    def send_LST(self):
        self.command_buffer.append("D123456")

    
    def send_dome_goto_pos(self, pos):
        self.command_buffer.append("E%03d" % pos)
        if PRINT:
            print("E%3d" % pos)
        # self.send_dome_enable_goto()

    def send_dome_enable_goto(self):
        self.command_buffer.append("F1")
    
    def send_stop_dome_goto(self):
        self.command_buffer.append("F0")
    
    def send_dome_auto(self):
        self.command_buffer.append("G1")

    def send_dome_manual(self):
        self.command_buffer.append("G0")
    
    def send_stop_dome_manual_move(self):
        self.command_buffer.append("H0")
        if PRINT:
            print("Stop manual")
    
    def send_dome_manual_left(self):
        self.command_buffer.append("H1")
        if PRINT:
            print("Left")
    
    def send_dome_manual_right(self):
        self.command_buffer.append("H2")
        if PRINT:
            print("Right")


class command_parser():
    def __init__(self,obj):
        self.handpaddle = obj
    def process(self, cmd):
        if PRINT:
            print("processing", cmd)
        fn = 'function_' + cmd[0]

        if hasattr(self, fn):
            getattr(self, fn)(cmd[1:])
        else:
            print("invalid command: ", cmd)
    
    def function_a(self, arg):
        print('North not implemented:', arg)

    def function_b(self, arg):
        print('South not implemented:', arg)

    def function_c(self, arg):
        print('East not implemented:', arg)
    
    def function_d(self, arg):
        print('West not implemented:', arg)

    def function_e(self, arg):
        print('no drive not implemented:', arg)

    def function_f(self, arg):
        self.handpaddle.mirror_cover_status = arg
        if PRINT:
            print("Mirror cover status received:", mirror_cover[self.handpaddle.mirror_cover_status])

    def function_g(self, arg):
        self.handpaddle.dome_drive_status = int(arg)
        if PRINT:
            print("Dome drive status: ", dome_drive[self.handpaddle.dome_drive_status])
        

    def function_h(self, arg):
        self.handpaddle.dome_azimuth = int(arg)
        if PRINT:
            print("Dome azimuth: %03d" % self.handpaddle.dome_azimuth)

    def function_i(self, arg):
        try:
            focus_data = arg.split(',')
            self.handpaddle.secondary_mirror = focus_data[0]
            self.handpaddle.focus_endspot_staus = focus_data[1]
            self.handpaddle.focus_absolute_position = focus_data[2]
            self.handpaddle.focus_relative_position = focus_data[3]
        except:
            print("error parsing focus command")

    def function_j(self, arg):
        try:
            self.handpaddle.shutter_status = int(arg)
        except:
            print("error parsing j command")

        if PRINT:
            print("Shutter status: ", shutter[self.handpaddle.shutter_status])

    def function_k(self, arg):
        self.handpaddle.dome_encoder_status = int(arg)
        if PRINT:
            print("Dome encoder status: ", dome_encoder[self.handpaddle.dome_encoder_status])

    def function_l(self, arg):
        self.handpaddle.dome_lights_status = int(arg)
        if PRINT:
            print("Dome lights status : ", dome_lights[self.handpaddle.dome_lights_status])




if __name__ == "__main__":
    # if this file is run, make it do something useful for testing
    
    hand_paddle = HandPaddle()
    while(1):
        hand_paddle.send_RA()
        hand_paddle.send_DEC()
        hand_paddle.send_HA()

        hand_paddle.send_commands()
        hand_paddle.read_command()
        time.sleep(0.2)

    

    