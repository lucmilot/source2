# -*- coding: utf-8 -*-
"""
Created on Wed Oct 17 12:04:49 2018

@author: XT21586
"""

import ftplib

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


from contextlib import redirect_stdout



def get_credential():  
    global user_name, user_password, window1, txt
    def clicked_Entry_username():   
        global return_txt 
        return_txt = txt.get()
        window1.destroy()  
        

    window1 = tk.Tk()
    window1.title("Enter Username")
    window1.config(height=100, width=200, bg="#C2C2D6") 
    txt = tk.Entry(window1,width=40)
    txt.grid(column=1, row=1)
    btn = tk.Button(window1, text="Submit", bg="white", fg="green",  height = 2, width = 10, command=clicked_Entry_username)
    btn.grid(column=2, row=1)      
    window1.mainloop()
    user_name = return_txt
    

    window1 = tk.Tk()
    window1.title("Enter Password")
    window1.config(height=100, width=200, bg="#C2C2D6") 
    txt = tk.Entry(window1,width=40)
    txt.grid(column=1, row=1)
    btn = tk.Button(window1, text="Submit", bg="white", fg="green",  height = 2, width = 10, command=clicked_Entry_username)
    btn.grid(column=2, row=1)      
    window1.mainloop()
    user_password = return_txt  
       

    return 


rt = tk.Tk()
rt.withdraw()
msg.showinfo("Information","You need to select the proper Grab_all_file_with_FTP ")
rt.destroy()
#root.quit() 


rt = tk.Tk() 
rt.withdraw()
in_file = askopenfilename(parent=rt)
rt.destroy()



get_credential()


try:
    sess = ftplib.FTP('imftpb',user_name,user_password)
except:
    rt = tk.Tk()
    rt.withdraw()
    msg.showinfo("Error","cant conect to FTP ")
    rt.destroy   
    sys.exit()



rt = tk.Tk()
rt.withdraw()
msg.showinfo("Information","SELECT LV1 with X in the followin EXCEL")
rt.destroy()
    

excel = win32.gencache.EnsureDispatch('Excel.Application')
wb = excel.Workbooks.Open(in_file)
excel.Visible = True
excel.ActiveSheet.Columns.AutoFit()
excel.Quit()


rt = tk.Tk()
rt.withdraw()
msg.showinfo("Information","DONT PRESS OK before saving excel ")
rt.destroy()


labels = [
'flag', 'lv1'
]
df_seed = pd.read_csv(in_file , names=labels , skiprows = 1)
df_seed.fillna('', inplace=True)
# \w Any word character (letter, number, underscore )
df_seed  = df_seed[df_seed['flag'].str.contains(re.compile('\w'))] 


List_seed = df_seed['lv1'].values.tolist()

if len(List_seed) == 0 :
    print( "nothing selected in input : " + in_file)
    sys.exit(0)

'''
from time import gmtime, strftime
tt = strftime("%Y-%m-%d %H:%M:%S", gmtime())
tt = tt.replace(" ", "_")

out_file_PO = path+"\\result\\"+"Grab_all_file_PO_"+tt+".csv" 
if os.path.exists(out_file_PO):
    os.remove(out_file_PO)	    
'''


rt = tk.Tk()
rt.withdraw()
msg.showinfo("Information","You need to select a working directory ")
rt.destroy()
#root.quit() 


rt = tk.Tk() 
rt.withdraw()
out_dir = askdirectory(title = 'Select Directory where file Grab_all_file_PO_MBR ... will be create (delete and recreate if already present ',initialdir=os.getcwd())
rt.destroy()


out_file_PO_MBR = out_dir + '/Grab_all_file_PO.csv'
if os.path.exists(out_file_PO_MBR):
    os.remove(out_file_PO_MBR)	     


