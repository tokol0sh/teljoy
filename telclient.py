#!/usr/bin/python

"""Client to display the state of the high-level telescope control 
   software. Reads the pickled data in the teljoy.status file, and uses 
   that to display the current telescope coordinates, motion state and
   other info every second, as long as Teljoy is running.
"""

import cPickle
import time

from globals import *
import motion
import detevent


if __name__ == '__main__':
  LastLST = 0
  displayed = False
  while True:
    time.sleep(1)
    f = open('/tmp/teljoy.status','r')
    try:
      Current, motors, dstatus, errors, prefs = cPickle.load(f)
    except EOFError:
      print '.'
      f.close()
      continue
    f.close()
    if Current.Time.LST == LastLST:
      if not displayed:
        displayed = True
        print "<no data>"
    else:
      flags = []
      if prefs.EastOfPier:
        flags.append('EoP')
      if prefs.NonSidOn:
        flags.append('NonSid')
      if motors.Frozen:
        flags.append('Frozen')
      if motors.moving:
        flags.append('Moving')
      if (dstatus.DomeInUse or dstatus.ShutterInUse):
        flags.append('Dome Active')
      if dstatus.DomeTracking:
        flags.append('DomeTr')
      print "%s [%s] %s" % (Current, ','.join(flags), errors)
      LastLST = Current.Time.LST
      displayed = False
  
