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




def enter_input(label_txt,hidden=''):
    global m
    def show(event=None): # handler
        global ret_txt 
        ret_txt = inp.get()
        m.destroy()


    m = tk.Tk()
    m.title('to access DB2K')    

    prompt = tk.Label(m, text=label_txt)
    prompt.pack(fill='x', side='left')
    
    if hidden == '' : 
        inp = tk.Entry(m,width = 30)
    else:
        inp = tk.Entry(m,show="*", width = 30)
    inp.bind('<Return>', show) # binding the Return event with an handler
    inp.pack(fill='x', side='left')
    
    ok = tk.Button(m, text='', command=show)
    ok.pack(fill='x', side='left')
    
    m.mainloop()
    

    
    return ret_txt




def process_db2(cursor, out_file ) :

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
    
    return
    

# Function to check state of thread1 and to update progressbar #
def process_selection_with_progress_bar(thread, main_rt):
    
    rt = tk.Tk()   
    
    rt.title("Fetching DB2 info (around 1 min)  -------")
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



def transform_df(df):    
    df1  = df[~df['DSN'].str.contains(re.compile(r'^&'))]
    df1  = df1[~df1['DSN'].str.contains(re.compile(r'^\*\.'))]
    df1  = df1[~df1['DSN'].str.contains(re.compile('^\*\.'))]
    df1  = df1[~df1['DSN'].str.contains(re.compile('LOADLIB'))]
    df1  = df1[~df1['DSN'].str.contains(re.compile('CONTROL'))]
    df1  = df1[~df1['DSN'].str.contains(re.compile('COPYLIB'))]
    df1  = df1[~df1['DSN'].str.contains(re.compile('DBRMLIB'))] 
    df1  = df1[~df1['DSN'].str.contains(re.compile('DCLGEN'))] 
    df1  = df1[~df1['DSN'].str.contains(re.compile('JCLMASTR'))] 
    
    df1  = df1[~df1['DSN'].str.contains(re.compile('NULLFILE'))] 
    
    
    df1  = df1[~df1['DDNAME'].str.contains(re.compile('STEPLIB'))] 
    df1  = df1[~df1['DDNAME'].str.contains(re.compile('MAIL'))] 
    
    
    df1  = df1[df1['PGM_NAME'].notnull()] 
    df1  = df1[~df1['PGM_NAME'].str.contains(re.compile('IDCAMS'))] 
    
    df1  = df1[df1['DISP1'].notnull()] 
    
    
    df1['DSN'].replace(to_replace="\.Y\d{7,7}", value=r".Y(XXXXXXX)", regex=True, inplace=True)
    df1['DSN'].replace(to_replace="\.F\d{7,7}", value=r".F(XXXXXXX)", regex=True, inplace=True)
    df1['DSN'].replace(to_replace="\.D\d{7,7}", value=r".D(XXXXXXX)", regex=True, inplace=True)
    
    
    df1['DSN'].replace(to_replace="\.Y\d{6,6}", value=r".Y(XXXXXX)", regex=True, inplace=True)
    df1['DSN'].replace(to_replace="\.F\d{6,6}", value=r".F(XXXXXX)", regex=True, inplace=True)
    df1['DSN'].replace(to_replace="\.D\d{6,6}", value=r".D(XXXXXX)", regex=True, inplace=True)
    df1['DSN'].replace(to_replace="\.G\d{6,6}", value=r".G(XXXXXX)", regex=True, inplace=True)
    
    df1['DSN'].replace(to_replace="\.Y\d{5,5}", value=r".Y(XXXXX)", regex=True, inplace=True)
    df1['DSN'].replace(to_replace="\.F\d{5,5}", value=r".F(XXXXX)", regex=True, inplace=True)
    df1['DSN'].replace(to_replace="\.D\d{5,5}", value=r".D(XXXXX)", regex=True, inplace=True)
    df1['DSN'].replace(to_replace="\.G\d{5,5}", value=r".G(XXXXX)", regex=True, inplace=True)
    
    df1['DSN'].replace(to_replace="\.Y\d{4,4}", value=r".Y(XXXX)", regex=True, inplace=True)
    df1['DSN'].replace(to_replace="\.F\d{4,4}", value=r".F(XXXX)", regex=True, inplace=True)
    df1['DSN'].replace(to_replace="\.D\d{4,4}", value=r".D(XXXX)", regex=True, inplace=True)
    df1['DSN'].replace(to_replace="\.G\d{4,4}", value=r".G(XXXX)", regex=True, inplace=True)
    
    df1['DSN'].replace(to_replace="\.F\d{3,3}", value=r".F(XXX)", regex=True, inplace=True)
    df1['DSN'].replace(to_replace="\.D\d{3,3}", value=r".D(XXX)", regex=True, inplace=True)
    
    
    df1['DSN'].replace(to_replace=r"\.Y\d{2,2}M\d{2,2}", value=r".Y(XX)M(XX)", regex=True, inplace=True)
    
    
    df1['DSN'].replace(to_replace=r"\.Y\d{2,2}", value=r".Y(XX)", regex=True, inplace=True)
    #df1['DSN'].replace(to_replace=r"\.F\d{2,2}", value=r".F(XX)", regex=True, inplace=True)
    #df1['DSN'].replace(to_replace=r"\.D\d{2,2}", value=r".D(XX)", regex=True, inplace=True)
    
    df1['DSN'].replace(to_replace="^\'", value=r"", regex=True, inplace=True)
    
    df1['DSN'].replace(to_replace="\'$", value=r"", regex=True, inplace=True)

    return df1



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