append_sw = 0
for lv1 in List_seed : 
    
    tot_PO = []   
    #arr_tot = np.array([],dtype=np.str)
    arr_PO = np.array([],dtype=np.str)
    arrx_PO = np.array([],dtype=np.str)
    arry_PO_MBR = np.array([],dtype=np.str)
    print( lv1 )
    try:
        sess.cwd("'" + lv1 + "'")
        #file_list = sess.nlst()
        f = io.StringIO()
        with redirect_stdout(f):
            sess.dir()

    except:
        print (lv1 + ' :not found or no permission')
        continue             
     
    #[1:] we start after header
    #test = np.array(f.getvalue().splitlines())[0]
    #Volume Unit    Referred Ext Used Recfm Lrecl BlkSz Dsorg Dsname
    
    arr_1 = np.array(f.getvalue().splitlines())[1:]
    
    #arr_ARCIVE = arr_1[pd.Series(arr_1).str.contains(re.compile('ARCIVE'))] 
    #arr_ARCIVE_s = np.array([re.findall(r'\S+', x) for x in arr_ARCIVE])  
    #arr_ARCIVE_s1 = np.array([lv1 + "." + x[5] for x in arr_ARCIVE_s ]) 
    #arr_tot = np.append(arr_tot, arr_ARCIVE_s1)
    
    arr_NOT_ARCIVE = arr_1[~pd.Series(arr_1).str.contains(re.compile('ARCIVE'))] 
    arr_NOT_ARCIVE_s = np.array([re.findall(r'\S+', x) for x in arr_NOT_ARCIVE])   
 
    
    arr_NOT_ARCIVE_s1 = arr_NOT_ARCIVE_s[[ (x[1] != 'Tape') & (x[1] != 'Error') & (x[0] != 'GDG') & (x[0] != 'Migrated') & (x[1] != 'Not') for x in arr_NOT_ARCIVE_s ]] 

    
    #arr1_NOT_PO = np.array([lv1 + "." + x[9] for x in arr_NOT_ARCIVE_s1[[ (len(x) == 10) & (x[8] != 'PO') for x in arr_NOT_ARCIVE_s1 ]] ])
    #arr2_NOT_PO = np.array([lv1 + "." + x[8] for x in arr_NOT_ARCIVE_s1[[ (len(x) == 9) & (x[7] != 'PO') for x in arr_NOT_ARCIVE_s1 ]] ])
    #arr_NOT_PO = np.hstack([arr1_NOT_PO,arr2_NOT_PO])
    #arr_tot = np.append(arr_tot, arr_NOT_PO)
   

    arr1_PO = np.array([lv1 + "." + x[9] for x in arr_NOT_ARCIVE_s1[[ (len(x) == 10) & (x[8] == 'PO') for x in arr_NOT_ARCIVE_s1 ]] ])
    arr2_PO = np.array([lv1 + "." + x[8] for x in arr_NOT_ARCIVE_s1[[ (len(x) == 9) & (x[7] == 'PO') for x in arr_NOT_ARCIVE_s1 ]] ])
 
    debugx = np.array([lv1 + "." + x[0] + " " + x[1] + " " + x[2] + " " + x[3]for x in arr_NOT_ARCIVE_s1[[ (len(x) < 9) for x in arr_NOT_ARCIVE_s1 ]] ])
        
    
    if len(arr2_PO) > 0 : 
        arr_PO = np.hstack([arr1_PO,arr2_PO])
    else:
        arr_PO = arr1_PO
        
    df_tot_PO = pd.DataFrame(list(zip([' '] * len(arr_PO),arr_PO)), columns=['flag', 'lv123'])

    if append_sw == 0:
        append_sw = 1
        df_tot_PO.to_csv(out_file_PO_MBR,mode = 'w',header=True, index = False)
    else:
        df_tot_PO.to_csv(out_file_PO_MBR,mode = 'a',header=False, index = False)



sess.quit

rt = tk.Tk()
rt.withdraw()
msg.showinfo("Information","LVL 2 3 in : " + out_file_PO_MBR)
rt.destroy()

