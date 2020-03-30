# -*- coding: utf-8 -*-
r"""

WITH PYTHON 
python DOCET_JOB_PGM_IN_OUT_REFRESH.py  -o C:\Users\XT21586\Documents\document\_DOSSET\_promoted_V2\result -u cndwxxx -p xxxxxxxx

WITH EXE:
TO COMPILE
once an exec modul is created with pyinstaller    
slow:   pyinstaller DOCET_JOB_PGM_IN_OUT_REFRESH.py -F  slow because of big EXE take 90 second to scan with antiviruse
onedir allow to put other exe in the same dir   ???
pyinstaller DOCET_JOB_PGM_IN_OUT_REFRESH.py --onedir    to be run on the directory were the ...py is 
    -- this will create a full directory structure in \DOCET_JOB_PGM_IN_OUT_REFRESH
    -----on the first program that is compiled  rename the structue to \DOCET 
       ----- on other program that are compile  
            -- copy OTHER_PROGRAM.exe from \OTHER_PROGRAM into \DOCET 
            -- and  copy OTHER_PROGRAM.exe.manifest from \OTHER_PROGRAM into \DOCET 

TO EXECUTE use the following .BAT template :
--------
REM     : the program DOCET_JOB_PGM_IN_OUT_REFRESH.exe  was put in the lan \\MTL-HQ-FTP\PUB  here the mapping drive is G:  
REM -d  : directory where the result file will be created
REM -f  : result file
REM -u  : user to access DB2K
REM -p  : password to acces DB2K



@echo off
G:\temp\Luc-pgm\DOCET_JOB_REFRESH\DOCET_JOB_PGM_IN_OUT_REFRESH.exe ^
-d C:\Users\XT21586\Documents\document\_DOSSET\_promoted_V2\result ^
-f DOCET_JPIO ^
-u cndwxxx ^
-p xxxxxxx

pause
---------



"""
import win32com.client as win32

import os, sys, getopt

import time

from time import gmtime, strftime

import pyodbc
import numpy as np
import pandas as pd

import re




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


def process_db2(cursor) :

    df_out = pd.DataFrame()
    line_count = 0

    while True:
        rows = cursor.fetchmany(10000)
    
        if len(rows) == 0:
                break
            
        df = pd.DataFrame.from_records(rows, columns=labels)
        df_out = pd.concat([df_out, df])

        line_count += len(rows)
        #print(line_count, 'memory usage: ', '{0:.4g}'.format(memory_usage_psutil()) )
        print(line_count)


    df_out.sort_values( ['JOBNAME','STEP_PROGR'])      
    
    return df_out
    




def transform_df(df):  
    print('processing transformation ...')
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

def show_odbc_sources():
    
    src = pyodbc.dataSources()
    dsns = list(src.keys())
    dsns.sort()
    sl = []
    for dsn in dsns:
        sl.append('%s [%s]' % (dsn, src[dsn]))
    print('\n'.join(sl))
     

def main_process():   
    global out_file, username, password
    

    tt = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    tt = tt.replace(" ", "_")
    tt = tt.replace(":", "_")
    
  
    out_file_csv = out_file+".csv"
    if os.path.exists(out_file_csv):
        out_file_2_csv  = out_file + "_" +tt+".csv" 
        os.system('copy '+ out_file_csv + " " + out_file_2_csv)        
        os.remove(out_file_csv)	
        

    print ('connecting to DB2')    
    
    try:
        cnxn = pyodbc.connect('DSN=LOCDB2K;UID='+username+';PWD='+password+';CURRENTSCHEMA=RE')
    except pyodbc.Error as ex:
        sqlstate = ex.args[1]
        print (sqlstate)
        show_odbc_sources()

        sys.exit()
    cursor = cnxn.cursor()
    
    print ('send execute statement')   
    cursor.execute(in_sql)
    
    df_1 = process_db2(cursor)
    
    cursor.close()
    cnxn.close()
    
    df_2 = transform_df(df_1)
    
    df_out = df_2.sort_values( ['DSN','JOBNAME','STEP_PROGR','N_PROGR']) 
    
    df_out.to_csv(out_file_csv, mode = 'w',header=True, index = False)




def main_in(argv):
    global out_file, username, password    
    
    wrk_dir = ''
    out_file_1 = ''
    username = ''
    password = ''
    try:
        opts, args = getopt.getopt(argv,"hw:o:u:p:",["help","wrkd=","outf=","usnam=","passw="])
    except getopt.GetoptError:
        print ('DOCET_JOB_PGM_IN_OUT_REFRESH.py -w <workingdir> -o <outfilename> -u <username) -p <password>')
        sys.exit(2)
        
     
    for opt, arg in opts:
        if opt == '-h':
            print ('DOCET_JOB_PGM_IN_OUT_REFRESH.py -w <workingdir> -o <outfilename> -u <username) -p <password>')
            sys.exit()
        elif opt in ("-w", "--wrkd"):
            wrk_dir = arg
        elif opt in ("-o", "--outf"):
            out_file_1 = arg            
        elif opt in ("-u", "--usnam"):
            username = arg
        elif opt in ("-p", "--passw"):
            password = arg         

    out_file = wrk_dir + out_file_1

    #for testing
    #wrk_dir= r"C:\Users\XT21586\Documents\document\_DOSSET\_promoted_V2\result\"
    #username = "cndwlmm"
    #password = "lcjcmhf3"    
    #out_file = wrk_dir + "DOCET_JPIO"

if __name__ == "__main__":
    
    main_in(sys.argv[1:])
    #out_dir = r"C:\Users\XT21586\Documents\document\_DOSSET\_promoted_V2\result\"
    #sername = "cndwlmm"
    #password = "lcjcmhfx"    
    
    print (out_file)
    
    print (username)
  
    main_process()   


   
   