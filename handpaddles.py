"""Handles reading and responding to hand paddle direction switches and speed buttons.
"""

from globals import *
import motion
import digio
from threading import Timer


class Paddles(object):
    """An instance of this class is used to store the state of the hand paddle
       buttons, current motion, and speed settings.

       Note that for the Perth telescope:
         -The Fine paddle speed can be one of 'Guide' or 'Set'
         -The Coarse paddle speed can be one of 'Set' or 'Slew'
       For the NZ telescope:
         -There is no fine paddle
         -The Coarse paddle speed can be one of 'Guide', 'Set', or 'Slew'
    """

    def __init__(self):
        self.RA_GuideAcc = 0.0  # Accumulated guide motion, from motion.motors.RA_guidelog
        self.DEC_GuideAcc = 0.0
        self.ButtonPressedRA = False  # True if one of the RA direction buttons is pressed
        self.ButtonPressedDEC = False  # True if one of the DEC direction buttons is pressed
        self.FineMode = 'FSet'  # one of 'FSet' or 'FGuide', depending on 'Fine' paddle speed toggle switch
        self.CoarseMode = 'CSet'  # one of 'CSet' or 'CSlew' or 'CGuide', depending on 'Coarse' paddle speed toggle switch
        self.RAdir = ''  # one of 'fineEast',  'fineWest',  'CoarseEast', or  'CoarseWest'
        self.DECdir = ''  # one of 'fineNorth', 'fineSouth', 'CoarseNorth', or 'CoarseSouth'

    def __repr__(self):
        s = "<PaddleStatus: GuideAcc=(%f,%f) " % (self.RA_GuideAcc, self.DEC_GuideAcc)
        if self.ButtonPressedRA:
            s += "(RA:%s) " % self.RAdir
        if self.ButtonPressedDEC:
            s += "(DEC:%s) " % self.DECdir
        s += " >"
        return s

    def check(self):
        """Read the actual handle paddle button and switch state, using the digio module, and
           handle them appropriately. When the state of the direction buttons changes (press or
           release), set the appropriate motion control flags and velocity parameters, then
           start or stop the actual motors.

           This method is called at regular intervals by the DetermineEvent loop.
        """
        # Read the Hand-paddle input
        cb = digio.ReadCoarse()
        fb = digio.ReadFine()

        # check the Fine paddle speed switches and set appropriate mode and velocity
        if (fb & digio.FGuideMsk) == digio.FGuideMsk:
            self.FineMode = 'FGuide'
            FinePaddleRate = prefs.GuideRate
        else:
            self.FineMode = 'FSet'
            FinePaddleRate = prefs.FineSetRate

        # Check the fine paddle by comparing fb to a set of mask
        if (fb & digio.FNorth) == digio.FNorth:  # Compare with the north mask
            if not self.ButtonPressedDEC:  # The button has just been pressed
                self.ButtonPressedDEC = True
                self.DECdir = 'fineNorth'
                Paddle_max_vel = FinePaddleRate
                motion.motors.DEC.StartPaddle(Paddle_max_vel)
        elif self.ButtonPressedDEC and (self.DECdir == 'fineNorth'):
            # Mask does not match but the motor is running
            self.ButtonPressedDEC = False
            motion.motors.DEC.StopPaddle()

        if (fb & digio.FSouth) == digio.FSouth:  # Check with South Mask
            if not self.ButtonPressedDEC:
                self.ButtonPressedDEC = True
                self.DECdir = 'fineSouth'
                Paddle_max_vel = -FinePaddleRate
                motion.motors.DEC.StartPaddle(Paddle_max_vel)
        elif self.ButtonPressedDEC and (self.DECdir == 'fineSouth'):
            # Mask does not match but the motor is runnin
            self.ButtonPressedDEC = False
            motion.motors.DEC.StopPaddle()

        if (fb & digio.FEast) == digio.FEast:  # Check the Eastmask
            if (not self.ButtonPressedRA) and motion.limits.CanEast():
                self.ButtonPressedRA = True
                self.RAdir = 'fineEast'
                Paddle_max_vel = FinePaddleRate
                motion.motors.RA.StartPaddle(Paddle_max_vel)
        elif self.ButtonPressedRA and (self.RAdir == 'fineEast'):
            # Mask does not match but the motor is running}
            self.ButtonPressedRA = False
            motion.motors.RA.StopPaddle()

        if (fb & digio.FWest) == digio.FWest:  # Check the West mask
            if (not self.ButtonPressedRA) and motion.limits.CanWest():
                self.ButtonPressedRA = True
                self.RAdir = 'fineWest'
                Paddle_max_vel = -FinePaddleRate
                motion.motors.RA.StartPaddle(Paddle_max_vel)
        elif self.ButtonPressedRA and (self.RAdir == 'fineWest'):
            # Mask does not match but the motor is running
            self.ButtonPressedRA = False
            motion.motors.RA.StopPaddle()

        # check the Coarse paddle speed switches and set appropriate mode and velocity
        if SITE == 'NZ':
            if ((cb & digio.CspaMsk) == digio.CspaMsk) and ((cb & digio.CspbMsk) == digio.CspbMsk):
                self.CoarseMode = 'CSet'
                CoarsePaddleRate = prefs.CoarseSetRate
            else:
                if ((cb & digio.CspbMsk) == digio.CspbMsk):
                    self.CoarseMode = 'CGuide'
                    CoarsePaddleRate = prefs.GuideRate
                else:
                    self.CoarseMode = 'CSlew'
                    CoarsePaddleRate = prefs.SlewRate
        else:
            if (cb & digio.CSlewMsk) == digio.CSlewMsk:
                self.CoarseMode = 'CSlew'
                CoarsePaddleRate = prefs.SlewRate
            else:
                self.CoarseMode = 'CSet'
                CoarsePaddleRate = prefs.CoarseSetRate

        # **Check the Coarse paddle by comparing cb to a set of mask
        if (cb & digio.CNorth) == digio.CNorth:
            if not self.ButtonPressedDEC:
                self.ButtonPressedDEC = True
                self.DECdir = 'coarseNorth'
                Paddle_max_vel = CoarsePaddleRate
                motion.motors.DEC.StartPaddle(Paddle_max_vel)
        elif self.ButtonPressedDEC and (self.DECdir == 'coarseNorth'):
            # Mask does not match but the motor is running
            self.ButtonPressedDEC = False
            motion.motors.DEC.StopPaddle()

        if (cb & digio.CSouth) == digio.CSouth:
            if not self.ButtonPressedDEC:
                self.ButtonPressedDEC = True
                self.DECdir = 'coarseSouth'
                Paddle_max_vel = -CoarsePaddleRate
                motion.motors.DEC.StartPaddle(Paddle_max_vel)
        elif self.ButtonPressedDEC and (self.DECdir == 'coarseSouth'):
            # Mask does not match but the motor is running
            self.ButtonPressedDEC = False
            motion.motors.DEC.StopPaddle()

        if (cb & digio.CEast) == digio.CEast:
            if (not self.ButtonPressedRA) and motion.limits.CanEast():
                self.ButtonPressedRA = True
                self.RAdir = 'coarseEast'
                Paddle_max_vel = CoarsePaddleRate
                motion.motors.RA.StartPaddle(Paddle_max_vel)
        elif self.ButtonPressedRA and (self.RAdir == 'coarseEast'):
            # Mask does not match but the motor is running
            self.ButtonPressedRA = False
            motion.motors.RA.StopPaddle()

        if (cb & digio.CWest) == digio.CWest:
            if (not self.ButtonPressedRA) and motion.limits.CanWest():
                self.ButtonPressedRA = True
                self.RAdir = 'coarseWest'
                Paddle_max_vel = -CoarsePaddleRate
                motion.motors.RA.StartPaddle(Paddle_max_vel)
        elif self.ButtonPressedRA and (self.RAdir == 'coarseWest'):
            # Mask does not match but the motor is running
            self.ButtonPressedRA = False
            motion.motors.RA.StopPaddle()



