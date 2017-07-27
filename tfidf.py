#!usr/env/bin python
#coding:utf-8

import sys
import math
from utils import get_files

if __name__=="__main__":
    args=sys.argv
    files=[]
    get_files("./data/ngrams/2/",files)
    N=len(files)

    with open(args[1],"r")as f:
        lines=f.readlines()
        words={}
        for line in lines:
            word=line.split("\t")[0]+"\t"+line.split("\t")[1]
            tf=int(line.split("\t")[2])/len(lines)
            #print(word,tf)
            df=0
            now_fnum=0
            for file in files:
                now_fnum+=1
                if now_fnum%1000==0:
                    print("%d/%d"%(now_fnum,N))
                with open(file,"r")as ff:
                    if word in ff.read():
                        df+=1
                        continue
            idf=math.log(N/df)+1
            words[word]=tf*idf
            print(word,words.get(word))

    for word,tfidf in sorted(words.items(), key=lambda x:x[1]):
        print(word,tfidf)
