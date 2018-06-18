#!usr/env/bin python
#coding:utf-8

import os

def get_files(dir):#,files):
    files=[]
    for f in os.listdir(dir):
        full_name=dir+f
        if os.path.isfile(full_name):
            files.append(full_name)
        #elif os.path.isdir(full_name):
        #    get_files(full_name+"/",files)
    return files
