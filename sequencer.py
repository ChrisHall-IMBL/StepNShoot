# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 10:33:00 2025

@author: imbl
"""

import sys
from PyQt5 import QtWidgets, uic
import seqConnect


app = QtWidgets.QApplication(sys.argv)

window = uic.loadUi("sequencer.ui")
seqConnect.initConnectGUI(window,app) # Make the GUI event-slot connections
window.show()
sys.exit(app.exec())

