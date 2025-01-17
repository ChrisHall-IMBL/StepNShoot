# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 15:05:05 2025

@author: imbl
"""

from PyQt5.QtWidgets import QPushButton, QLineEdit, QLabel
# from PyQt5.QtWidgets import QPlainTextEdit, QComboBox, QCheckBox
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt5.QtCore import QTimer, QDateTime
import csv, time
from epics import caget, caput

def initConnectGUI(GUI,app):
    # Define the Qt widgets to connect to he GUI
    # Use the findChild fucntion to get their handles
    # Set defatul values where required
    global GUIhandle
    GUIhandle=GUI # Make the GUI handle accessible
    global AppHandle
    AppHandle=app
    
    # Table
    global Table
    Table=GUI.findChild(QTableWidget, "tableWidgetPosList")
    Table.setRowCount(1)
    Table.setColumnCount(4)
    #Table.setHorizontalHeaderLabels(["Descriptor", "X", "Y"])
    Table.itemClicked.connect(TableClick)
    
    # Labels
    global GoToX
    GoToX=GUI.findChild(QLabel, "labelGoToX")
    global GoToY
    GoToY=GUI.findChild(QLabel, "labelGoToY")
    global Status
    Status=GUI.findChild(QLabel, "labelStatus")
    global ShowTime
    ShowTime=GUI.findChild(QLabel, "labelTime")
    global StartTime
    StartTime=GUI.findChild(QLabel, "labelStartTime")
    global StopTime
    StopTime=GUI.findChild(QLabel, "labelStopTime")
    
    # Line edits
    global FileName, sequenceFile
    FileName=GUI.findChild(QLineEdit, "lineEditSeqFile")
    #sequenceFile="sequence.csv"
    sequenceFile=FileName.text()
    LoadSequence()
    
    global XPV
    XPV=GUI.findChild(QLineEdit, "lineEditXPV")
    global YPV
    YPV=GUI.findChild(QLineEdit, "lineEditYPV")
    UpdatePos()
    global ADPV
    ADPV=GUI.findChild(QLineEdit, "lineEditADPV")
    global ShutterPV
    ShutterPV='SR08ID01IS01'
    global SnapTime
    SnapTime=GUI.findChild(QLineEdit, "lineEditSnapTime")
    
    # Buttons
    global GoButton
    GoButton=GUI.findChild(QPushButton, "pushButtonGo")
    GoButton.clicked.connect(GoSequence)
    global GoToButton
    GoToButton=GUI.findChild(QPushButton, "pushButtonGoTo")
    GoToButton.clicked.connect(GoTo)
    global LoadButton
    LoadButton=GUI.findChild(QPushButton, "pushButtonLoadSeq")
    LoadButton.clicked.connect(LoadSequence)
    global SnapButton
    SnapButton=GUI.findChild(QPushButton, "pushButtonSnap")
    SnapButton.clicked.connect(Snap)
    global ExposeButton
    ExposeButton=GUI.findChild(QPushButton, "pushButtonExpose")
    ExposeButton.clicked.connect(Expose)
    global AbortButton
    AbortButton=GUI.findChild(QPushButton, "pushButtonAbort")
    AbortButton.clicked.connect(Abort)
    
# Set up a timer
    global Timer
    Timer=QTimer()
    Timer.setSingleShot(True)

# Event callback functions
def GoTo():
    # Reponse to GoTo button click
    # Move motors to the position in the GoTo labels
    X=float(GoToX.text())
    Y=float(GoToY.text())
    Status.setText('Going to position: {}, {}'.format(X,Y))
    XMotorPV=XPV.text()
    YMotorPV=YPV.text()
    caput(XMotorPV,X)
    caput(YMotorPV,Y)
    UpdatePos() # Read back thte positions into the edit boxes
    Status.setText('Idle')

def GoSequence():
    # Response to Run sequence button click
    # Move and expose as instruceted in each line of the table.
    Status.setText('Running Sequence')
    # print('Let''s go!')
    try:
        for row in Table.rows():
            GotoPos(row)
            ShutterEtime(row) # Blocks until exposure has finished.
            
    except:
        print('Didn''t work!')
    
def LoadSequence():
    # Response to Load sequence button click
    # Import the sequence csv file and load into the table.
    sequenceFile=FileName.text()
    print('Loading sequence')
    try:
        with open(sequenceFile, newline='') as csvfile:
            seqReader = csv.reader(csvfile)
            Table.setRowCount(0) # Clears the table. Could use the clear() slot
            for r, Trow in enumerate(seqReader):
                # print(', '.join(Trow))
                if r == 0:
                    Table.setRowCount(1) # First row
                    Table.setHorizontalHeaderLabels(Trow)
                else:
                    row=Table.rowCount()-1
                    Table.insertRow(row)
                    Table.setItem(row,0,QTableWidgetItem(Trow[0]))
                    Table.setItem(row,1,QTableWidgetItem(Trow[1]))
                    Table.setItem(row,2,QTableWidgetItem(Trow[2]))
                    Table.setItem(row,3,QTableWidgetItem(Trow[3]))
    except:
        print('Can''t load file: ',sequenceFile)

def TableClick():
    # Response to click on the sequence table.
    # Copy the row information indicated in the GoTo labels.
    row=Table.currentRow()
    X=Table.item(row, 1).text()
    Y=Table.item(row, 2).text()
    T=Table.item(row, 3).text()
    print('Table clicked on row: {0}. position X: {1}, Position Y: {2}, Time {3}'.format(row,X,Y,T))
    GoToX.setText(X)
    GoToY.setText(Y)

def Snap():
    # Response to a click on the Snap button
    # Program the detector to drive the shutter and take a snap for a snap time
    # Assumes the shutter section of AD is set up correctly.
    SetSnapEtime()
    ADPVroot=ADPV.text()
    caput(ADPVroot+':CAM:AcquirePeriod', 0) # Set minimum acquire period
    caput(ADPVroot+':CAM:ImageMode', 0) # Single image
    caput(ADPVroot+':CAM:TriggerMode', 0) # Internal trigger
    caput(ADPVroot+':CAM:ShutterMode', 1) # EPICS driven shutter
    caput('SR08ID01IS01:SHUTTERENABLE_CMD',1) # Enable this shutter
    caput('SR08ID01IS01:EXPOSURETRIGGERMODE_CMD',1) # Set software timing control  
    caput(ADPVroot+':CAM:Acquire', 1) # Make the snap
    while caget(ADPVroot+':CAM:Acquire') != 0:
        time.sleep(0.5)
    Status.setText('Snap done')
    
def Expose():   
    # Response to click on the Expose button
    # Set imager running continosly with SnapT exposure
    ADPVroot=ADPV.text()
    caput(ADPVroot+':CAM:ShutterMode', 0) # No shutter control
    SetSnapEtime() # Assume there will be continous monitoring with the detector
    caput(ADPVroot+':CAM:ImageMode', 2) # Run in continous mode
    caput(ADPVroot+':CAM:Acquire', 1) # Start the detector running
    row=Table.currentRow()
    ShutterEtime(row) # Run the long exposure
    caput(ADPVroot+':CAM:Acquire', 0) # Stop the detector running
    # caput(ShutterPV+':EXPOSURESTART_CMD',1) # Start the shutter timer
    # while caget(ShutterPV+':SHUTTEROPEN_MONITOR') != 0:
    #     time.sleep(0.5)
    Status.setText('Exposure done')
    
def Abort():
    caput(ShutterPV+':SHUTTEROPEN_CMD',0) # Close the shutter
    Timer.stop() # Stop the timer
    Status.setText('Aborted')
    
# Helper functions
def UpdatePos():
    # Read the motor positions using CA, and populate the edit boxes
    YMotorPV=YPV.text()
    YPos=caget(YMotorPV)
    labYPos=GUIhandle.findChild(QLabel, "labelYPos")
    labYPos.setText('%.3f'%YPos)
    XMotorPV=XPV.text()
    XPos=caget(XMotorPV)
    labXPos=GUIhandle.findChild(QLabel, "labelXPos")
    labXPos.setText('%.3f'%XPos)
    
def SetSnapEtime():
    SnapT=float(SnapTime.text())
    ADPVroot=ADPV.text()
    caput(ADPVroot+':CAM:Acquire', 0) # Ensure detector is not collecting
    ADPVEtime=ADPVroot+':CAM:AcquireTime'
    # print('Current Etime is :',caget(ADPVEtime))
    caput(ADPVEtime, SnapT)

def ShutterEtime(row):
    # Opens the shutter for an exposure time given in the table row
    caput(ShutterPV +':SHUTTERENABLE_CMD',1) # Enable the shutter
    caput(ShutterPV +':EXPOSURETRIGGERMODE_CMD',1) # Set software control
    ExpT=1000*float(Table.item(row, 3).text()) # Exposure time In ms
    Status.setText('Exposing here for: {} ms'.format(ExpT))
    caput(ShutterPV+':SHUTTEROPEN_CMD',1) # Open the shutter
    current_time=QDateTime.currentDateTime()
    formatted_time=current_time.toString('yyyy-MM-dd hh:mm:ss')
    StartTime.setText(formatted_time)
    Timer.start(int(ExpT))
    TimeLeft=Timer.remainingTime()
    while TimeLeft != 0: # Check the timer every second
        time.sleep(1)
        TimeLeft=Timer.remainingTime()
        # print('Time remaining: ',TimeLeft)
        ShowTime.setText(str(TimeLeft))
        AppHandle.processEvents()
    Timer.stop()
    caput(ShutterPV+':SHUTTEROPEN_CMD',0) # Close the shutter
    current_time=QDateTime.currentDateTime()
    formatted_time=current_time.toString('yyyy-MM-dd hh:mm:ss')
    StopTime.setText(formatted_time)
    # Internal shutter timer method   
    # caput(ShutterPV+':SHUTTERENABLE_CMD',1) # Enable ths shutter
    # caput(ShutterPV+':EXPOSURETRIGGERMODE_CMD',0) # Set to internal Timer
    # caput(ShutterPV+':EXPOSUREPERIOD_CMD',ExpT) # Set the exposure time
    # caput(ShutterPV+':CYCLEPERIOD_CMD',1.1*ExpT) # Set cycle perid 10% longer
    # caput(ShutterPV+':EXPOSUREREPEATS_CMD',1) # Set for a single cycle
    
def GotoPos(row):
    X=Table.item(row, 1).text()
    Y=Table.item(row, 2).text()
    XMotorPV=XPV.text()
    YMotorPV=YPV.text()
    caput(XMotorPV,X)
    caput(YMotorPV,Y)
    UpdatePos() # Read back thte positions into the edit boxes
