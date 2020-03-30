# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pyodbc
import pandas as pd

import os, sys


import win32com.client as win32

import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory
import tkinter.ttk as ttk
from tkinter import messagebox

#get all the job info for all jobs formating YMMDD etc with FFFF

import threading

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


    df_out.sort_values( ['JOBNAME','STEP_PROGR'])      
    df_out.to_csv(out_file, mode = 'w',header=True, index = False)
    

# Function to check state of thread1 and to update progressbar #
def process_selection_with_progress_bar(thread, root):
    # starts thread #
    thread.start()
    
    root.title("Progressbar ------------")
    root.config(bg = '#F0F0F0')  
                
    canvas = tk.Canvas(root, relief = tk.FLAT, background = "#D2D2D2",
                                            width = 800, height = 20)
                       
    pb1 = ttk.Progressbar(canvas, orient=tk.HORIZONTAL,
                                      length=800, mode="indeterminate"                                     
                                      )

    canvas.create_window(1, 1, anchor=tk.NW, window=pb1)
    canvas.grid()

    # places and starts progress bar #
    pb1.pack()
    pb1.start()

    # checks whether thread is alive #
    while thread.is_alive():
        root.update()
        pass

    # once thread is no longer active, remove pb1 and place the '100%' progress bar #
    pb1.destroy()

    root.destroy()
    
    return 



root = tk.Tk() 
root.withdraw()
#out_file = askopenfilename(parent=root)
out_dir = askdirectory(title = 'Select Directory where file RESULT_JOB_SQL.CSV will be create (delete and recreate if already present ')

print (out_dir)

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


cnxn = pyodbc.connect('DSN=LOCDB2K;UID=CNDWLMM;PWD=LCJCMHF9;CURRENTSCHEMA=RE')
cursor = cnxn.cursor()

cursor.execute(in_sql)

argx = (cursor,out_file)

#  to debug comment out this        
thread1 = threading.Thread(target=process_db2, args=argx)
pg = tk.Tk()
process_selection_with_progress_bar(thread1, pg)
print('tata')
pg.mainloop()  


#  to debug use this    
#process_db2(argx[0],argx[1])


cursor.close()
cnxn.close()

messagebox.showinfo("Information","'RESULT are in : ' + out_file + ' \n' +  'This will be used as hidden source by python : 2-jobiteration_sql_to_csv.py' " )



print ('DONE')