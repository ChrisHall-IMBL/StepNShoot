# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 17:14:22 2025

@author: imbl
"""

import epics
import time

def onChanges(pvname=None, value=None, char_value=None, **kw):
    print('PV Changed! ', pvname, char_value, time.ctime())
    print('Value: ', value)

# mypv = epics.get_pv('SR08ID01ZORRO:LARGE_Y', callback=onChanges)
epics.camonitor('SR08ID01ZORRO:LARGE_Y', callback=onChanges)

print('Now wait for changes')
expire_time = time.time() + 60.
try:
    while time.time() < expire_time:
        time.sleep(0.01)
    epics.camonitor_clear('SR08ID01ZORRO:LARGE_Y')
    print('Done.')
except:
    epics.camonitor_clear('SR08ID01ZORRO:LARGE_Y')
    print('Halted')