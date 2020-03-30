# -*- coding: utf-8 -*-
"""
Created on Mon Jul 30 05:41:13 2018

@author: XT21586
"""

import os
import sys
from cx_Freeze import setup, Executable

#run with : python setup_cxfreeze_2-jobiteration_sql_to_csv.py build
#OR
#run with : python setup_cxfreeze_pickle_inquiry.py bdist_msi

# Dependencies are automatically detected, but it might need fine tuning.
#build_exe_options = {"packages": ["os"], "excludes": ["tkinter"]}

build_exe_options = {"includes": ["tkinter"]}

os.environ['TCL_LIBRARY'] = r'C:\Users\XT21586\AppData\Local\Continuum\anaconda3\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Users\XT21586\AppData\Local\Continuum\anaconda3\tcl\tk8.6'


pathx = os.getcwd()
print (pathx)

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "2-jobiteration_sql_to_csv_V1",
        version = "1.0",
        description = "luc!",
        options = {"build_exe": build_exe_options},
        executables = [Executable("2-jobiteration_sql_to_csv.py", base=base)])

