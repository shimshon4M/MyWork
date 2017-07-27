#!usr/bin/env/python
#coding:utf-8

import MeCab
import types
import sys
import os

def get_ngram(target_text,n):
    #m=MeCab.Tagger("-Ochasen -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd/")
    m=MeCab.Tagger("-Ochasen")
    m.parse("")
    ret_ngram_list=[]
    if(isinstance(target_text,str)):#単文で受け取った場合
        morphemes=m.parse(target_text).split("\n")
        for i in range(len(morphemes)-n-1):
            tmp_ngram=[]
            for j in range(n):
                tmp_ngram.append(morphemes[i+j].split("\t")[0])
            ret_ngram_list.append("".join(tmp_ngram))
        
    return ret_ngram_list

#数も考慮
def get_ngram_count(target_text,n):
    #m=MeCab.Tagger("-Ochasen -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd/")
    m=MeCab.Tagger("-Ochasen")
    m.parse("")
    ret_ngram_dic={}
    if(isinstance(target_text,str)):#単文で受け取った場合
        morphemes=m.parse(target_text).split("\n")
        for i in range(len(morphemes)-n-1):
            tmp_ngram=[]
            tmp_hinshi=[]
            for j in range(n):
                tmp_ngram.append(morphemes[i+j].split("\t")[0])
                tmp_hinshi.append(morphemes[i+j].split("\t")[3])
            ngram_str="".join(tmp_ngram)
            hinshi_str="/".join(tmp_hinshi)
            if ngram_str+"\t"+hinshi_str in ret_ngram_dic:
                ret_ngram_dic[ngram_str+"\t"+hinshi_str]+=1
            else:
                ret_ngram_dic[ngram_str+"\t"+hinshi_str]=1
        
    return ret_ngram_dic

def get_files(dir,files):
    for f in os.listdir(dir):
        full_name=dir+f
        if os.path.isfile(full_name):
            files.append(full_name)
        elif os.path.isdir(full_name):
            get_files(full_name+"/",files)

"""
param1:target file name
param2:"n" of "n-gram"
"""
if __name__=="__main__":
    """
    args=sys.argv
    #ファイル名を引数に入れる場合
    with open(args[1],"r")as f:
        ngrams=get_ngram(f.read(),int(args[2]))
    #直接テキストを引数に入れる場合
    #ngrams=get_ngram(args[1],int(args[2]))

    #コンソールに出力
    #for word in ngrams:
    #    print(word)
    """

    files=[]
    n=4
    get_files("./data/formated_paper_text/",files)
    i=0
    for file in files:
        i+=1
        if i%200==0:print(str(i)+"/"+str(len(files)))
        with open(file,"r")as f:
            ngramdic=get_ngram_count(f.read(),n)
        
        tmp=file.split("/")[-1]
        with open("./data/ngrams/"+str(n)+"/"+str(n)+"gram_"+tmp,"w")as f:
            for word in ngramdic.items():
                f.write(word[0]+"\t"+str(word[1])+"\n")
                
        
