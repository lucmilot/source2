# -*- coding: utf-8 -*-
"""
INPUT: Grab_all_file_PO_MBR_...


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


#dont keep line number
# we use input[0:72]  
#pat1 = re.compile(r"(^\w{6})",flags = re.MULTILINE)

#dont line suffix  number
# we use input[0:72]  
#pat2 = re.compile(r"(\s\d{8}$)",flags = re.MULTILINE)

#dont line suffix like CL*64
# we use input[0:72]  
#pat3 = re.compile(r"(\b\w*\**\d+$)",flags = re.MULTILINE)

#  ¦  at the end or any one charatter field
pat4 = re.compile(r"(\s¦\s*$)",flags = re.MULTILINE)


#dont keep comment line
pat_comment = re.compile(r"(^\s{6}\*)") # this is used line per line

pat_identification  = re.compile('IDENTIFICATION DIVISION',flags = re.DOTALL)

pat_exec_sql = re.compile('EXEC SQL',flags = re.DOTALL)   

pat_SIUD = re.compile(".*(?=SELECT|INSERT|DELETE|UPDATE).*",flags = re.DOTALL)
pat_IUD = re.compile(".*(?=INSERT|DELETE|UPDATE).*",flags = re.DOTALL)
pat_S = re.compile(".*(?=SELECT).*",flags = re.DOTALL)

pat_EXEC_BLK = re.compile("(?:EXEC SQL)(.+?)(?:END-EXEC)",flags = re.DOTALL)

pat_not_blank_line = re.compile(r"(\S+)")  #any non white space character 

pat_sql_comment = re.compile(r"(^\*)")  #* as first charater 



def call_cobol_sql(file_sel,mbr_sel):  

    global l_acum, search_identification
    def append_line(input):
        global l_acum, ix
        
        if re.search(pat_comment,input )  is not None : 
            pass
        else : 
            l_acum.extend([input])
            
    def call_sqeeze_sql(x):         
      
        x_1 = ''
        s = io.StringIO(x)
        sw1 = 0
        for line in s:
 
            if re.search(pat_not_blank_line,line) is not None and re.search(pat_sql_comment,line) is None :   
                if sw1 == 0 :
                    sw1 = 1
                    for i in range(len(line)):
                        if line[i] != ' ' : break
                    shift_ix = i
          
                x_1 = x_1  + line[shift_ix:] 
                
        return x_1                
 
    #lambda x: x*10 if x<2 else (x**2 if x<4 else x+10)

    l_acum = []
    sess.cwd("'" + file_sel + "'") 
    sess.retrlines('RETR ' + mbr_sel, append_line)

    #np.array([ x[6:72] if len(x)> 72  else x[6:] for x in l_acum ])  to get rid of first 6 and last 8 column
    # len(x) > 0  mean line is not empty, in that case we dont take only line starting with  != '*'  (x[0] is first character)
    # when len(x) = 0  we put false  i.e (1 == 0)
    # once the * got process we use x[1:] to get rid  of first column
    # we leave in separate line , because it is easyier to understant and performance is still good
    t1 =np.array([ x[6:72] if len(x)> 72  else x[6:] for x in l_acum ])
    t2 = [(x[0] != '*') if (len(x) > 0) else (1 == 0) for x in t1 ]
    t3 = t1[t2]
    l_acum_1 = [x[1:] for x in t3]
    acum_txt = "\n".join(l_acum_1)


    return_list = []   
    if re.search(pat_identification,acum_txt)  is None  or re.search(pat_exec_sql,acum_txt) is None:
        return return_list      

    #acum_txt = re.sub(pat1, '      ', acum_txt)    #dont keep line number
    #acum_txt = re.sub(pat2, '        ', acum_txt)  #dont line suffix  number
    #acum_txt = re.sub(pat3, '', acum_txt)  #dont line suffix  number
    acum_txt = re.sub(pat4, '', acum_txt)  #dont line suffix  with ¦

    list1  = []  
    list2 = re.findall(pat_EXEC_BLK , acum_txt)  
    

    for x in list2:
        x1 = ''
        if re.search(pat_IUD,x) is not None and re.search(pat_S,x)  is not None: 
            x1 = "??? IUD and SELECT - still to code ???"
        
        elif re.search(pat_SIUD,x) is not None :
            x1 = call_sqeeze_sql(x)       
         
        if x1 != '':    
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


def write_buf():
    global buf_write_cnt , tot_PO_mbr_1, tot_PO_mbr_2,  mbr_list_1 , arrx_PO_MBR  , arry_PO_MBR, df_out_mbr, first_sw   
    buf_write_cnt = 0
    if len(arry_PO_MBR) > 0 :
        if first_sw == 0 :
            first_sw = 1
            df_out_mbr = pd.DataFrame(arry_PO_MBR, columns= ['file','mbr'] +  ["sql"+str(i) for i in range(50)])
        else:
            df_out_mbr.to_csv(out_file,mode = 'a',header=True, index = False)  
                
        tot_PO_mbr_1 = []
        tot_PO_mbr_2 = []        
        mbr_list_1 = []
        arrx_PO_MBR = np.array([],dtype=np.str)
        arry_PO_MBR = np.array([],dtype=np.str) 


rt = tk.Tk()
rt.withdraw()
msg.showinfo("Information","You need to select the proper Grab_all_file_PO_MBR_... ")
rt.destroy()
#root.quit() 


rt = tk.Tk() 
rt.withdraw()
in_file = askopenfilename(parent=rt)
rt.destroy()

#in_file = r'C:/Users/XT21586/Documents/document/_DOSSET/_promoted/result/Grab_all_file_PO_MBR_CHANGEI.CNDWPROD.COBSRCE.csv'
out_dir = r"/".join(in_file.split(r"/")[0:-1])
out_file = out_dir + "/SQL_FULL_" + in_file.split(r"_")[-1:][0]

rt = tk.Tk()
rt.withdraw()
msg.showinfo("Information","The result will be put in: " + out_file)
rt.destroy()

if os.path.exists(out_file):
    os.remove(out_file)	            



labels = ['Lv123','Name','VV.MM','Created','Changedate','Changetime','Sze','Init','Mod','Id']
df_seed = pd.read_csv(in_file , names=labels , skiprows = 1)
df_seed = df_seed.sort_values( ['Lv123','Name'])      



if len(df_seed) == 0 :
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


tot_lst_1 = []          
tot_lst_2 = []  
tot_lst_3 = []
lv123_prev = ''
first_sw = 0
buf_write_cnt_limit = 100
buf_write_cnt = 0
write_cnt = 0
for index, row in df_seed.iterrows():
    
    lv123 = row['Lv123']
    mbr = row['Name']
    
    if lv123 != lv123_prev :
        try:
            sess.cwd("'" + lv123 + "'")
            #file_list = sess.nlst()
            f = io.StringIO()
            with redirect_stdout(f):
                sess.dir()
        except:
            print (lv123 + ' :not found or no permission')
            continue    
            
            
    hit_list = call_cobol_sql(lv123,mbr)   
    
    
    
    
    if len(hit_list) == 0:
        continue
    
    if len(tot_lst_1) == 0 : 
        tot_lst_1 = [lv123]          
        tot_lst_2 = [mbr]  
        tot_lst_3 = [hit_list]
    else :
        tot_lst_1.extend([lv123]) 
        tot_lst_2.extend([mbr]) 
        tot_lst_3.extend([hit_list])  


    buf_write_cnt = buf_write_cnt + 1
    write_cnt = write_cnt + 1
    print (buf_write_cnt,  write_cnt)
    if buf_write_cnt > buf_write_cnt_limit :
        buf_write_cnt = 0
        c1 = np.array(tot_lst_1)[: , np.newaxis]
        c2 = np.array(tot_lst_2)[: , np.newaxis]
        c3 = np.array(tot_lst_3)
        arrx = np.hstack([c1,c2,c3])
        df_out_mbr = pd.DataFrame(arrx)
        df_out_mbr.columns = ['file','mbr'] +  ["sql"+str(i) for i in range(50)]
        
        if first_sw == 0:
            first_sw = 1
            df_out_mbr.to_csv(out_file,mode = 'w',header=True, index = False)
        else :
            df_out_mbr.to_csv(out_file,mode = 'a',header=False, index = False)
            
        tot_lst_1 = []          
        tot_lst_2 = []  
        tot_lst_3 = []

    #print('test')
    
    

if buf_write_cnt > 0 :
    c1 = np.array(tot_lst_1)[: , np.newaxis]
    c2 = np.array(tot_lst_2)[: , np.newaxis]
    c3 = np.array(tot_lst_3)
    
    
    
    
    
    arrx = np.hstack([c1,c2,c3])
    df_out_mbr = pd.DataFrame(arrx)
    df_out_mbr.columns = ['file','mbr'] +  ["sql"+str(i) for i in range(50)]
    
    if first_sw == 0:
        first_sw = 1
        df_out_mbr.to_csv(out_file,mode = 'w',header=True, index = False)
    else :
        df_out_mbr.to_csv(out_file,mode = 'a',header=False, index = False)

sess.quit


