# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 10:33:00 2025
An application to use the IMBL EPICS based instruments to move, and expose objects
in the beam.
Primarily written for circuit boards carrying ICs for LID exposures.
See the documentation for use.

@author: imbl(CH)
"""

import sys
from PyQt5 import QtWidgets, uic
import seqConnect


app = QtWidgets.QApplication(sys.argv)

window = uic.loadUi("sequencer.ui")
seqConnect.initConnectGUI(window,app) # Make the GUI event-slot connections
window.show()
sys.exit(app.exec())

