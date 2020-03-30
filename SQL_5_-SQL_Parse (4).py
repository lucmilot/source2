# -*- coding: utf-8 -*-
"""
Created on Thu Aug  9 11:36:01 2018

@author: Luc Milot








"""

import os, sys

import win32com.client as win32

import tkinter as tk
from tkinter.filedialog import askopenfilename


import numpy as np

import pandas as pd

import re

import sqlparse

from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML

import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory

import tkinter.ttk as ttk

import tkinter.messagebox as msg


import sys
sys.setrecursionlimit(10000) # 10000 is an example, try with different values

'''
pat_SIUD = re.compile(".*(?=SELECT|INSERT|DELETE|UPDATE).*",flags = re.DOTALL)
pat_strt_double_quote = re.compile(r"^\"",flags = re.DOTALL)
pat_end_double_quote = re.compile("(\"$)",flags = re.DOTALL)
pat_strt_newline = re.compile("(^\r\n)",flags = re.DOTALL)
pat_strt_blank_SELECT = re.compile("(?:^\s)(\s*)(?:SELECT)",flags = re.DOTALL) 
'''
pat_strt_newline = re.compile("\n",flags = re.DOTALL)
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

#------------------------------------------------------------------------
def create_view(df_parsex):
    global keep, full_keep, ix_keep, from_sw   
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
            keepy = keep[lvl]
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


    l2 = []
    
    for index, row in df_parsex.iterrows():
        file = row[0]
        pgm = row[1]
        print(pgm)
        l1 = []
        ##print (index)
        for sql in row[2: ]:
            if sql != '':
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
        
        
rt = tk.Tk()
rt.withdraw()
msg.showinfo("Information","You need to select the proper SQL_FULL_... ")
rt.destroy()
#root.quit() 


rt = tk.Tk() 
rt.withdraw()
in_file = askopenfilename(parent=rt)
rt.destroy()

out_dir = r"/".join(in_file.split(r"/")[0:-1])
out_file = out_dir + "/SQL_VIEW_" + in_file.split(r"_")[-1:][0]
out_file_select = out_dir + "/SQL_VIEW_SELECT_" + in_file.split(r"_")[-1:][0]
out_file_update = out_dir + "/SQL_VIEW_UPDATE_" + in_file.split(r"_")[-1:][0]
out_file_insert = out_dir + "/SQL_VIEW_INSERT_" + in_file.split(r"_")[-1:][0]
out_file_delete = out_dir + "/SQL_VIEW_DELETE_" + in_file.split(r"_")[-1:][0]


if os.path.exists(out_file_select):
    os.remove(out_file_select)	            
if os.path.exists(out_file_update):
    os.remove(out_file_update)	    
if os.path.exists(out_file_insert):
    os.remove(out_file_insert)	    
if os.path.exists(out_file_delete):
    os.remove(out_file_delete)	    



df_in = pd.read_csv(in_file)
df_in = df_in.fillna('')
df_0_1= df_in.iloc[:,0:2]
df_1_n = df_in.iloc[:,2:]
df_1_n = df_1_n.applymap(lambda x: x.strip())



df_select = pd.DataFrame()
df_1_select = df_1_n[df_1_n.applymap(lambda x: re.search(pat_select_overall,x) is not None  )].fillna('')
df_2_select = pd.concat([df_0_1, df_1_select ], axis = 1)
l2 = create_view(df_2_select)
df_select['file'] = [ l2[i][0] for i in range(len(l2))  ] 
df_select['pgm']  = [ l2[i][1] for i in range(len(l2))  ] 
df_select['Select'] = ["\n".join(l2[i][2]) for i in range(len(l2))] 
df_select.to_csv(out_file_select,mode = 'w',header=True, index = False)

df_update = pd.DataFrame()
df_1_update = df_1_n[df_1_n.applymap(lambda x: (re.search(pat_UPDATE,x)  is not None) )].fillna('')
list_update = []
for index, row in df_1_update.iterrows():
    list_update.append(   "\n".join(  sorted(list(set([ re.sub(pat_strt_newline, ' ', x).split()[1]  for x in row[:] if x != '' ] ))) ) )
df_2_update = pd.DataFrame(list_update)
df_2_update.columns = ['Update'] 
df_update = pd.concat([df_0_1, df_2_update], axis = 1)
df_update.to_csv(out_file_update,mode = 'w',header=True, index = False)

df_insert = pd.DataFrame()
df_1_insert = df_1_n[df_1_n.applymap(lambda x: (re.search(pat_INSERT,x)  is not None) )].fillna('')
list_insert = []
for index, row in df_1_insert.iterrows():
    list_insert.append(   "\n".join(  sorted(list(set([ re.sub(pat_strt_newline, ' ', x).split()[2]  for x in row[:] if x != '' ] ))) ) )
df_2_insert = pd.DataFrame(list_insert)
df_2_insert.columns = ['Insert'] 
df_insert = pd.concat([df_0_1, df_2_insert], axis = 1)
df_insert.to_csv(out_file_insert,mode = 'w',header=True, index = False)

df_delete = pd.DataFrame()
df_1_delete = df_1_n[df_1_n.applymap(lambda x: (re.search(pat_DELETE,x)  is not None) )].fillna('')
list_delete = []
for index, row in df_1_delete.iterrows():
    list_delete.append(   "\n".join(  sorted(list(set([ re.sub(pat_strt_newline, ' ', x).split()[2]  for x in row[:] if x != '' ] ))) ) )
df_2_delete = pd.DataFrame(list_delete)
df_2_delete.columns = ['Delete'] 
df_delete = pd.concat([df_0_1, df_2_delete], axis = 1)
df_delete.to_csv(out_file_delete,mode = 'w',header=True, index = False)

df_crud = pd.DataFrame()
df_crud = pd.concat([df_select, df_update.iloc[:,2:], df_insert.iloc[:,2:], df_delete.iloc[:,2:]], axis = 1).fillna('')

# CREATE pivot
# 


