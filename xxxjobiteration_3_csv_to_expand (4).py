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



#dfx = df1[df1['DSN'].str.contains(re.compile("\.\w\d{5,7}"))] 

"""
dfx  = df1[df1['DSN'].str.contains(re.compile(r"Y\(XX\)"))] 
dfx  = df1[df1['DSN'].str.contains(re.compile(r"F\(XXXXXXX\)"))] 


ex: \1 refers to first hit group  ,  a group is defined with (...)
re.sub(r"\.(00|11)\.", r"X\1X", ".00..0..11.")

ex \b word boundary
s = 'Tahiti Tahiti Atoll'
result = re.findall(r'\b(\w+)\b\s+\1\b', s)

s = 'Tahiti xxx Atoll'
ttt = re.match(r"(?:Tahiti)(\w+)(?:Atoll)", s).group(1)


try:
    ttt = re.match(r"(?:Tahiti)(.+)(?:Atolddl)", s).group(1)
except (TypeError, AttributeError):
    ttt = ""

ttt = "" 
try:
    ttt = re.match(r"(?:Tahiti)(.+)(?:Atoll)", s).group(1)
except (TypeError, AttributeError):
    ttt = ""
    
    
in1 = '''select ddafa

from '''
t1 = "" 
try:
    t1 = re.match(r"(?:select)(.*)(?:from)", in1,re.DOTALL).group(1)
except (TypeError, AttributeError):
    t1 = ""    
    

\s?  0 or one white space char

line = "President [P] Barack Obama [/P] met Microsoft founder [P] Bill Gates [/P], yesterday."
ttt = re.findall('\[P\]\s?(.+?)\s?\[\/P\]', line)

dfx = pd.DataFrame(['$40,000.32*','$40000 conditions attached'], columns=['pricing'])
dfx['pricing'].replace(to_replace="\$([0-9,\.]+).*", value=r"\1", regex=True, inplace=True)
print(dfx)

non capturing group  ?:    group(0) return entire match 
>>> print (re.match(r"(?:aaa)(_bbb)", string1).group(0))
aaa_bbb
>>> print (re.match(r"(?:aaa)(_bbb)", string1).group(1))
_bbb


"""


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