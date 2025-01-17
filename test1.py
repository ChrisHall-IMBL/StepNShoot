# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 15:57:09 2025

@author: imbl
"""
import csv

sequenceFile="sequence.csv"
with open(sequenceFile, newline='') as csvfile:
    seqReader = csv.reader(csvfile)
    for Trow in seqReader:
        print(', '.join(Trow))