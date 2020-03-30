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




#dont keep line number
pat1 = re.compile(r"(^\w{6})",flags = re.MULTILINE)

#dont line suffix  number
pat2 = re.compile(r"(\s\d{8}$)",flags = re.MULTILINE)

#dont line suffix like CL*64
pat3 = re.compile(r"(\b\w*\**\d+$)",flags = re.MULTILINE)

#dont keep comment line
pat_comment = re.compile(r"(^\s{6}\*)") # this is used line per line

pat_identification  = re.compile('IDENTIFICATION DIVISION',flags = re.DOTALL)

pat_exec_sql = re.compile('EXEC SQL',flags = re.DOTALL)   

pat_SIUD = re.compile(".*(?=SELECT|INSERT|DELETE|UPDATE).*",flags = re.DOTALL)

pat_EXEC_BLK = re.compile("(?:EXEC SQL)(.+?)(?:END-EXEC)",flags = re.DOTALL)

pat_not_blank_line = re.compile(r"(\S+)")  #any non white space character 

pat_sql_comment = re.compile(r"(^\*)")  #* as first charater 


def call_cobol_sql(file_sel,mbr_sel):  

    global acum_txt, search_identification
    def append_newline(input):
        global acum_txt, ix
        if re.search(pat_comment,input ) : 
            pass
        else :
            acum_txt = acum_txt + input + "\n"  
            
    def call_sqeeze_sql(x):         
      
        x_1 = ''
        s = io.StringIO(x)
        sw1 = 0
        for line in s:
            if re.search(pat_not_blank_line,line) and not re.search(pat_sql_comment,line) :   
                if sw1 == 0 :
                    sw1 = 1
                    for i in range(len(line)):
                        if line[i] != ' ' : break
                    shift_ix = i
          
                x_1 = x_1  + line[shift_ix:] 
                
        return x_1                
 


    acum_txt = ''
    sess.cwd("'" + file_sel + "'")
    print(file_sel, mbr_sel)        
    sess.retrlines('RETR ' + mbr_sel, append_newline)

      

    return_list = []   
    if re.search(pat_identification,acum_txt)  is None  or re.search(pat_exec_sql,acum_txt) is None:
        return return_list      

    acum_txt = re.sub(pat1, '      ', acum_txt)    #dont keep line number
    acum_txt = re.sub(pat2, '        ', acum_txt)  #dont line suffix  number
    acum_txt = re.sub(pat3, '', acum_txt)  #dont line suffix  number

    list1  = []  
    list2 = re.findall(pat_EXEC_BLK , acum_txt)   
    for x in list2:
        if re.search(pat_SIUD,x) : 
  
            x1 = call_sqeeze_sql(x)       
            
            if len(list1) == 0 : 
                list1 = [x1]
            else :
                list1.extend([x1])           
 
 
    if len(list1) > 0 :  
        for i in range(50) :   
            if i < len(list1) :
                return_list.append(list1[i])
            else:
                return_list.append('')
            
    return return_list 


#-----------------------------------------------------------



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
msg.showinfo("Information","You need to select the proper Grab_all_file_PO_MBR_... ")
rt.destroy()
#root.quit() 


rt = tk.Tk() 
rt.withdraw()
in_file = askopenfilename(parent=rt)
rt.destroy()


out_dir = r"/".join(in_file.split(r"/")[0:-1])


rt = tk.Tk()
rt.withdraw()
msg.showinfo("Information","The result will be put in: " + out_dir + "/Grab_all_file_SQL_FULL_...  ")
rt.destroy()

out_file_SQL_FULL = out_dir + '/Grab_all_file_SQL_FULL_xxx.csv'
if os.path.exists(out_file_SQL_FULL):
    os.remove(out_file_SQL_FULL)	            


path = os.getcwd()        
in_file = path+"\\input\\"+'Grab_all_file_with_FTP.csv'


labels = ['Lv123''Name','VV.MM','Created','Changedate','Changetime','Sze','Init','Mod','Id']

df_seed = pd.read_csv(in_file , names=labels , skiprows = 1)
#df_seed.fillna('', inplace=True)
# \w Any word character (letter, number, underscore )


List_Lv123 = df_seed['Lv123'].values.tolist()

