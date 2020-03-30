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
msg.showinfo("Information","You need to select the proper Grab_all_file_PO  ")
rt.destroy()
#root.quit() 


rt = tk.Tk() 
rt.withdraw()
in_file = askopenfilename(parent=rt)
rt.destroy()




rt = tk.Tk()
rt.withdraw()
msg.showinfo("Information","SELECT LV123 with X in the followin EXCEL")
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
'flag', 'lv123'
]
df_seed = pd.read_csv(in_file , names=labels , skiprows = 1)
df_seed.fillna('', inplace=True)
# \w Any word character (letter, number, underscore )
df_seed  = df_seed[df_seed['flag'].str.contains(re.compile('\w'))] 


List_seed = df_seed['lv123'].values.tolist()

if len(List_seed) == 0 :
    print( "nothing selected in input : " + in_file)
    sys.exit(0)




out_dir = r"/".join(in_file.split(r"/")[0:-1])


rt = tk.Tk()
rt.withdraw()
msg.showinfo("Information","The result will be put in: " + out_dir + "//Grab_all_file_PO_MBR_...  ")
rt.destroy()
#root.quit() 



get_credential()

try:
    sess = ftplib.FTP('imftpb',user_name,user_password)
except:
    rt = tk.Tk()
    rt.withdraw()
    msg.showinfo("Error","cant conect to FTP ")
    rt.destroy   
    sys.exit()


for lv123 in List_seed :

    out_file_PO_MBR = out_dir + '/Grab_all_file_PO_MBR_' + lv123 + '.csv'
    if os.path.exists(out_file_PO_MBR):
        os.remove(out_file_PO_MBR)	            
      
    tot_PO = []   
    #arr_tot = np.array([],dtype=np.str)
    arr_PO = np.array([],dtype=np.str)
    arrx_PO = np.array([],dtype=np.str)
    arry_PO_MBR = np.array([],dtype=np.str)
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
    

    
    if len( df1) > 0 :
        df1.to_csv(out_file_PO_MBR,mode = 'w',header=True, index = False)
        
    

sess.quit



