#!usr/env/bin python
#coding:utf-8

import sys
import os

def get_files(dir,files):
    for f in os.listdir(dir):
        full_name=dir+f
        if os.path.isfile(full_name):
            files.append(full_name)
        elif os.path.isdir(full_name):
            get_files(full_name+"/",files)

def merge(files):
    ngramdic={}
    i=0
    for file in files:
        i+=1
        if i%200==0:print(str(i)+"/"+str(len(files)))
        with open(file,"r")as f:
            for line in f.readlines():
                ngram,count=line.split("\t")[0]+"\t"+line.split("\t")[1],line.split("\t")[2]
                if ngram in ngramdic:
                    ngramdic[ngram]+=1
                else:
                    ngramdic[ngram]=1
    return ngramdic

if __name__=="__main__":
    files=[]
    n=4
    get_files("./data/ngrams/"+str(n)+"/",files)

    ngramdic=merge(files)

    with open("./data/ngrams/merged/"+str(n)+"-gram.txt","w")as f:
        for ngram in ngramdic.items():
            if ngram[1]>=10:
                f.write(ngram[0]+"\t"+str(ngram[1])+"\n")