if len(List_Lv123) == 0 :
    print( "nothing selected in input : " + in_file)
    sys.exit(0)



#-----------------------------------------------------------

get_credential()

try:
    sess = ftplib.FTP('imftpb',user_name,user_password)
except:
    rt = tk.Tk()
    rt.withdraw()
    msg.showinfo("Error","cant conect to FTP ")
    rt.destroy   
    sys.exit()



for lv1 in List_Lv123 :


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

            
        chnk = 50
        bdr1 = 0
        bdr2 = bdr1 + chnk
    
        # we process for a maximum of chnk * 100,  ex chnk 1000  >> 100,000 mbr 
        #for ic in range(100):
        for ic in range(2):
            #cpx = call_process_mbr()
            

            tot_PO_mbr_1 = []
            tot_PO_mbr_2 = []        
              
            mbr_list_1 = []
        
            arrx_PO_MBR = np.array([],dtype=np.str)
            arry_PO_MBR = np.array([],dtype=np.str) 
        
        
            bdr2x = min(len(mbr_list), bdr2)
        
            hit_sw = 0
            for mbr_sel in mbr_list[bdr1:bdr2x]:                    
                hit_list = call_cobol_sql(file_sel,mbr_sel)     
               
                if len(hit_list) > 0:
                    hit_sw = 1
                    mbr_list_1.extend([mbr_sel])
                    if len(tot_PO_mbr_2) == 0 : 
                        tot_PO_mbr_1 = [mbr_sel]  
                        tot_PO_mbr_2 = [hit_list]
                    else :
                        tot_PO_mbr_1.extend([mbr_sel]) 
                        tot_PO_mbr_2.extend([hit_list])  
             
            
            if hit_sw == 1 : 
                c1 = np.array([file_sel] * len(tot_PO_mbr_1))[: , np.newaxis]
                c2 = np.array(tot_PO_mbr_1)[: , np.newaxis]
                c3 = np.array(tot_PO_mbr_2)
                
                arrx_PO_MBR = np.hstack([c1,c2,c3])
            
            
                if len(arry_PO_MBR) == 0 : 
                    arry_PO_MBR = arrx_PO_MBR 
                else :
                    arry_PO_MBR = np.vstack([arry_PO_MBR,arrx_PO_MBR ]) 
            
            
                if len(arry_PO_MBR) > 0 :
                    df_out_mbr = pd.DataFrame(arry_PO_MBR, columns= ['file','mbr'] +  ["sql"+str(i) for i in range(50)])
            
                    df_out_mbr.to_csv(out_file_PO_MBR,mode = 'a',header=True, index = False)
                        
            if bdr2x == len(mbr_list) :
                #return 'complete'
                cpx = 'complete'
            else:
                #return 'not complete'   
                cpx = 'not complete'
            
            
            
            
            
            
            
            
            
            bdr1 = bdr1 + chnk
            bdr2 = bdr2 + chnk         
            if cpx == 'complete' : break



sess.quit

acum_txt = '''

                 SELECT 'Y'
                 INTO :FULL-DISPLAY-FLAG
                 FROM VREFCODE
                 WHERE REF_CD_TYPE        = 'DB'
                   AND REF_CD_VAL         = :FULL-COMPILED-NAME
                   AND REF_CD_DSC_ENG     = 'DEBUG ON'
                 WITH UR
              
 UPDATE VRATAMNT
           SET SHIP_COND_SET_ID = :I-SHIP-COND-SET-ID
             , AUDT_UPD_TS      = :I-AUDT-UPD-TS
             , AUDT_UPD_USE_ID  = :I-AUDT-UPD-USE-ID
             , AUDT_UPD_PGM_ID  = :I-AUDT-UPD-PGM-ID
           WHERE RATE_ID          = :SQL-RATE-ID
             AND RATE_AMT_POST_TS = :SQL-RATE-AMT-POST-TS
             AND SHIP_COND_SET_ID = :W-VRATAMNT.SHIP-COND-SET-ID
*******    WHERE CURRENT OF READNEXT_VRATAMNT
           

'''
acum_txt_buf = acum_txt_1

acum_txt_1 = ''
s = io.StringIO(acum_txt)
for line in s:
    acum_txt_1 = acum_txt_1  + line
    input ('ddd')



