# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
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

global choice_return, file_list, listbox1,master

    
global ret_txt    

choice_return = ""
file_list = []

class RegEntry(object):
    def __init__(self,pathx,namex):
        super(RegEntry,self).__init__
        self.path = pathx
        self.name = namex
        try:
            key1 = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.path, 0, winreg.KEY_WRITE)   
        except:  # BI_LUM is not there we create it
            try:
                self.path = r'Software'
                self.name = r'BI_LUM2' 
                self.create_sub_key()
                key1 = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.path, 0, winreg.KEY_WRITE) 
            except: 
                print ('bizarre1')  
                
        #reference list stored in namex and call list_entry         
        self.path = pathx
        self.name = namex
        values = self.list_entry()
        if values is None :
            self.clear_entry()
        

    def create_sub_key(self):
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.path, 0, winreg.KEY_WRITE)
        winreg.CreateKeyEx(key, self.name, 0, winreg.KEY_WRITE)
        winreg.CloseKey(key)

    def list_entry(self):
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.path, 0, winreg.KEY_READ)
        try:
            values = winreg.QueryValueEx(key, self.name)
            winreg.CloseKey(key)
            return values[0]
        except:
            print('bizarre2')
            return None

    def clear_entry(self):
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.path, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, self.name, 0, winreg.REG_MULTI_SZ, [])
        winreg.CloseKey(key)
        
    def add_entry(self, hid):
        values = self.list_entry()
        '''
        if (values is not None) and (hid not in values):
            values.append(hid)
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, self.name, 0, winreg.REG_MULTI_SZ, values)
            winreg.CloseKey(key)
        '''    
        if (values is not None) :
            values = [hid]
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, self.name, 0, winreg.REG_MULTI_SZ, values)
            winreg.CloseKey(key)            



def input_entry(title):  

    def clicked_Entry_username():   
        global return_txt 
        return_txt = txt.get()
        window1.destroy()  
        

    window1 = tk.Tk()
    window1.title(title)
    window1.config(height=100, width=200, bg="#C2C2D6") 
    txt = tk.Entry(window1,width=40)
    txt.grid(column=1, row=1)
    btn = tk.Button(window1, text="Submit", bg="white", fg="green",  height = 2, width = 10, command=clicked_Entry_username)
    btn.grid(column=2, row=1)      
    window1.mainloop()
    return return_txt
    




def process_db2(cursor, out_file ) :
    
    labels = [
    'DSN',        
    'JOBNAME',
    #step position within the job
    'STEP_PROGR',
    'PGM_NAME',
    #dd position within the step
    'N_PROGR',
    'DDNAME',
    'DISP1'
            ]
    
    
    df_out = pd.DataFrame()
    line_count = 0
        
    while True:
        rows = cursor.fetchmany(10000)
    
        if len(rows) == 0:
                break
            
        df = pd.DataFrame.from_records(rows, columns=labels)
        df_out = pd.concat([df_out, df])
        if line_count == 1:
            df.to_csv(out_file,mode = 'a',header=True, index = False)
        else:
            df.to_csv(out_file,mode = 'a',header=False, index = False)
        
        line_count += len(rows)
        print(line_count)
        
        break

    df_out.sort_values( ['JOBNAME','STEP_PROGR'])      
    df_out.to_csv(out_file, mode = 'w',header=True, index = False)
    

# Function to check state of thread1 and to update progressbar #
def process_selection_with_progress_bar(thread, main_rt):
    
    rt = tk.Tk()   
    
    rt.title("Progressbar ------------")
    rt.config(bg = '#F0F0F0')  
                
    canvas = tk.Canvas(rt, relief = tk.FLAT, background = "#D2D2D2",
                                            width = 800, height = 20)
                       
    pb1 = ttk.Progressbar(canvas, orient=tk.HORIZONTAL,
                                      length=800, mode="indeterminate"                                     
                                      )

    canvas.create_window(1, 1, anchor=tk.NW, window=pb1)
    canvas.grid()

    # places and starts progress bar #
    pb1.pack()
    pb1.start()
    
    thread.start()

    # checks whether thread is alive #
    while thread.is_alive():
        rt.update()
        pass

    pb1.destroy()
    canvas.destroy()
    rt.destroy()
    main_rt.destroy()
    
    return 






user_name = input_entry('User Name')    

user_password = input_entry('User Password')    


#to hold the message box output
root = tk.Tk()
root.withdraw()
out_file = 'xxx'


'''
pathx = r'Software\BI_LUM2'
namex = "job_iter_res"
tt = RegEntry(pathx,namex)
tt.add_entry('test2')     

pathx = r'Software\BI_LUM2'
namex = "job_iter_res"
tt = RegEntry(pathx,namex)
file_list = tt.list_entry()    
'''
 

main_rt = tk.Tk() 
main_rt.withdraw()

#out_file = askopenfilename(parent=rt)
out_dir = askdirectory(title = 'Select Directory where file RESULT_JOB_SQL.CSV will be create (delete and recreate if already present ',initialdir=os.getcwd())

if out_dir == "":
    sys.exit

out_file = out_dir + '/RESULT_JOB_SQL.CSV'

if os.path.exists(out_file):
    os.remove(out_file)



in_sql = '''
select

trim(dds_dsn) as dsn,
trim(DDS_JOBNAME) as JOBNAME,
trim(DDS_STEP_PROGR) as STEP_PROGR,
trim(stp.STP_PGMMVS)  as pgmname,
trim(DDS_N_PROGR) as N_PROGR,
trim(DDS_DDNAME) as DDNAME,
trim(DDS_DISP1) as DISP1

from re.bjdds as dds


left outer join 
RE.BJSTEPS as stp
on
(
dds.dds_jobname = stp.stp_jobname and
dds.dds_step_progr = stp.stp_n_progr
)

where dds_dsn <> ''
order by
dsn,
jobname, 
STEP_PROGR,
N_PROGR
;
'''


user_name = input_entry('User Name')    

user_password = input_entry('User Password')    


cnxn = pyodbc.connect('DSN=LOCDB2K;UID=' + user_name + ';PWD=' + user_password + ';CURRENTSCHEMA=RE')
cursor = cnxn.cursor()
cursor.execute(in_sql)

argx = (cursor,out_file)  
thread1 = threading.Thread(target=process_db2, args=argx)
process_selection_with_progress_bar(thread1, main_rt)

cursor.close()
cnxn.close()


msg.showinfo("Information",'RESULT are in : ' + out_file + '\n This will be used as hidden source by python : 2-jobiteration_sql_to_csv.py')
root.destroy


print ('DONE')