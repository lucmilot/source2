# -*- coding: utf-8 -*-
"""
take /RESULT_JOB_SQL_TRANSFORM.CSV produced by jobiteration_sql_to_csv.py

transform it to filter out not related to handling of cobol program
also replace the generated year and date with xxxx

produce jobiteration_sql_job_trans.csv



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
from tkinter import messagebox

#get all the job info for all jobs formating YMMDD etc with FFFF

import threading


import pyodbc

import re



#get all the job info for all jobs formating YMMDD etc with FFFF

path = "C:\\Users\\XT21586\\Documents\\document\\_DOSSET\\lineage\\"


# in_file is produced by 2-jobiteration_sql_to_csv.py


root = tk.Tk() 
root.withdraw()
in_file = askopenfilename(parent=root)
root.destroy()

out_dir = r"/".join(in_file.split(r"/")[0:-1])

out_file = out_dir + '/RESULT_JOB_SQL_TRANSFORM.CSV'




labels = [ 
'DSN',        
'JOBNAME',
'STEP_PROGR',
'PGM_NAME',
'N_PROGR',
'DDNAME',
'DISP1'
        ]

df = pd.read_csv(in_file, names=labels  , skiprows = 1)
#df = dfr.drop(columns = ['xx'],axis = 1)


#282115
#pd.DataFrame[DataFrame['columnName'].str.contains(re.compile('regex_pattern'))]


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





out_file = path+'jobiteration_sql_job_trans.csv'


if os.path.exists(out_file):
    os.remove(out_file)


df1 = df1.sort_values( ['DSN','JOBNAME','STEP_PROGR','N_PROGR'])      
df1.to_csv(out_file, mode = 'w',header=True, index = False)

print( 'calling excel....')

excel = win32.gencache.EnsureDispatch('Excel.Application')
wb = excel.Workbooks.Open(out_file)
excel.Visible = True
excel.ActiveSheet.Columns.AutoFit()


print ('DONE')