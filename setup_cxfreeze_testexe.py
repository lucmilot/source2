# -*- coding: utf-8 -*-
"""
Created on Mon Jul 30 05:41:13 2018

@author: XT21586
"""

import os
import sys

from glob import glob
from cx_Freeze import setup, Executable

#run on the directory where the py is : python setup_cxfreeze_testexe.py build > cxfreeze_result.txt


#build_exe_options = {"includes": ["tkinter"]}
build_exe_options = {"packages": ["os","numpy"], "excludes": ["tkinter"]}



''' 
mplBackendsPath = os.path.join(os.path.split(sys.executable)[0],
                        "Lib/site-packages/matplotlib/backends/backend_*")

fileList = glob(mplBackendsPath)

moduleList = []

for mod in fileList:
    modules = os.path.splitext(os.path.basename(mod))[0]
    if not modules == "backend_qt4agg":
        moduleList.append("matplotlib.backends." + modules)

build_exe_options = {"excludes": ["tkinter"] + moduleList, "optimize": 2}
'''



os.environ['TCL_LIBRARY'] = r'C:\Users\XT21586\AppData\Local\Continuum\anaconda3\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Users\XT21586\AppData\Local\Continuum\anaconda3\tcl\tk8.6'


pathx = os.getcwd()
print (pathx)

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "DOCET_ITERATION_REFRESH_V2",
        version = "1.0",
        description = "refresh lineage info from db2k, once a week",
        options = {"build_exe": build_exe_options},
        executables = [Executable("testexe.py", base=base)])

'''
mplBackendsPath = os.path.join(os.path.split(sys.executable)[0],
                        "Lib/site-packages/matplotlib/backends/backend_*")

#fileList = glob.glob(mplBackendsPath)
fileList = glob(mplBackendsPath)

moduleList = []

for mod in fileList:
    modules = os.path.splitext(os.path.basename(mod))[0]
    if not modules == "backend_qt4agg":
        moduleList.append("matplotlib.backends." + modules)

build_exe_options_2 = {"excludes": ["tkinter"] + moduleList, "optimize": 2}
'''