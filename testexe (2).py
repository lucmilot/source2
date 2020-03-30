# -*- coding: utf-8 -*-
r"""





python testexe.py  -o C:\\Users\\XT21586\\Documents\\document\\_DOSSET\\_promoted_V2\\result -u cndwlmm -p lcjcmhf9

once an exec modul is created with pyinstaller
testexe.exe  -o C:\\Users\\XT21586\\Documents\\document\\_DOSSET\\_promoted_V2\\result -u cndwlmm -p lcjcmhf9

"""

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

 

def main_process():   
    global out_dir, username, password
    

    tt = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    tt = tt.replace(" ", "_")
    tt = tt.replace(":", "_")
    
  
    out_file = out_dir+"\DOCET_JOB_SQL.csv"
    if os.path.exists(out_file):
        out_file_2  = out_dir+"\DOCET_JOB_SQL_BK_ON_"+tt+".csv" 
        os.system('copy '+ out_file + " " + out_file_2)        
        os.remove(out_file)	
        
    out_file_temp = out_dir+"\DOCET_JOB_SQL_TEMP.csv"
    if os.path.exists(out_file_temp): 
        os.remove(out_file_temp)	        
        
        
    try:
        cnxn = pyodbc.connect('DSN=LOCDB2K;UID='+username+';PWD='+password+';CURRENTSCHEMA=RE')
    except:
        print ("Error","cant conect to db2 ")
        sys.exit()
    cursor = cnxn.cursor()
    cursor.execute(in_sql)
    
    df_1 = process_db2(cursor)
    
    cursor.close()
    cnxn.close()
    
    df_2 = transform_df(df_1)
    
    df_out = df_2.sort_values( ['DSN','JOBNAME','STEP_PROGR','N_PROGR']) 
    
    df_out.to_csv(out_file, mode = 'w',header=True, index = False)




def main_in(argv):
    global out_dir, username, password    
    
    out_dir = ''
    username = ''
    password = ''
    try:
        opts, args = getopt.getopt(argv,"ho:u:p:",["help","odirn=","usnam=","passw="])
    except getopt.GetoptError:
        print ('DOCET_ITERATION_REFRESH.py -o <outdirname> -u <username) -p <password>')
        sys.exit(2)
        
     
    for opt, arg in opts:
        if opt == '-h':
            print ('DOCET_ITERATION_REFRESH.py -o <outdirname> -u <username> -p <password>')
            sys.exit()
        elif opt in ("-o", "--odirn"):
            out_dir = arg
        elif opt in ("-u", "--usnam"):
            username = arg
        elif opt in ("-p", "--passw"):
            password = arg         

    #for testing
    #out_dir = r"C:\Users\XT21586\Documents\document\_DOSSET\_promoted_V2\result"
    #username = "cndwlmm"
    #password = "lcjcmhf9"    


if __name__ == "__main__":
    
    main_in(sys.argv[1:])
    
    print(out_dir)
    print(username)
    print(password)    


        
    main_process()   


   
   