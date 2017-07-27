#!usr/bin/env python
#coding:utf-8

import sys
import os
import MeCab

m=MeCab.Tagger("-Ochasen")
m=parse()

def format(filename):
    isTitle=False

    lines=[]
    with open(filename,"r")as f:
        lines= f.readlines():
        for line in lines:
            if line=="" or line=="\n":
                continue#空行は飛ばす
            

    tmp=filename.split("/")
    outfilename="./data/formated_paper_text/"+tmp[3]+"_"+tmp[5]
    with open(outfilename,"w")as f:
        f.write(article)

def get_files(dir,files):
    for f in os.listdir(dir):
        full_name=dir+f
        if os.path.isfile(full_name):
            files.append(full_name)
        elif os.path.isdir(full_name):
            get_files(full_name+"/",files)

"""
param1:-f or -d
param2:file(if -f) or directory(if -d)
"""
if __name__=="__main__":
    args=sys.argv
    
    if args[1]=="-f":
        format(args[2])
    elif args[1]=="-d":
        files=[]
        get_files(args[2],files)
        for file in files:
            print(file)
            format(file)
