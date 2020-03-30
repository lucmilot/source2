# -*- coding: utf-8 -*-
"""
Created on Wed Oct 17 12:04:49 2018

@author: XT21586
"""


import win32com.client as win32

import os, sys, getopt

import time

from time import gmtime, strftime

import pyodbc
import numpy as np
import pandas as pd

import re

import ftplib

from contextlib import redirect_stdout

import io

import sqlparse



'''
import pyodbc
import pandas as pd

import numpy as np

import os, sys

import io

import time

import win32com.client as win32

import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory

import tkinter.ttk as ttk

import tkinter.messagebox as msg


#get all the job info for all jobs formating YMMDD etc with FFFF

import threading
import re



import winreg as winreg



'''



def get_seed(in_file):
    
    excel = win32.gencache.EnsureDispatch('Excel.Application')       
    
    wb1 = excel.Workbooks.Open(in_file)
    excel.Visible = True
    excel.ActiveSheet.Columns.AutoFit()  
    
    input("Save Excel and quit excel before pressing enter? ")     

    labels = [
    'selection',
    'seed'
    ]
    
    df_seed = pd.read_csv(in_file , names=labels , skiprows = 1)
    
    df_seed.fillna('', inplace=True)
    
    # \w Any word character (letter, number, underscore ) 
    df_seed  = df_seed[df_seed['selection'].str.contains(re.compile('\w'))] 
        
    List_seed = df_seed['seed'].values.tolist()
    
    if len(List_seed) == 0 :
        print( "nothing selected in input : " + in_file)
        sys.exit(0)    
    
    return List_seed





def main_process() :

    try:
        sess = ftplib.FTP('imftpb',username,password)
    except ftplib.Error as ex:
        err1 = ex.args[1]
        print (err1)
        sys.exit()    
    
    List_seed = get_seed(in_file)
   
    for lv123 in List_seed :
    
        out_file_MBR = out_file + '_' + lv123 + '.csv'
        if os.path.exists(out_file_MBR):
            os.remove(out_file_MBR)	            

        print( lv123 )
        try:
            sess.cwd("'" + lv123 + "'")
            #file_list = sess.nlst()
            f = io.StringIO()
            with redirect_stdout(f):
                sess.dir()
    
        except:
            print (lv123 + ' :not found or no permission')
            continue             
         
    
        label_1 = ['Name','VV.MM','Created','Changedate','Changetime','Sze','Init','Mod','Id']
        lst_1 = [str.split(x) for x in list(f.getvalue().splitlines()[1:])]
        df1 = pd.DataFrame(lst_1)
        df1.columns = label_1
        df1.insert(loc=0, column='Lv123', value=np.array([lv123] * len(lst_1)))
        df1.insert(loc=0, column='selection', value= np.array(['x'] * len(lst_1)))
        
        if len( df1) > 0 :
            df1.to_csv(out_file_MBR,mode = 'w',header=True, index = False)
            
        
    
    sess.quit



def main_in(argv):
    global in_file, out_file, username, password    
    
    wrk_dir = ''
    in_file_1 = ''
    out_file_1 = ''
    username = ''
    password = ''
    try:
        opts, args = getopt.getopt(argv,"hw:i:o:u:p:",["help","wrkd=","inf=","outf=","usnam=","passw="])
    except getopt.GetoptError:
        print ('CRUD.py -w <workingdir> -i <infilename> -o <outfilename> -u <username) -p <password>')
        sys.exit(2)
        
     
    for opt, arg in opts:
        if opt == '-h':
            print ('CRUD.py -w <workingdir> -i <infilename> -o <outfilename> -u <username) -p <password>')
            sys.exit()
        elif opt in ("-w", "--wrkd"):
            wrk_dir = arg
        elif opt in ("-i", "--inf"):
            in_file_1 = arg                     
        elif opt in ("-o", "--outf"):
            out_file_1 = arg            
        elif opt in ("-u", "--usnam"):
            username = arg
        elif opt in ("-p", "--passw"):
            password = arg         

    in_file = wrk_dir + "\\" + in_file_1 + ".CSV"
    out_file = wrk_dir + "\\" + out_file_1

    #for testing put the following in  RUN  ---  Configuration per file  --- Command line option 
    #-w C:\Users\XT21586\Documents\document\_DOSSET\_promoted_V2\result -i COB_LIBRARY_SEED -o COB_MBR_SEED -u CNDWLMM -p lcjcmhf3
    
    #wrk_dir = "C:\Users\XT21586\Documents\document\_DOSSET\_promoted_V2\result"
    #username = "cndwlmm"
    #password = "lcjcmhf3"    
    #in_file = wrk_dir + "COB_LIBRARY_SEED.CSV"
    #out_file = wrk_dir + "COB_MBR_SEED.CSV"


if __name__ == "__main__":
    
    main_in(sys.argv[1:])
    #out_dir = r"C:\Users\XT21586\Documents\document\_DOSSET\_promoted_V2\result\"
    #sername = "cndwlmm"
    #password = "lcjcmhfx"    

    print (in_file)    
    print (out_file)
    print (username)
  
    main_process()   


