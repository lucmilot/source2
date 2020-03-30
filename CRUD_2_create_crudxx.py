# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 06:46:00 2018

@author: xt21586
"""



import win32com.client as win32

import os, sys, getopt

import time

from time import gmtime, strftime

import pyodbc
import numpy as np
import pandas as pd

#aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
#aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
import re

import ftplib

from contextlib import redirect_stdout

import io

import sqlparse


#from sqlparse.sql import IdentifierList, Identifier
#from sqlparse.tokens import Keyword, DML


#    at the end or any one charatter field


#from sqlparse.tokens import Keyword, DML
#from sqlparse.tokens import Keyword, DML


#from sqlparse.tokens import Keyword, DML
#pat4 = re.compile(r"(\s|\s*$)",flags = re.MULTILINE)



#dont keep comment line
pat_comment = re.compile(r"(^\s{6}\*)") # this is used line per line

pat_identification  = re.compile('IDENTIFICATION DIVISION',flags = re.DOTALL)

pat_exec_sql = re.compile('EXEC SQL',flags = re.DOTALL)   

pat_SIUD = re.compile(".*(?=SELECT|INSERT|DELETE|UPDATE).*",flags = re.DOTALL)
pat_IUD = re.compile(".*(?=INSERT|DELETE|UPDATE).*",flags = re.DOTALL)
pat_S = re.compile(".*(?=SELECT).*",flags = re.DOTALL)

pat_UNION = re.compile("(?:^UNION$|^UNION\s|\sUNION$|\sUNION\s)",re.MULTILINE)    

pat_ALL_str_alone = re.compile("(?:^ALL$|^ALL\s*$)",re.MULTILINE)    

pat_EXEC_BLK = re.compile("(?:EXEC SQL)(.+?)(?:END-EXEC)",flags = re.DOTALL)

pat_not_blank_line = re.compile(r"(\S+)")  #any non white space character 

pat_sql_comment = re.compile(r"(^\*)")  #* as first charater 

pat_newline = re.compile("\n",flags = re.DOTALL)

pat_strt_newline = re.compile("^\n",flags = re.DOTALL)

pat_select_overall = re.compile(".*(?=SELECT).*",flags = re.DOTALL)

pat_view = re.compile("(^(V|T)\S*(\s|$))|(^\S*\.(V|T)\S*(\s|$))",re.IGNORECASE)
pat_view1 = re.compile("((V|T)\S*(\s|$))",re.IGNORECASE)
pat_FROM = re.compile("^FROM$",re.IGNORECASE)
pat_WHERE = re.compile("^WHERE$",re.IGNORECASE)
pat_SELECT = re.compile("^SELECT$",re.IGNORECASE)
pat_UPDATE = re.compile("^UPDATE",re.IGNORECASE)
pat_INSERT = re.compile("^INSERT",re.IGNORECASE)
pat_DELETE = re.compile("^DELETE",re.IGNORECASE)
pat_ON = re.compile("^ON$",re.IGNORECASE)


excel = win32.gencache.EnsureDispatch('Excel.Application')     

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
       

def call_cobol_sql(file_sel,mbr_sel,sess):  

    global l_acum, search_identification

    def append_line(input):
       
        if re.search(pat_comment,input )  is not None : 
            pass
        else : 
            l_acum.extend([input])

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
    
    
    #acum_txt = re.sub(pat4, '', acum_txt)  #dont line suffix  with 

    list1  = []  
    list2 = re.findall(pat_EXEC_BLK , acum_txt)  
    
 
    for x in list2:
        x1 = ''

        if (("INSERT" in x) or ("UPDATE" in x) or ("DELETE" in x))  and ("SELECT" in x) : 
            
            # return -1 when not found
            
            pos_sel = x.find('SELECT')  # always present since and ("SELECT" in x)
            
            pos_upd = x.find('UPDATE')
            if pos_upd < 0 : pos_upd = 9999

            pos_ins = x.find('INSERT')
            if pos_ins < 0 : pos_ins = 9999
            
            pos_del = x.find('DELETE')      
            if pos_del < 0 : pos_del = 9999            
            
            #is select before update we let thru,  if not we take the update in one slot and the select in an other
            
            if (pos_sel > pos_upd) | (pos_sel > pos_ins) | (pos_sel > pos_del)  :
                x1 = "??? IUD and S - still to code ???"
            else:
                x1 = call_sqeeze_sql(x)                 

        
        elif (("INSERT" in x) or ("UPDATE" in x) or ("DELETE" in x) or ("SELECT" in x)) :
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


#------------------------------------------------------------------------


def parse_gen(tree_list,lvl):
    global keep, full_keep, ix_keep , from_sw   
    if len(tree_list) == 0 : 
        if lvl == 0 :
            return
        else : 
            full_keep[lvl] = tree_list 
            yield from parse_gen(keep[lvl-1],lvl-1 ) 

    if len(keep[lvl]) == 0 :
        return
    #print('LEVEL:' + str(lvl) + " : ")
    #print(keep[lvl]) 
    #print(keep[lvl][0])
    #print(type(keep[lvl][0]).__name__)
    #print(full_keep[lvl])



    if keep[lvl][0].is_group: 
        #print(keep[lvl]) 
        keepx = keep[lvl][0]
        keep[lvl] = keep[lvl][1:]
        # when keep[lvl1] is empty the next 'yield from'  will hit len(tree_list) == 0
        #  and calling yield from parse_gen(keep[lvl-1],lvl-1 )
        #  the lvl-1 is pointing to the next token to execute
        ix_keep[lvl] = ix_keep[lvl] + 1
        
        #print(type(keepx).__name__)
        #print(keepx)

        if type(keepx).__name__ == 'Identifier':           
        #if isinstance(keepx, Identifier):      
            if (re.search(pat_view ,str(keepx)) is not None) and (from_sw == 1):                 
                if (re.search(pat_view ,str(keepx)) is not None) and (from_sw == 1):  
                    yield str(re.findall(pat_view1 ,str(keepx))[0][0]).strip()               
            #yield str(keepx)   
            yield from parse_gen(keep[lvl],lvl )
            
        elif type(keepx).__name__ == 'IdentifierList':
        #elif isinstance(keepx, IdentifierList):            
            ##print ('idendifier list length\n')
            for t in keepx.get_identifiers():
                #print(t)
                if (re.search(pat_view ,str(t)) is not None) and (from_sw == 1):  
                    yield str(re.findall(pat_view1 ,str(t))[0][0]).strip()    
                #yield str(t)
            yield from parse_gen(keep[lvl],lvl )   
                
        elif type(keepx).__name__ == 'Where':
            #yield str(keepx)   
            from_sw = 0
            ix_keep[lvl+1] = 0
            keep[lvl+1] = keepx.tokens
            ##print ('going to group : ' + str(lvl+1))
            yield from parse_gen(keep[lvl+1],lvl+1 )             

        #Comparison, Operation, Parenthesis
        elif type(keepx).__name__ == 'Comparison':
            #yield str(keepx)   
            yield from parse_gen(keep[lvl],lvl )    
            
        elif type(keepx).__name__ == 'Operation':
            #yield str(keepx)   
            yield from parse_gen(keep[lvl],lvl )                
            
        elif type(keepx).__name__ == 'Parenthesis':
            #yield str(keepx)   
            ix_keep[lvl+1] = 0
            keep[lvl+1] = keepx.tokens
            #print(keep[lvl+1])
            ##print ('going to group : ' + str(lvl+1))
            yield from parse_gen(keep[lvl+1],lvl+1 )      
            
        else:
            print ('WARNING ????? : ' , type(keepx).__name__)
            yield from parse_gen(keep[lvl],lvl )   
        
    else:
        keepx = keep[lvl][0]
        keep[lvl] = keep[lvl][1:]
        ix_keep[lvl] = ix_keep[lvl] + 1
        
        
        #if   re.search(pat_FROM ,str(keepx)) is not None and keep[lvl][0].ttype <> 'Token.Operator' : 
        if   re.search(pat_FROM ,str(keepx)) is not None  :             
            # if the next token (i.e keep[lvl][0]) is an operator
            #  it means that it is a vairable like WS-FROM-STN-333 

            from_sw = 1
        elif re.search(pat_WHERE ,str(keepx)) is not None : 
            from_sw = 0
        elif re.search(pat_SELECT ,str(keepx)) is not None : 
            from_sw = 0
        elif re.search(pat_ON ,str(keepx)) is not None : 
            from_sw = 0
    
        yield from parse_gen(keep[lvl],lvl ) 
        


def create_view(df_parsex):
    global keep, full_keep, ix_keep, from_sw   

    
    l2 = []
    
    for index, row in df_parsex.iterrows():
        file = row[0]
        pgm = row[1]
    
        l1 = []
        ##print (index)
        for sql in row[2: ]:
            if sql != '':            
                #if start with declare get rid of it 
                
          
                if sql[0:7] == 'DECLARE':
                    pos_sel = sql.find('SELECT')
                    sql = sql[pos_sel:]
                
                pos_1 = sql.find('FOR UPDATE OF')
                if pos_1 > -1:
                    sql = sql[0:pos_1]
                    

                lx = re.split(pat_UNION,sql)
                
                if len(lx) > 1 :
                    print('debug split UNION : ', pgm)
                
                for sql in lx            :
                    
                    sql = re.sub(pat_ALL_str_alone, '', sql)                     
                    sql = re.sub(pat_strt_newline, '', sql) 

                    keep = [([]) for i in range(1000)]
                    full_keep = [([]) for i in range(1000)]
                    ix_keep = [(0) for i in range(1000)]
                    
                    parsed = sqlparse.parse(sql)[0]
                    
                    keep[0] =  parsed.tokens
                    full_keep[0] = keep[0]
                    ix_keep[0] = 0
                    from_sw = 0   
                    
                    stream = parse_gen(keep[0],0)
                    
                    for k in stream:
                        if len(l1) == 0 : 
                            l1 = [k]  
                        else :
                            l1.extend([k]) 
                        
    
        if len(l2) == 0:             
            l2 = [[file, pgm,sorted(list(set(l1)))  ]]    
        else :
            l2.extend([[file, pgm,sorted(list(set(l1)))  ]]  )  
            
    return l2

#------------------------------------------------------------------------



def sql_parse(df_out_mbr):
    
    #global  df_in, df_0_1, df_1_n, df_update, df_1_update,  l2 , df_select_out, l_file, l_mbr, l_view
    #global df_in, df_0_1, df_1_n, l2,df_1_update
    
    df_in = df_out_mbr
    df_in = df_in.fillna('')
    df_0_1= df_in.iloc[:,0:2]
    df_1_n = df_in.iloc[:,2:]
    df_1_n = df_1_n.applymap(lambda x: x.strip())
    
    
    #----------------------------------------------
    df_select = pd.DataFrame()
    df_1_select = df_1_n[df_1_n.applymap(lambda x: ("SELECT" in x  ) )].fillna('')
    df_2_select = pd.concat([df_0_1, df_1_select ], axis = 1)
    
    l2 = create_view(df_2_select)
    
    df_select['file'] = [ l2[i][0] for i in range(len(l2))  ] 
    df_select['pgm']  = [ l2[i][1] for i in range(len(l2))  ] 
    df_select['Select'] = ["\n".join(l2[i][2]) for i in range(len(l2))] 
    
    l_select_out = []
    for x1 in l2:
        for x2 in x1[2] : 
            l_select_out.append([x1[0],x1[1],x2])               
    df_select_out = pd.DataFrame(l_select_out, columns = ['Lv123','Name','View'])       

    if not os.path.isfile(out_file_s):
       df_select_out.to_csv(out_file_s,mode = 'w',header=True, index = False)
    else: # else it exists so append without writing the header
       df_select_out.to_csv(out_file_s,mode = 'a',header=False, index = False) 
    

    #----------------------------------------------
    df_update = pd.DataFrame()
    df_update_out = pd.DataFrame()
    df_1_update = df_1_n[df_1_n.applymap(lambda x: (x.find('UPDATE') == 0) )].fillna('')
    list_update = []
    l_file = []
    l_mbr = []
    l_view = []
    #l_update_out = []
    for index, row in df_1_update.iterrows():
        l1 = sorted(list(set([ re.sub(pat_newline, ' ', x).split()[1]  for x in row[:] if x != '' ] ))) 
        l2 = [ x if x.find('.') == -1 else x.split('.')[1]  for x in l1 ]        
        list_update.append("\n".join(l2))
        
        l_file.extend([df_0_1['file'].loc[index]] * len(l2))
        l_mbr.extend([df_0_1['mbr'].loc[index]] * len(l2))
        l_view.extend(l2)
            
    df_2_update = pd.DataFrame(list_update)
    df_2_update.columns = ['Update'] 
    df_update = pd.concat([df_0_1, df_2_update], axis = 1)
    
    df_update_out = pd.DataFrame(list(zip(l_file, l_mbr, l_view)),columns=['file','mbr', 'view'])    
    
    if not os.path.isfile(out_file_u):
       df_update_out.to_csv(out_file_u,mode = 'w',header=True, index = False)
    else: # else it exists so append without writing the header
       df_update_out.to_csv(out_file_u,mode = 'a',header=False, index = False) 
    
  
    
    #----------------------------------------------
    df_insert = pd.DataFrame()
    df_insert_out = pd.DataFrame()
    df_1_insert = df_1_n[df_1_n.applymap(lambda x: (x.find('INSERT') == 0) )].fillna('')
    list_insert = []
    l_file = []
    l_mbr = []
    l_view = []
    for index, row in df_1_insert.iterrows():
        l1 = sorted(list(set([ re.sub(pat_newline, ' ', x).split()[2]  for x in row[:] if x != '' ] ))) 
        l2 = [ x if x.find('.') == -1 else x.split('.')[1]  for x in l1 ]               
        list_insert.append("\n".join(l2))
        
        l_file.extend([df_0_1['file'].loc[index]] * len(l2))
        l_mbr.extend([df_0_1['mbr'].loc[index]] * len(l2))
        l_view.extend(l2)
            
    df_2_insert = pd.DataFrame(list_insert)
    df_2_insert.columns = ['Insert'] 
    df_insert = pd.concat([df_0_1, df_2_insert], axis = 1)
    
    df_insert_out = pd.DataFrame(list(zip(l_file, l_mbr, l_view)),columns=['file','mbr', 'view'])    
    
    if not os.path.isfile(out_file_i):
       df_insert_out.to_csv(out_file_i,mode = 'w',header=True, index = False)
    else: # else it exists so append without writing the header
       df_insert_out.to_csv(out_file_i,mode = 'a',header=False, index = False) 
    


  #----------------------------------------------
    df_delete = pd.DataFrame()
    df_delete_out = pd.DataFrame()
    df_1_delete = df_1_n[df_1_n.applymap(lambda x: (x.find('DELETE') == 0) )].fillna('')
    list_delete = []
    l_file = []
    l_mbr = []
    l_view = []
    for index, row in df_1_delete.iterrows():
        l1 = sorted(list(set([ re.sub(pat_newline, ' ', x).split()[2]  for x in row[:] if x != '' ] ))) 
        l2 = [ x if x.find('.') == -1 else x.split('.')[1]  for x in l1 ]                       
        list_delete.append("\n".join(l2))
        
        l_file.extend([df_0_1['file'].loc[index]] * len(l2))
        l_mbr.extend([df_0_1['mbr'].loc[index]] * len(l2))
        l_view.extend(l2)
            
    df_2_delete = pd.DataFrame(list_delete)
    df_2_delete.columns = ['Delete'] 
    df_delete = pd.concat([df_0_1, df_2_delete], axis = 1)
    
    df_delete_out = pd.DataFrame(list(zip(l_file, l_mbr, l_view)),columns=['file','mbr', 'view'])    
    
    if not os.path.isfile(out_file_d):
       df_delete_out.to_csv(out_file_d,mode = 'w',header=True, index = False)
    else: # else it exists so append without writing the header
       df_delete_out.to_csv(out_file_d,mode = 'a',header=False, index = False) 
    



    #---------------------------------------------- 
    df_investigate = pd.DataFrame()
    df_1_investigate = df_1_n[df_1_n.applymap(lambda x: ("???" in x  ))].fillna('')
    list_investigate = []
    l_file = []
    l_mbr = []
    l_view = []
    for index, row in df_1_investigate.iterrows():
        l1 = sorted(list(set([ re.sub(pat_newline, ' ', x)  for x in row[:] if x != '' ] )))
        l2 = [ x if x.find('.') == -1 else x.split('.')[1]  for x in l1 ]               
        list_investigate.append("\n".join(l2))

        l_file.extend([df_0_1['file'].loc[index]] * len(l2))
        l_mbr.extend([df_0_1['mbr'].loc[index]] * len(l2))
        l_view.extend(l2)


    df_2_investigate = pd.DataFrame(list_investigate)
    df_2_investigate.columns = ['Investigate'] 
    df_investigate = pd.concat([df_0_1, df_2_investigate], axis = 1)
    
    df_investigate_out = pd.DataFrame(list(zip(l_file, l_mbr, l_view)),columns=['file','mbr', 'view'])    
    
    if not os.path.isfile(out_file_x):
       df_investigate_out.to_csv(out_file_x,mode = 'w',header=True, index = False)
    else: # else it exists so append without writing the header
       df_investigate_out.to_csv(out_file_x,mode = 'a',header=False, index = False) 
    




    #----------------------------------------------        
    df_crud = pd.DataFrame()
    df_crud = pd.concat([df_select, df_update.iloc[:,2:], df_insert.iloc[:,2:], df_delete.iloc[:,2:], df_investigate.iloc[:,2:]], axis = 1).fillna('')
    if not os.path.isfile(out_file):
       df_crud.to_csv(out_file,mode = 'w',header=True, index = False)
    else: # else it exists so append without writing the header
       df_crud.to_csv(out_file,mode = 'a',header=False, index = False) 


    return ()    


def get_seed(in_file):
    
  
    excel.DisplayAlerts = True  
    wb1 = excel.Workbooks.Open(in_file)
    excel.Visible = True
    excel.ActiveSheet.Columns.AutoFit()  
    wb1.Close()
    
    input("Save Excel and quit excel before pressing enter? ")     


    labels = ['selection','Lv123','Name','VV.MM','Created','Changedate','Changetime','Sze','Init','Mod','Id']

    df_seed  = pd.read_csv(in_file , names=labels , skiprows = 1)
    df_seed  = df_seed[['selection','Lv123','Name']]    
    df_seed.fillna('', inplace=True)
    

    # \w Any word character (letter, number, underscore ) 
    df_seed  = df_seed[df_seed['selection'].str.contains(re.compile('\w'))] 
        
    
    if len(df_seed) == 0 :
        print( "nothing selected in input : " + in_file)
        sys.exit(0)    
    
    return df_seed


def write_final_in_xlsx():
    
    pat_forward_slash = re.compile(r"(\/)")     
    
    buf = re.sub(pat_forward_slash , r"\\", out_file)    
    out_file_xls = ".".join(buf.split(".")[0:-1]) + ".xlsx"    
      
    if os.path.isfile(out_file_xls):
        os.remove(out_file_xls)	     

        
    excel.Visible = False     
    
    wb1 = excel.Workbooks.Open(out_file)    
    excel.ActiveSheet.Cells.ColumnWidth = 35
    excel.ActiveSheet.Rows.AutoFit() 
    excel.ActiveSheet.Name = "CRUD"
    
    wb_s = excel.Workbooks.Open(out_file_s)    
    excel.ActiveSheet.Cells.ColumnWidth = 35
    excel.ActiveSheet.Rows.AutoFit()   
    excel.ActiveSheet.Name = "SELECT"        
    wb_s.Worksheets("SELECT").Move(After=wb1.Worksheets("CRUD"))
    
    wb_u = excel.Workbooks.Open(out_file_u)    
    excel.ActiveSheet.Cells.ColumnWidth = 35
    excel.ActiveSheet.Rows.AutoFit()   
    excel.ActiveSheet.Name = "UPDATE"        
    wb_u.Worksheets("UPDATE").Move(After=wb1.Worksheets("SELECT"))
        
    wb_i = excel.Workbooks.Open(out_file_i)    
    excel.ActiveSheet.Cells.ColumnWidth = 35
    excel.ActiveSheet.Rows.AutoFit()   
    excel.ActiveSheet.Name = "INSERT"        
    wb_i.Worksheets("INSERT").Move(After=wb1.Worksheets("UPDATE"))
    
    wb_d = excel.Workbooks.Open(out_file_d)    
    excel.ActiveSheet.Cells.ColumnWidth = 35
    excel.ActiveSheet.Rows.AutoFit()   
    excel.ActiveSheet.Name = "DELETE"        
    wb_d.Worksheets("DELETE" ).Move(After=wb1.Worksheets("INSERT"))   
    
    wb_x = excel.Workbooks.Open(out_file_x)    
    excel.ActiveSheet.Cells.ColumnWidth = 35
    excel.ActiveSheet.Rows.AutoFit()   
    excel.ActiveSheet.Name = "INVESTIGATE"        
    wb_x.Worksheets("INVESTIGATE" ).Move(After=wb1.Worksheets("DELETE"))      

    excel.DisplayAlerts = False   
    wb1.SaveAs(Filename=out_file_xls , FileFormat="61") 
    excel.DisplayAlerts = True       
    excel.Visible = True             
    wb1.Close()

    if os.path.exists(out_file_s): os.remove(out_file_s)	
    if os.path.exists(out_file_u): os.remove(out_file_u)	
    if os.path.exists(out_file_i): os.remove(out_file_i)	
    if os.path.exists(out_file_d): os.remove(out_file_d)	      
    if os.path.exists(out_file_x): os.remove(out_file_x)	    
    
    

def main_process():    

    df_seed = get_seed(in_file)    
    
    if os.path.exists(out_file): os.remove(out_file)	    
    if os.path.exists(out_file_s): os.remove(out_file_s)	
    if os.path.exists(out_file_u): os.remove(out_file_u)	
    if os.path.exists(out_file_i): os.remove(out_file_i)	
    if os.path.exists(out_file_d): os.remove(out_file_d)	      
    if os.path.exists(out_file_x): os.remove(out_file_x)	

    try:
        sess = ftplib.FTP('imftpb',username,password)
    except ftplib.Error as ex:
        err1 = ex.args[1]
        print (err1)
        sys.exit()    
    

    tot_lst_1 = []          
    tot_lst_2 = []  
    tot_lst_3 = []
    lv123_prev = ''
    buf_write_cnt_limit = 200
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
                
                
        hit_list = call_cobol_sql(lv123,mbr,sess)   
 
        
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
         
            sql_parse(df_out_mbr)
                       
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
        
        sql_parse(df_out_mbr)
          
    sess.quit
 
    write_final_in_xlsx()



    
    
 

def main_in(argv):
    global in_file, out_file, out_file_s, out_file_i, out_file_u, out_file_d, out_file_x, username, password    
    
    wrk_dir = ''
    in_file_1 = ''
    out_file_1 = ''
    username = ''
    password = ''
    try:
        opts, args = getopt.getopt(argv,"hw:i:o:u:p:",["help","wrkd=","inf=","outf=","usnam=","passw="])
    except getopt.GetoptError:
        print ('CRUD.py -w <workingdir> -i <infilename> -o <outfilename> -u <username) -p <password>')
        sys.exit(2)
        
     
    for opt, arg in opts:
        if opt == '-h':
            print ('CRUD.py -w <workingdir> -i <infilename> -o <outfilename> -u <username) -p <password>')
            sys.exit()
        elif opt in ("-w", "--wrkd"):
            wrk_dir = arg
        elif opt in ("-i", "--inf"):
            in_file_1 = arg                     
        elif opt in ("-o", "--outf"):
            out_file_1 = arg            
        elif opt in ("-u", "--usnam"):
            username = arg
        elif opt in ("-p", "--passw"):
            password = arg         


    in_file = wrk_dir + "\\" + in_file_1 + ".CSV"   
    out_file = wrk_dir + "\\" + out_file_1 + ".CSV"  
    out_file_s = wrk_dir + "\\" + out_file_1 + "_S.CSV"  
    out_file_i = wrk_dir + "\\" + out_file_1 + "_I.CSV"  
    out_file_u = wrk_dir + "\\" + out_file_1 + "_U.CSV"  
    out_file_d = wrk_dir + "\\" + out_file_1 + "_D.CSV"  
    out_file_x = wrk_dir + "\\" + out_file_1 + "_X.CSV"  
    

    #for testing put the following in  RUN  ---  Configuration per file  --- Command line option 
    #-w C:\Users\XT21586\Documents\document\_DOSSET\_promoted_V2\result -i COB_MBR_SEED_CHANGEI.CNDWPROD.COBSRCE -o CRUD_CHANGEI.CNDWPROD.COBSRCE -u CNDWLMM -p lcjcmhf3
 
    #wrk_dir = "C:\\Users\\XT21586\\Documents\\document\\_DOSSET\\_promoted_V2\\result"
    #username = "cndwlmm"
    #password = "lcjcmhf3"    
    #in_file = wrk_dir + "COB_MBR_SEED_CHANGEI.CNDWPROD.COBSRCE.CSV"
    #out_file = wrk_dir + "CRUD_CHANGEI.CNDWPROD.COBSRCE.CSV"    


if __name__ == "__main__":
    
    main_in(sys.argv[1:])



    print (in_file)    
    print (out_file)
    print (username)
    
  
    main_process()   

    excel.Quit()
    del excel
