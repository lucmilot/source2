# -*- coding: utf-8 -*-
"""
Created on Wed Oct 17 12:04:49 2018

@author: XT21586
"""


import pyodbc
import pandas as pd

import os, sys

import time

import win32com.client as win32

import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory

import tkinter.ttk as ttk

import tkinter.messagebox as msg




#get all the job info for all jobs formating YMMDD etc with FFFF

import threading
import pyodbc
import re



import winreg as winreg



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

in_sql = '''
select distinct
DDS_DSN 
from 
re.bjdds
where
DDS_DSN <> ' '
order by DDS_DSN
;
'''

labels = [
'DDS_DSN'
]



rt = tk.Tk()
rt.withdraw()
msg.showinfo("Information","You need to select a working directory ")
rt.destroy()
#root.quit() 


rt = tk.Tk() 
rt.withdraw()
out_dir = askdirectory(title = 'Select Directory where file RESULT_JOB_SQL.CSV will be create (delete and recreate if already present ',initialdir=os.getcwd())
rt.destroy()

if out_dir == "":
    sys.exit

out_file = out_dir + '/Grab_all_file_with_FTP.CSV'
if os.path.exists(out_file):
    os.remove(out_file)
    



get_credential()


try:
    cnxn = pyodbc.connect('DSN=LOCDB2K;UID='+user_name+';PWD='+user_password+';CURRENTSCHEMA=RE')
except:
    rt = tk.Tk()
    rt.withdraw()
    msg.showinfo("Error","cant conect to db2 ")
    rt.destroy   
    sys.exit()




cursor = cnxn.cursor()
cursor.execute(in_sql)
print('Starting fetchall.......')
rows = cursor.fetchall()
cursor.close()
cnxn.close()

df = pd.DataFrame.from_records(rows, columns=labels) 




t3 = []
x1 = []

for index, row in df.iterrows():
    x1 = re.split(r"\.",row['DDS_DSN'])
    if len(x1) >= 2:
        t3.append(str.strip(x1[0]))    

df_t3 = pd.DataFrame(t3)

df_t3.drop_duplicates(inplace = True)
df_t4 = df_t3.sort_values( [0]) 
df_t4.reset_index(inplace=True, drop=True) 

df_t4  = df_t4[~df_t4[0].str.contains(re.compile(r"(\%)|(\&)"))] 
df_t4  = df_t4[~df_t4[0].str.contains(re.compile(r"^(\*)|^(\')"))] 


t4_list = df_t4[0].values.tolist()


     
df_tot_wrk = pd.DataFrame(list(zip([' '] * len(t4_list),t4_list)), columns=['flag', 'lv1'])
df_tot_wrk.to_csv(out_file,mode = 'w',header=True, index = False)    