class VirtualPaddles(object):
    """An instance of this class is used to store the state of the hand paddle
        buttons, current motion, and speed settings.

        Note that for the Perth telescope:
        -The Fine paddle speed can be one of 'Guide' or 'Set'
        -The Coarse paddle speed can be one of 'Set' or 'Slew'
        For the NZ telescope:
        -There is no fine paddle
        -The Coarse paddle speed can be one of 'Guide', 'Set', or 'Slew'
    """
    def __init__(self):
        self.RA_GuideAcc = 0.0         # Accumulated guide motion, from motion.motors.RA_guidelog
        self.DEC_GuideAcc = 0.0
        self.ButtonPressedRA = False   # True if one of the RA direction buttons is pressed
        self.ButtonPressedDEC = False  # True if one of the DEC direction buttons is pressed
        self.CoarseMode = 'CSlew'       # one of 'CSet' or 'CSlew' or 'CGuide', depending on 'Coarse' paddle speed toggle switch
        self.RAdir = ''                # one of 'fineEast',  'fineWest',  'CoarseEast', or  'CoarseWest'
        self.DECdir = ''               # one of 'fineNorth', 'fineSouth', 'CoarseNorth', or 'CoarseSouth'
        self.VirtualButtons = {"North":False, "South":False, "East":False, "West":False}
        self.VirtualButtonsTimer = 0
        self.previous_time = 0
        self.current_time = 0

    def __repr__(self):
        s = "<PaddleStatus: GuideAcc=(%f,%f) " % (self.RA_GuideAcc, self.DEC_GuideAcc)
        if self.ButtonPressedRA:
            s += "(RA:%s) " % self.RAdir
        if self.ButtonPressedDEC:
            s += "(DEC:%s) " % self.DECdir
        s += " >"
        return s

    def check(self):
        """Read the actual handle paddle button and switch state, using the digio module, and
        handle them appropriately. When the state of the direction buttons changes (press or
        release), set the appropriate motion control flags and velocity parameters, then
        start or stop the actual motors.

        This method is called at regular intervals by the DetermineEvent loop.
        """
        ## TODO: add timeout to the button presses 
        # check the Coarse paddle speed switches and set appropriate mode and velocity
        self.current_time = time.time()

        if self.current_time - self.previous_time > 1.0:
            # a button timeout has occured
            # set all buttons to false
            self.VirtualButtons = {"North":False, "South":False, "East":False, "West":False}
            self.previous_time = self.current_time
        

        # if ((cb & digio.CspaMsk) == digio.CspaMsk) and ((cb & digio.CspbMsk) == digio.CspbMsk):
        #   self.CoarseMode = 'CSet'
        #   CoarsePaddleRate = prefs.CoarseSetRate
        # else:
        #   if ((cb & digio.CspbMsk) == digio.CspbMsk):
        #     self.CoarseMode = 'CGuide'
        #     CoarsePaddleRate = prefs.GuideRate
        #   else:
        #     self.CoarseMode = 'CSlew'
        #     CoarsePaddleRate = prefs.SlewRate
        if self.CoarseMode == 'CSlew':
            CoarsePaddleRate = prefs.SlewRate
        elif self.CoarseMode == 'CGuide':
            CoarsePaddleRate = prefs.GuideRate
        elif self.CoarseMode == 'CSet':
            CoarsePaddleRate = prefs.CoarseSetRate
        



        # **Check the Coarse paddle by comparing cb to a set of mask
        if self.VirtualButtons["North"]:
            # self.previous_time = self.current_time
            if not self.ButtonPressedDEC:
                self.ButtonPressedDEC = True
                self.DECdir = 'coarseNorth'
                Paddle_max_vel = CoarsePaddleRate
                motion.motors.DEC.StartPaddle(Paddle_max_vel)
                print("Virtual North pressed")
                
        elif self.ButtonPressedDEC and (self.DECdir == 'coarseNorth'):
            #Mask does not match but the motor is running
            self.ButtonPressedDEC = False
            motion.motors.DEC.StopPaddle()
            print("Virtual North stopped")

        if self.VirtualButtons["South"]:
            # self.previous_time = self.current_time
            if not self.ButtonPressedDEC:
                self.ButtonPressedDEC = True
                self.DECdir = 'coarseSouth'
                Paddle_max_vel = -CoarsePaddleRate
                motion.motors.DEC.StartPaddle(Paddle_max_vel)
                print("Virtual South pressed")
        elif self.ButtonPressedDEC and (self.DECdir == 'coarseSouth'):
            # Mask does not match but the motor is running
            self.ButtonPressedDEC = False
            motion.motors.DEC.StopPaddle()
            print("Virtual South stopped")

        if self.VirtualButtons["East"]:
            # self.previous_time = self.current_time
            if (not self.ButtonPressedRA) : #and motion.limits.CanWest()
                self.ButtonPressedRA = True
                self.RAdir = 'coarseEast'
                Paddle_max_vel = CoarsePaddleRate
                motion.motors.RA.StartPaddle(Paddle_max_vel)
                print("Virtual East pressed")
        elif self.ButtonPressedRA and (self.RAdir == 'coarseEast'):
            # Mask does not match but the motor is running
            self.ButtonPressedRA = False
            motion.motors.RA.StopPaddle()
            print("Virtual East stopped")

        if self.VirtualButtons["West"]:
            # self.previous_time = self.current_time
            if (not self.ButtonPressedRA) : #and motion.limits.CanWest()
                self.ButtonPressedRA = True
                self.RAdir = 'coarseWest'
                Paddle_max_vel = -CoarsePaddleRate
                motion.motors.RA.StartPaddle(Paddle_max_vel)
                print("Virtual West pressed")
        elif self.ButtonPressedRA and (self.RAdir == 'coarseWest'):
            # Mask does not match but the motor is running
            self.ButtonPressedRA = False
            motion.motors.RA.StopPaddle()
            print("Virtual West stopped")


paddles = Paddles()
vpaddles = VirtualPaddles()