labels = [ 
'DSN',        
'JOBNAME',
'STEP_PROGR',
'PGM_NAME',
'N_PROGR',
'DDNAME',
'DISP1'
        ]
 





pathx = r'Software\BI_LUM'
namex = "RESULT_JOB_SQL"
tt = RegEntry(pathx,namex)
file_list = tt.list_entry()    


root = tk.Tk()
root.withdraw()
msg.showinfo("Information","You need to select a working directory ")
root.destroy()
#root.quit() 


root = tk.Tk() 
root.withdraw()
out_dir = askdirectory(title = 'Select Directory where file RESULT_JOB_SQL.CSV will be create (delete and recreate if already present ',initialdir=os.getcwd())
root.destroy()

if out_dir == "":
    sys.exit

out_file = out_dir + '/RESULT_JOB_SQL.CSV'
if os.path.exists(out_file):
    os.remove(out_file)
    

pathx = r'Software\BI_LUM'
namex = "RESULT_JOB_SQL"
tt = RegEntry(pathx,namex)
tt.add_entry(out_file)     


#--------------------------------------------------------------------------------
# for some reason it only works  (the event handler) before we call other tk.
user_name = enter_input('enter user name:','')   

user_password = enter_input('enter password:','hid')    



try:
    cnxn = pyodbc.connect('DSN=LOCDB2K;UID='+user_name+';PWD='+user_password+';CURRENTSCHEMA=RE')
except:
    root = tk.Tk()
    root.withdraw()
    msg.showinfo("Error","cant conect to db2 ")
    root.destroy   
    sys.exit()




cursor = cnxn.cursor()
cursor.execute(in_sql)

argx = (cursor,out_file)  
thread1 = threading.Thread(target=process_db2, args=argx)

root = tk.Tk() 
root.withdraw()
process_selection_with_progress_bar(thread1, rt)
root.destroy()

cursor.close()
cnxn.close()


root = tk.Tk()
root.withdraw()
msg.showinfo("Information",'RESULT are in : ' + out_file + '\n This will be used as hidden source by python : 2-jobiteration_sql_to_csv.py')
root.destroy

root = tk.Tk()
root.withdraw()
msg.showinfo("Information","Processing Transformation ")
root.destroy

out_file_transfrom = out_dir + '/RESULT_JOB_SQL_TRANSFORM.CSV'
if os.path.exists(out_file_transfrom):
    os.remove(out_file_transfrom)

df = pd.read_csv(out_file, names=labels  , skiprows = 1)
df1 = transform_df(df)

df1 = df1.sort_values( ['DSN','JOBNAME','STEP_PROGR','N_PROGR'])      
df1.to_csv(out_file_transfrom, mode = 'w',header=True, index = False)



print ('DONE')