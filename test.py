#!usr/env/bin python
#coding:utf-8

import os
import sys
import re

rm_pat=r'[\)\(\{\}）（,\.，、。．「」\[\]\\\?"]'

with open("./data/ngrams/merged/2-gram.txt","r")as f:
    for line in f.readlines():
        tmp=line.split("\t")
        word=tmp[0]
        hinshi=tmp[1].split("/")
        count=tmp[2]

        if re.search(rm_pat,word):
            continue
        if "cid" in word:
            continue
        if re.search("助詞",hinshi[-1]) or re.search("助詞",hinshi[0]):
            continue
        if re.search("助動詞",hinshi[-1]) or re.search("助動詞",hinshi[0]):
            continue
        if re.search("記号",hinshi[-1]) or re.search("記号",hinshi[0]) or re.search("記号",hinshi[1]):
            continue
        if re.search("形容詞",hinshi[-1]) or re.search("形容動詞",hinshi[-1]):
            continue
        if re.search("動詞",hinshi[-1]) or re.search("動詞",hinshi[0]):
            continue
        #if hinshi[1].startswith("助詞") and not hinshi[1].endswith("連体化"):
         #   continue
        if int(count)>300:
            continue
        if word.isdigit():
            continue

        print(word+"  :  "+"/".join(hinshi)+"  :  "+str(count),end="")
