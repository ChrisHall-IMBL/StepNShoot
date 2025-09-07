# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 10:33:00 2025
An application to use the IMBL EPICS based instruments to move, and expose objects
in the beam.
Primarily written for circuit boards carrying ICs for LID exposures.
See the documentation for use.

@author: imbl(CH)
"""



from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import QCoreApplication
from PyQt5 import uic
import sys
import seqConnect

class SeqMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("sequencer.ui",self)
        self.setWindowTitle("Chip irradition sequencer")

    def closeEvent(self, event):
        """
        Overrides the close event to handle application exit.
        """
        reply = QMessageBox.question(self, 'Message',
        "Are you sure to want to quit?", QMessageBox.Yes |
        QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            QMessageBox.warning(self, 'Please wait', \
                    'Channel Access is closing down...')
            seqConnect.shutDown()
            event.accept()  # Allow the window to close
            print("Application closing...")
            # Perform any cleanup here before the application fully exits
            QCoreApplication.instance().quit() # Ensure the application quits
        else:
            event.ignore()  # Prevent the window from closing

if __name__ == "__main__":
    app =  QApplication(sys.argv)
    # window = uic.loadUi("sequencer.ui")
    # SeqMainWindow = uic.loadUi("sequencer.ui")
    window=SeqMainWindow()
    seqConnect.initConnectGUI(window,app) # Make the GUI event-slot connections
    window.show()
    sys.exit(app.exec())

